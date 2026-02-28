import requests
from threading import Thread, Lock
from time import sleep
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError, MaxRetryError

try:
    from config import (
        STATION_CODE,
        RTT_API_USERNAME,
        RTT_API_PASSWORD,
        MAX_DEPARTURES,
        MAX_CALLING_POINT_LOOKUPS,
    )
except (ModuleNotFoundError, NameError, ImportError):
    STATION_CODE = "PAD"
    RTT_API_USERNAME = ""
    RTT_API_PASSWORD = ""
    MAX_DEPARTURES = 10
    MAX_CALLING_POINT_LOOKUPS = 6

RETRIES = 3
RATE_LIMIT_DELAY = 0.5
BASE_URL = "https://api.rtt.io/api/v1/json"


class Departures:
    def __init__(self):
        self._lock = Lock()
        self._data = []
        self._station_name = STATION_CODE
        self._new_data = False
        self._processing = False

    def grab_data(self):
        Thread(target=self._grab_data, daemon=True).start()

    def _grab_data(self):
        with self._lock:
            self._new_data = False
            self._processing = True

        data = []

        try:
            url = f"{BASE_URL}/search/{STATION_CODE}"
            response = requests.get(
                url,
                auth=(RTT_API_USERNAME, RTT_API_PASSWORD),
                timeout=15,
            )
            response.raise_for_status()
            result = response.json()

            station_name = result.get("location", {}).get("name", STATION_CODE)
            services = result.get("services") or []

            for service in services:
                if service.get("serviceType") != "train":
                    continue

                loc = service.get("locationDetail", {})

                # Get destination
                destinations = loc.get("destination") or []
                if not destinations:
                    continue
                destination = destinations[0].get("description", "Unknown")

                # Get times
                booked_dep = loc.get("gbttBookedDeparture", "")
                realtime_dep = loc.get("realtimeDeparture", "")

                scheduled = self._format_time(booked_dep)
                expected = self._format_time(realtime_dep)

                # Get platform
                platform = loc.get("platform", "")

                # Determine status
                display_as = loc.get("displayAs", "")
                cancel_code = loc.get("cancelReasonCode")
                cancelled = cancel_code is not None or display_as == "CANCELLED_CALL"

                if cancelled:
                    status = "Cancelled"
                elif scheduled == expected or not expected:
                    status = "On time"
                else:
                    status = f"Exp {expected}"

                # Get service UID and run date for calling points lookup
                service_uid = service.get("serviceUid", "")
                run_date = service.get("runDate", "")

                # Get operator
                operator = service.get("atocName", "")

                data.append({
                    "destination": destination,
                    "scheduled": scheduled,
                    "expected": expected,
                    "platform": platform,
                    "status": status,
                    "cancelled": cancelled,
                    "operator": operator,
                    "service_uid": service_uid,
                    "run_date": run_date,
                    "calling_points": [],
                })

                if len(data) >= MAX_DEPARTURES:
                    break

            # Fetch calling points for top services
            for dep in data[:MAX_CALLING_POINT_LOOKUPS]:
                if dep["service_uid"] and dep["run_date"]:
                    sleep(RATE_LIMIT_DELAY)
                    self._fetch_calling_points(dep)

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

    def _fetch_calling_points(self, departure):
        try:
            date_str = departure["run_date"].replace("-", "/")
            uid = departure["service_uid"]
            url = f"{BASE_URL}/service/{uid}/{date_str}"
            response = requests.get(
                url,
                auth=(RTT_API_USERNAME, RTT_API_PASSWORD),
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()

            locations = result.get("locations") or []
            found_origin = False
            calling_points = []

            for loc in locations:
                crs = loc.get("crs", "")
                tiploc = loc.get("tiploc", "")

                if crs == STATION_CODE or tiploc == STATION_CODE:
                    found_origin = True
                    continue

                if found_origin and loc.get("isCall", False):
                    calling_points.append(loc.get("description", "Unknown"))

            departure["calling_points"] = calling_points

        except Exception as e:
            print(f"Error fetching calling points for {departure.get('service_uid')}: {e}")

    @staticmethod
    def _format_time(time_str):
        if not time_str or len(time_str) < 4:
            return ""
        return f"{time_str[:2]}:{time_str[2:4]}"

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
