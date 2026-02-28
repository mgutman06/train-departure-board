import importlib.util
import os
import requests
from threading import Thread, Lock
from time import sleep
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError

_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py"
)

_DEFAULTS = {
    "STATION_CODE": "PAD",
    "DARWIN_API_TOKEN": "",
    "HUXLEY_URL": "https://huxley2.azurewebsites.net",
    "MAX_DEPARTURES": 10,
    "REFRESH_INTERVAL": 60,
}


def load_config():
    """Load config fresh from disk so changes apply without a restart."""
    try:
        spec = importlib.util.spec_from_file_location("config", _CONFIG_FILE)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return {key: getattr(config, key, default) for key, default in _DEFAULTS.items()}
    except Exception:
        return dict(_DEFAULTS)


class Departures:
    def __init__(self):
        self._lock = Lock()
        self._data = []
        cfg = load_config()
        self._station_name = cfg["STATION_CODE"]
        self._new_data = False
        self._processing = False

    def grab_data(self):
        Thread(target=self._grab_data, daemon=True).start()

    def _grab_data(self):
        with self._lock:
            self._new_data = False
            self._processing = True

        cfg = load_config()
        data = []

        try:
            url = (
                f"{cfg['HUXLEY_URL'].rstrip('/')}/departures/{cfg['STATION_CODE']}"
                f"/{cfg['MAX_DEPARTURES']}"
                f"?accessToken={cfg['DARWIN_API_TOKEN']}&expand=true"
            )
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            result = response.json()

            station_name = result.get("locationName", cfg["STATION_CODE"])
            services = result.get("trainServices") or []

            for service in services:
                # Get destination
                destinations = service.get("destination") or []
                if not destinations:
                    continue
                destination = destinations[0].get("locationName", "Unknown")

                # Get times — std/etd are already formatted as "HH:MM"
                scheduled = service.get("std", "")
                etd = service.get("etd", "")

                # Determine status from etd
                # etd can be: "On time", "Delayed", "Cancelled", or a time like "09:30"
                cancelled = service.get("isCancelled", False) or etd == "Cancelled"

                if cancelled:
                    status = "Cancelled"
                elif etd == "On time":
                    status = "On time"
                elif etd == "Delayed":
                    status = "Delayed"
                else:
                    # etd is an actual time like "09:30"
                    status = f"Exp {etd}"

                # Get platform
                platform = service.get("platform", "")

                # Get operator
                operator = service.get("operator", "")

                # Get calling points from expanded response
                calling_points = []
                subsequent = service.get("subsequentCallingPoints")
                if subsequent:
                    # subsequentCallingPoints is a list of lists
                    for point_list in subsequent:
                        calling_point_items = point_list.get("callingPoint") or []
                        for point in calling_point_items:
                            name = point.get("locationName", "")
                            if name:
                                calling_points.append(name)

                data.append({
                    "destination": destination,
                    "scheduled": scheduled,
                    "expected": etd if etd not in ("On time", "Delayed", "Cancelled") else "",
                    "platform": platform,
                    "status": status,
                    "cancelled": cancelled,
                    "operator": operator,
                    "calling_points": calling_points,
                })

            with self._lock:
                self._new_data = True
                self._processing = False
                self._data = data
                self._station_name = station_name

        except (ConnectionError, NewConnectionError, MaxRetryError, Exception) as e:
            print(f"Error fetching train data: {e}")
            with self._lock:
                self._new_data = False
                self._processing = False

    @property
    def new_data(self):
        with self._lock:
            return self._new_data

    @property
    def processing(self):
        with self._lock:
            return self._processing

    @property
    def data(self):
        with self._lock:
            self._new_data = False
            return self._data

    @property
    def station_name(self):
        with self._lock:
            return self._station_name

    @property
    def data_is_empty(self):
        return len(self._data) == 0


if __name__ == "__main__":
    d = Departures()
    d.grab_data()
    while not d.new_data:
        print("Fetching departures...")
        sleep(1)

    for dep in d.data:
        print(f"{dep['scheduled']}  {dep['destination']:30s}  {dep['status']:12s}  Plt {dep['platform']}")
        if dep["calling_points"]:
            print(f"  Calling at: {', '.join(dep['calling_points'])}")
