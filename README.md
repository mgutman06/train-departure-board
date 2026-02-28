# RGB Matrix Train Departure Display

A Raspberry Pi-powered LED matrix display that shows live UK train departure information, styled like the dot matrix displays found at railway stations across the United Kingdom.

Uses the [Realtime Trains API](https://api.rtt.io/) for live departure data displayed on a 64x32 RGB LED matrix panel.

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
git clone https://github.com/ColinWaddell/FlightTracker TrainTracker
cd /home/pi/TrainTracker
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

1. Register for a free account at [https://api.rtt.io/](https://api.rtt.io/)
2. Note your API username and password

### 5. Configure

```bash
cd /home/pi/TrainTracker
nano config.py
```

Example configuration:

```python
# Station to display departures for (CRS code)
STATION_CODE = "PAD"

# Realtime Trains API credentials
RTT_API_USERNAME = "your_rtt_username"
RTT_API_PASSWORD = "your_rtt_password"

# Maximum number of departures to display
MAX_DEPARTURES = 10

# How many services to fetch calling points for
MAX_CALLING_POINT_LOOKUPS = 6

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
| `RTT_API_USERNAME`         | Your Realtime Trains API username. Register at [api.rtt.io](https://api.rtt.io/). |
| `RTT_API_PASSWORD`         | Your Realtime Trains API password. |
| `MAX_DEPARTURES`           | Maximum number of departures to fetch and cycle through. |
| `MAX_CALLING_POINT_LOOKUPS`| How many services to fetch detailed calling points for (each is an API call). |
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
cd /home/pi/TrainTracker
env/bin/python3 train-tracker.py
```

Press `Ctrl-C` to quit.

### 8. Run on startup

```bash
sudo cp /home/pi/TrainTracker/assets/TrainTracker.service /etc/systemd/system/TrainTracker.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable TrainTracker.service
sudo systemctl start TrainTracker.service
```

Check status:

```bash
sudo systemctl status TrainTracker.service
journalctl -u TrainTracker.service -f
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
