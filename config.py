# Trainline Configuration
# =======================

# Station to display departures for (CRS code)
# Common examples: PAD (Paddington), KGX (King's Cross), EUS (Euston),
# BHM (Birmingham New St), MAN (Manchester Piccadilly), LDS (Leeds),
# EDI (Edinburgh), GLC (Glasgow Central), BRI (Bristol Temple Meads)
STATION_CODE = "PAD"

# Darwin API token (National Rail Live Departure Boards)
# Register for free at https://realtime.nationalrail.co.uk/OpenLDBWSRegistration/
DARWIN_API_TOKEN = "your_darwin_token"

# Huxley2 API base URL (JSON proxy for Darwin)
# Default public instance — you can self-host your own
HUXLEY_URL = "https://huxley2.azurewebsites.net"

# Maximum number of departures to display
MAX_DEPARTURES = 10

# Display settings
BRIGHTNESS = 40
GPIO_SLOWDOWN = 4
HAT_PWM_ENABLED = False

# Data refresh interval in seconds
REFRESH_INTERVAL = 60

# Optional: GPIO loading LED
LOADING_LED_ENABLED = False
LOADING_LED_GPIO_PIN = 25
