#!/bin/bash
# =============================================================================
# Train Tracker - Automated Setup Script
# =============================================================================
# This script installs and configures the Train Tracker on a Raspberry Pi.
# It sets up both the main display service and the web configuration UI
# to start automatically on boot.
#
# Usage:  sudo bash setup.sh
# =============================================================================

set -e

# --- Colours for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No colour

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Pre-flight checks ---
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root.  Try:  sudo bash setup.sh"
fi

INSTALL_USER="${SUDO_USER:-pi}"
INSTALL_HOME=$(eval echo "~$INSTALL_USER")
PROJECT_DIR="$INSTALL_HOME/TrainTracker"

if [ ! -f "$PROJECT_DIR/train-tracker.py" ]; then
    error "Could not find train-tracker.py in $PROJECT_DIR\n       Make sure you cloned the repo to $PROJECT_DIR first."
fi

info "Installing Train Tracker for user '$INSTALL_USER'"
info "Project directory: $PROJECT_DIR"
echo ""

# --- Step 1: System packages ---
info "Updating system packages..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-dev git > /dev/null 2>&1
info "System packages installed."

# --- Step 2: Python virtual environment ---
info "Setting up Python virtual environment..."
cd "$PROJECT_DIR"

if [ ! -d "env" ]; then
    sudo -u "$INSTALL_USER" python3 -m venv env
fi

sudo -u "$INSTALL_USER" env/bin/pip install --upgrade pip > /dev/null 2>&1
sudo -u "$INSTALL_USER" env/bin/pip install -r requirements.txt > /dev/null 2>&1
info "Python dependencies installed."

# --- Step 3: RGB matrix Python bindings ---
RGB_DIR="$INSTALL_HOME/rpi-rgb-led-matrix"
if [ -d "$RGB_DIR/bindings/python" ]; then
    info "Installing RGB matrix Python bindings..."
    cd "$RGB_DIR/bindings/python"
    sudo -u "$INSTALL_USER" "$PROJECT_DIR/env/bin/pip" install . > /dev/null 2>&1
    info "RGB matrix bindings installed."
else
    warn "RGB matrix library not found at $RGB_DIR"
    warn "You must install it separately before running the tracker."
    warn "See:  https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi"
fi

# --- Step 4: Set Python capabilities (avoids needing root) ---
PYTHON_BIN=$(readlink -f "$PROJECT_DIR/env/bin/python3")
info "Setting capabilities on $PYTHON_BIN ..."
setcap 'cap_sys_nice=eip' "$PYTHON_BIN" 2>/dev/null || true

# Also set on system Python in case venv links to it
SYS_PYTHON=$(readlink -f "$(which python3)")
setcap 'cap_sys_nice=eip' "$SYS_PYTHON" 2>/dev/null || true
info "Python capabilities set."

# --- Step 5: Install systemd services ---
cd "$PROJECT_DIR"

# Main tracker service
info "Installing TrainTracker systemd service..."
cat > /etc/systemd/system/TrainTracker.service << EOF
[Unit]
Description=Train Departure Display
After=network.target

[Service]
Type=simple
ExecStart=$PROJECT_DIR/env/bin/python $PROJECT_DIR/train-tracker.py
WorkingDirectory=$PROJECT_DIR
StandardOutput=append:$INSTALL_HOME/train.log
StandardError=append:$INSTALL_HOME/train.log
Restart=on-failure
User=$INSTALL_USER
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Web configuration UI service
info "Installing TrainTrackerWeb systemd service..."
cat > /etc/systemd/system/TrainTrackerWeb.service << EOF
[Unit]
Description=Train Tracker Web Configuration UI
After=network.target

[Service]
Type=simple
ExecStart=$PROJECT_DIR/env/bin/python $PROJECT_DIR/web_config.py
WorkingDirectory=$PROJECT_DIR
StandardOutput=append:$INSTALL_HOME/train-web.log
StandardError=append:$INSTALL_HOME/train-web.log
Restart=on-failure
User=$INSTALL_USER
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

# --- Step 6: Enable and start services ---
info "Enabling services to start on boot..."
systemctl enable TrainTracker.service > /dev/null 2>&1
systemctl enable TrainTrackerWeb.service > /dev/null 2>&1

# Start the web UI immediately so the user can configure credentials
info "Starting web configuration UI..."
systemctl start TrainTrackerWeb.service

# Get the Pi's IP address for the user
PI_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "============================================="
echo -e "${GREEN}  Setup complete!${NC}"
echo "============================================="
echo ""
echo "  Next steps:"
echo ""
echo "  1. Open the settings page in your browser:"
echo -e "     ${YELLOW}http://${PI_IP}:5000${NC}"
echo ""
echo "  2. Enter your Realtime Trains API credentials"
echo "     and choose your home station."
echo "     (Register free at https://api.rtt.io/)"
echo ""
echo "  3. Save settings, then start the display:"
echo -e "     ${YELLOW}sudo systemctl start TrainTracker.service${NC}"
echo ""
echo "  Both services will start automatically on boot."
echo ""
echo "  Useful commands:"
echo "    Check display status:  sudo systemctl status TrainTracker"
echo "    Check web UI status:   sudo systemctl status TrainTrackerWeb"
echo "    View display logs:     tail -f $INSTALL_HOME/train.log"
echo "    Restart after config:  sudo systemctl restart TrainTracker"
echo ""
