# Trainline Configuration
# =======================

# Station to display departures for (CRS code)
# Common examples: PAD (Paddington), KGX (King's Cross), EUS (Euston),
# BHM (Birmingham New St), MAN (Manchester Piccadilly), LDS (Leeds),
# EDI (Edinburgh), GLC (Glasgow Central), BRI (Bristol Temple Meads)
STATION_CODE = "PAD"

# Realtime Trains API credentials
# Register for free at https://api.rtt.io/
RTT_API_USERNAME = "your_rtt_username"
RTT_API_PASSWORD = "your_rtt_password"

# Maximum number of departures to display
MAX_DEPARTURES = 10

# How many services to fetch calling points for
# (each requires an additional API call)
MAX_CALLING_POINT_LOOKUPS = 6

# Display settings
BRIGHTNESS = 40
GPIO_SLOWDOWN = 4
HAT_PWM_ENABLED = False

# Data refresh interval in seconds
REFRESH_INTERVAL = 60

# Optional: GPIO loading LED
LOADING_LED_ENABLED = False
LOADING_LED_GPIO_PIN = 25
