# Train Tracker - Complete Installation Guide

A step-by-step guide to building a live UK train departure display using a
Raspberry Pi and an RGB LED matrix panel. This guide assumes you are starting
from a brand-new, unopened Raspberry Pi and have never used one before.

---

## Table of Contents

1. [What You Need to Buy](#1-what-you-need-to-buy)
2. [Flash the SD Card](#2-flash-the-sd-card)
3. [First Boot and SSH Access](#3-first-boot-and-ssh-access)
4. [Assemble the Hardware](#4-assemble-the-hardware)
5. [Install the RGB Matrix Driver](#5-install-the-rgb-matrix-driver)
6. [Install Train Tracker](#6-install-train-tracker)
7. [Get Your API Credentials](#7-get-your-api-credentials)
8. [Configure via Web UI](#8-configure-via-the-web-ui)
9. [Start the Display](#9-start-the-display)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What You Need to Buy

| Item | Notes |
|------|-------|
| **Raspberry Pi** | Pi Zero 2 W, Pi 3, Pi 4, or Pi 5 all work. The Pi Zero 2 W is the cheapest option. |
| **Micro SD card** | 8 GB or larger. Class 10 or better recommended. |
| **Adafruit RGB Matrix Bonnet** | Sits on top of the Pi and drives the LED panel. [Product page](https://www.adafruit.com/product/3211). |
| **64x32 RGB LED Matrix Panel** | P3 or P4 pitch, HUB75 connector. Widely available online. |
| **5V 4A power supply** | For the LED matrix. The bonnet has a screw terminal for this. |
| **USB-C power supply for the Pi** | Official Raspberry Pi PSU recommended (5V 3A). |
| **Micro SD card reader** | To flash the operating system from your computer. |

**Optional but recommended:**
- A case or standoffs to mount the Pi behind the panel
- Short GPIO header if using a Pi Zero (needs soldering)

---

## 2. Flash the SD Card

You will install Raspberry Pi OS onto the SD card from your main computer
(Windows, Mac, or Linux). The Pi will run "headless" — no monitor, keyboard,
or mouse attached.

### 2.1 Download Raspberry Pi Imager

Download and install the official imaging tool:

- **Windows / Mac / Linux**: https://www.raspberrypi.com/software/

### 2.2 Flash the OS

1. Insert the micro SD card into your computer.
2. Open **Raspberry Pi Imager**.
3. Click **Choose Device** and select your Pi model.
4. Click **Choose OS** → **Raspberry Pi OS (other)** → **Raspberry Pi OS Lite (64-bit)**.
   - You want the **Lite** version (no desktop). It uses less resources.
5. Click **Choose Storage** and select your SD card.
6. Click **Next**. When prompted, click **Edit Settings** to pre-configure:

#### OS Customisation Settings (important!)

On the **General** tab:
- **Set hostname**: `traintracker` (or whatever you like)
- **Set username and password**: Choose a username (default: `pi`) and a strong password. **Write this down.**
- **Configure wireless LAN**: Enter your Wi-Fi network name (SSID) and password. Select your country.
- **Set locale settings**: Choose your timezone.

On the **Services** tab:
- **Enable SSH**: Select **Use password authentication**.

7. Click **Save**, then **Yes** to apply settings.
8. Wait for the write and verification to complete.
9. Remove the SD card from your computer.

---

## 3. First Boot and SSH Access

### 3.1 Boot the Pi

1. Insert the SD card into the Raspberry Pi.
2. Connect the USB-C power supply to the Pi.
3. Wait 1-2 minutes for it to boot and connect to your Wi-Fi.

### 3.2 Find the Pi's IP Address

You need the Pi's IP address to connect to it. Try any of these methods:

**Option A — Use the hostname (simplest):**
```
ping traintracker.local
```
If this responds, you can use `traintracker.local` instead of an IP address
everywhere in this guide.

**Option B — Check your router:**
Log into your router's admin page (often 192.168.1.1 or 192.168.0.1) and look
for a device named `traintracker` in the connected devices list.

**Option C — Scan the network:**
- **Windows**: Download [Advanced IP Scanner](https://www.advanced-ip-scanner.com/)
- **Mac/Linux**: `arp -a` or install `nmap` and run `nmap -sn 192.168.1.0/24`

### 3.3 Connect via SSH

**On Mac or Linux** open Terminal. **On Windows** open PowerShell or Command
Prompt (Windows 10+) or install [PuTTY](https://www.putty.org/).

```bash
ssh pi@traintracker.local
```

Replace `pi` with the username you chose during setup, and `traintracker.local`
with the IP address if the hostname doesn't resolve.

When prompted, type `yes` to accept the host key, then enter your password.

You should now see a prompt like:
```
pi@traintracker:~ $
```

**Every command from this point onwards is typed into this SSH session.**

---

## 4. Assemble the Hardware

> **Do this with the Pi powered off.** Unplug the USB-C cable first.

1. **Attach the RGB Matrix Bonnet** to the Pi's 40-pin GPIO header. Press it
   firmly and evenly until fully seated.

2. **Connect the LED panel** to the bonnet using the HUB75 ribbon cable.
   The cable connects to the **input** connector on the back of the panel
   (usually labelled "IN" or marked with an arrow). Make sure the red stripe
   on the ribbon cable aligns with pin 1.

3. **Connect the 5V power supply** to the screw terminal on the bonnet (red
   to +, black to −). This powers the LED panel.

4. **Reconnect the Pi's USB-C power supply.**

For detailed assembly photos and instructions, see the
[Adafruit guide](https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi/overview).

### Optional: Solder bridge for sound-card PWM

Adding a small solder bridge on the bonnet improves display quality by using
the Pi's PWM hardware. This is recommended but not required. See
[this photo](https://learn.adafruit.com/assets/57727) for the exact location.
If you do this, you will enable `HAT_PWM_ENABLED` in the configuration later.

---

## 5. Install the RGB Matrix Driver

SSH back into the Pi and run:

```bash
sudo apt-get update && sudo apt-get -y dist-upgrade
```

This may take several minutes. Then install the RGB matrix library:

```bash
cd /home/pi
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh > /tmp/rgb-matrix.sh
sudo bash /tmp/rgb-matrix.sh
```

The installer will ask you questions:

1. **Which matrix driver?** Select **Adafruit RGB Matrix Bonnet** (option 2).
2. **Quality vs convenience?** Select **Quality** to enable hardware PWM
   (recommended).
3. When it asks to reboot, say **Yes**.

After the reboot, SSH in again and test the display:

```bash
cd /home/pi/rpi-rgb-led-matrix/examples-api-use
sudo ./demo --led-rows=32 --led-cols=64 -D0
```

You should see a pattern on the LED panel. Press `Ctrl-C` to stop.

If the display is flickering, don't worry — this will be tuned later via
the `GPIO_SLOWDOWN` setting.

---

## 6. Install Train Tracker

### 6.1 Clone the repository

```bash
cd /home/pi
git clone https://github.com/ColinWaddell/FlightTracker TrainTracker
cd TrainTracker
```

### 6.2 Run the setup script

A single script handles the entire software installation: creating the
virtual environment, installing dependencies, setting permissions, and
registering the services to start on boot.

```bash
sudo bash setup.sh
```

This will:
- Install Python dependencies in a virtual environment
- Install the RGB matrix Python bindings
- Set the necessary Linux capabilities so the display doesn't need root
- Create two systemd services:
  - **TrainTracker** — the main departure display (not started yet)
  - **TrainTrackerWeb** — the settings web page (started immediately)
- Enable both services to launch automatically whenever the Pi boots

When the script finishes it will print the URL for the settings page.

---

## 7. Get Your API Credentials

The display uses the **Realtime Trains API** to fetch live departure data.
You need a free account.

1. Go to **https://api.rtt.io/** in your browser (on your phone or computer,
   not the Pi).
2. Click **Register** and create an account.
3. After registering, you will receive an **API username** and **API password**
   (also called an API auth token). These are separate from your login password.
4. Keep this page open — you will need these credentials in the next step.

---

## 8. Configure via the Web UI

The setup script started a settings page that you can access from any device
on the same Wi-Fi network as the Pi.

### 8.1 Open the settings page

On your phone, tablet, or computer, open a browser and go to:

```
http://traintracker.local:5000
```

or

```
http://<your-pi-ip-address>:5000
```

You will see the Train Tracker settings page.

### 8.2 Enter your settings

Fill in at minimum:

| Field | What to enter |
|-------|---------------|
| **Station Code** | The 3-letter CRS code for your station. See the table below. |
| **Realtime Trains Username** | The API username from step 7. |
| **Realtime Trains Password** | The API password from step 7. |

All other settings have sensible defaults, but you can adjust:

| Field | Default | Description |
|-------|---------|-------------|
| Brightness | 40 | LED brightness, 0-100. Start low; these panels are very bright. |
| GPIO Slowdown | 4 | Reduce if your Pi is slow (Pi Zero: try 1-2). Increase if flickering (Pi 4/5: use 4). |
| HAT PWM | Disabled | Enable only if you added the solder bridge in step 4. |
| Max Departures | 10 | How many departures to cycle through. |
| Refresh Interval | 60 | Seconds between API fetches. Don't go below 30. |

### 8.3 Common station codes

| Station | Code | | Station | Code |
|---------|------|-|---------|------|
| London Paddington | `PAD` | | Manchester Piccadilly | `MAN` |
| London King's Cross | `KGX` | | Leeds | `LDS` |
| London Euston | `EUS` | | Edinburgh Waverley | `EDB` |
| London Waterloo | `WAT` | | Glasgow Central | `GLC` |
| London Victoria | `VIC` | | Bristol Temple Meads | `BRI` |
| London Liverpool Street | `LST` | | Cardiff Central | `CDF` |
| Birmingham New Street | `BHM` | | York | `YRK` |

Find any station code at the [National Rail website](https://www.nationalrail.co.uk/).

### 8.4 Save

Click **Save Settings**. You will see a green confirmation banner.

---

## 9. Start the Display

Back in your SSH session, start the main display:

```bash
sudo systemctl start TrainTracker.service
```

The LED panel should light up within a few seconds showing departures from
your chosen station.

**That's it — you're done!** Both services are set to start automatically
on boot, so if the Pi loses power or is restarted, everything will come
back up on its own.

### Useful commands

| What | Command |
|------|---------|
| Check display status | `sudo systemctl status TrainTracker` |
| Check web UI status | `sudo systemctl status TrainTrackerWeb` |
| Stop the display | `sudo systemctl stop TrainTracker` |
| Restart after changing settings | `sudo systemctl restart TrainTracker` |
| View live logs | `tail -f ~/train.log` |
| View web UI logs | `tail -f ~/train-web.log` |

### Changing settings later

The web UI is always available at `http://traintracker.local:5000`. After
saving new settings, restart the display to apply them:

```bash
sudo systemctl restart TrainTracker.service
```

Or simply reboot the Pi:

```bash
sudo reboot
```

---

## 10. Troubleshooting

### The LED panel stays dark

- **Check power.** The 5V supply must be connected to the bonnet's screw
  terminal, not just USB power.
- **Check the ribbon cable.** Make sure it is plugged into the panel's
  **input** port, not the output.
- **Check the service is running:**
  ```bash
  sudo systemctl status TrainTracker
  ```
- **Check the logs:**
  ```bash
  tail -50 ~/train.log
  ```

### The display shows an animated train but no departures

This means the display is working but no departure data is available. This
happens when:
- API credentials are wrong — check your username and password in the web UI.
- The station code is invalid — double-check it on the National Rail website.
- There are genuinely no departures (e.g. late at night or during a strike).

Check the log for API errors:
```bash
grep -i error ~/train.log
```

### The display is flickering

Adjust the `GPIO Slowdown` value in the web UI:
- **Pi Zero 2 W**: try `1` or `2`
- **Pi 3**: try `2` or `3`
- **Pi 4 / Pi 5**: try `4`

Then restart the service.

### I can't reach the web UI

- Make sure you are on the same Wi-Fi network as the Pi.
- Try the IP address instead of the hostname: `http://<ip>:5000`
- Check if the web service is running:
  ```bash
  sudo systemctl status TrainTrackerWeb
  ```
- If it is not running, start it:
  ```bash
  sudo systemctl start TrainTrackerWeb
  ```

### SSH connection refused

- The Pi may still be booting. Wait 1-2 minutes and try again.
- Make sure you enabled SSH during the SD card setup (step 2.6).
- If you can't connect at all, you may need to re-flash the SD card and
  double-check the Wi-Fi settings.

### I want to edit config.py directly

If you prefer the command line over the web UI:

```bash
nano /home/pi/TrainTracker/config.py
```

Save with `Ctrl-O`, `Enter`, then exit with `Ctrl-X`. Restart the service
afterwards.

### I want to update to the latest version

```bash
cd /home/pi/TrainTracker
sudo systemctl stop TrainTracker
git pull
sudo systemctl start TrainTracker
```

### Checking the Pi's IP address from SSH

```bash
hostname -I
```

### Viewing real-time display output

```bash
journalctl -u TrainTracker.service -f
```

Press `Ctrl-C` to stop following the log.
