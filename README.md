# Trainline - RGB Matrix Train Departure Display

A Raspberry Pi-powered LED matrix display that shows live UK train departure information, styled like the dot matrix displays found at railway stations across the United Kingdom.

Uses the [National Rail Darwin API](https://www.nationalrail.co.uk/developers/darwin-data-feeds/) via [Huxley2](https://github.com/jpsingleton/Huxley2) for live departure data displayed on a 64x32 RGB LED matrix panel.

Based on the original [FlightTracker](https://github.com/ColinWaddell/FlightTracker) project by Colin Waddell.

## What it shows

**When trains are departing:**
- Destination station name (top, amber)
- Departure time, platform number, and status (middle)
- Scrolling calling points for each service (bottom)
- Cycles through upcoming departures automatically

**When no departures:**
- Station name and clock
- Animated train

## Hardware Required

- Raspberry Pi (Pi Zero 2 W, Pi 3, Pi 4, or Pi 5)
- [Adafruit RGB Matrix Bonnet](https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi/overview)
- 64x32 RGB LED Matrix Panel
- 5V power supply (for the LED matrix)

## Setup

### 1. System preparation

```bash
sudo apt-get update
sudo apt-get dist-upgrade
```

### 2. Install the RGB Screen

1. Assemble the RGB matrix, Pi, and Bonnet as described in [this Adafruit guide](https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi/overview).
2. It is recommended that the [solder bridge is added to the HAT](https://learn.adafruit.com/assets/57727) for PWM via the soundcard.
3. Install the `rgb-matrix` library:

```bash
cd /home/pi
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh > /tmp/rgb-matrix.sh
sudo bash /tmp/rgb-matrix.sh
```

4. Test the display:

```bash
cd /home/pi/rpi-rgb-led-matrix/examples-api-use
sudo ./demo --led-rows=32 --led-cols=64 -D0
```

### 3. Install this software

```bash
cd /home/pi/
git clone https://github.com/mgutman06/FlightTracker trainline
cd /home/pi/trainline
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Install the RGB matrix Python bindings into the virtual environment:

```bash
cd /home/pi/rpi-rgb-led-matrix/bindings/python
pip install .
```

### 4. Get API credentials

1. Register for a free Darwin API token at [realtime.nationalrail.co.uk/OpenLDBWSRegistration](https://realtime.nationalrail.co.uk/OpenLDBWSRegistration/)
2. Note your API token (a GUID string)

### 5. Configure

```bash
cd /home/pi/trainline
nano config.py
```

Example configuration:

```python
# Station to display departures for (CRS code)
STATION_CODE = "PAD"

# Darwin API token (National Rail Live Departure Boards)
DARWIN_API_TOKEN = "your_darwin_token"

# Huxley2 API base URL (JSON proxy for Darwin)
HUXLEY_URL = "https://huxley2.azurewebsites.net"

# Maximum number of departures to display
MAX_DEPARTURES = 10

# Display settings
BRIGHTNESS = 50
GPIO_SLOWDOWN = 2
HAT_PWM_ENABLED = True

# Data refresh interval in seconds
REFRESH_INTERVAL = 60
```

### Configuration details

| Variable                   | Description |
|----------------------------|-------------|
| `STATION_CODE`             | The CRS code of the station to show departures for. Find your station code at [National Rail](https://www.nationalrail.co.uk/). |
| `DARWIN_API_TOKEN`         | Your Darwin API token. Register free at [realtime.nationalrail.co.uk](https://realtime.nationalrail.co.uk/OpenLDBWSRegistration/). |
| `HUXLEY_URL`               | Base URL of the Huxley2 JSON proxy. Default public instance works out of the box. |
| `MAX_DEPARTURES`           | Maximum number of departures to fetch and cycle through. |
| `BRIGHTNESS`               | Display brightness, range 0-100. |
| `GPIO_SLOWDOWN`            | Range 0-4. Higher values reduce flickering on faster Pi models. |
| `HAT_PWM_ENABLED`          | Set `True` if you've added the solder bridge for soundcard PWM. |
| `REFRESH_INTERVAL`         | How often (seconds) to fetch fresh departure data. |

### Common station codes

| Station | Code |
|---------|------|
| London Paddington | `PAD` |
| London King's Cross | `KGX` |
| London Euston | `EUS` |
| London Waterloo | `WAT` |
| London Victoria | `VIC` |
| London Liverpool Street | `LST` |
| Birmingham New Street | `BHM` |
| Manchester Piccadilly | `MAN` |
| Leeds | `LDS` |
| Edinburgh Waverley | `EDB` |
| Glasgow Central | `GLC` |
| Bristol Temple Meads | `BRI` |
| Cardiff Central | `CDF` |
| York | `YRK` |

### 6. Configure permissions

To avoid running as root:

```bash
sudo setcap 'cap_sys_nice=eip' /usr/bin/python3.11
```

### 7. Test

```bash
cd /home/pi/trainline
env/bin/python3 trainline.py
```

Press `Ctrl-C` to quit.

### 8. Run on startup

```bash
sudo cp /home/pi/trainline/assets/trainline.service /etc/systemd/system/trainline.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable trainline.service
sudo systemctl start trainline.service
```

Check status:

```bash
sudo systemctl status trainline.service
journalctl -u trainline.service -f
```

## Web Configuration UI

A built-in web interface lets you update settings from any device on your network - no SSH required.

### Running the web UI

```bash
cd /home/pi/trainline
env/bin/python3 web_config.py
```

Then open `http://<your-pi-ip>:5000` in a browser. From there you can change:

- Station code
- Darwin API token and Huxley2 URL
- Display brightness and GPIO settings
- Refresh interval and departure limits

After saving, restart the tracker for changes to take effect:

```bash
sudo systemctl restart trainline.service
```

## Optional

### Loading LED

An LED can be wired to a GPIO pin to blink when data is being fetched. Add to `config.py`:

```python
LOADING_LED_ENABLED = True
LOADING_LED_GPIO_PIN = 25
```

## Display Layout

```
+----------------------------------------------------------------+
|  Destination Station Name              (large font, amber)     |
|----------------------------------------------------------------|
|  12:05  P3  On time                          1/5  (info row)   |
|                                                                |
|  Calling at: Reading, Swindon, Bristol...  (scrolling, amber)  |
+----------------------------------------------------------------+
```

- **Top**: Destination station name in large amber text
- **Middle**: Departure time (yellow), platform (white), status (green/amber/red), service index
- **Bottom**: Scrolling calling points in amber, cycling to next departure when complete

## License

Based on [FlightTracker](https://github.com/ColinWaddell/FlightTracker) by Colin Waddell.
Released under the GNU General Public License v3.0. See LICENSE for details.
