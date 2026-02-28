import importlib.util
import os
from flask import Flask, render_template_string, request, redirect

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")

app = Flask(__name__)


def load_config():
    spec = importlib.util.spec_from_file_location("config", CONFIG_FILE)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        f.write("# Trainline Configuration\n")
        f.write("# =======================\n\n")
        f.write(f'STATION_CODE = "{data["station_code"].strip().upper()}"\n\n')
        f.write(f'DARWIN_API_TOKEN = "{data["darwin_token"].strip()}"\n\n')
        f.write(f'HUXLEY_URL = "{data["huxley_url"].strip()}"\n\n')
        f.write(f"MAX_DEPARTURES = {int(data['max_departures'])}\n\n")
        f.write(f"BRIGHTNESS = {int(data['brightness'])}\n")
        f.write(f"GPIO_SLOWDOWN = {int(data['gpio_slowdown'])}\n")
        f.write(f"HAT_PWM_ENABLED = {data['hat_pwm'] == 'True'}\n\n")
        f.write(f"REFRESH_INTERVAL = {int(data['refresh_interval'])}\n\n")
        f.write(f"LOADING_LED_ENABLED = {data.get('loading_led') == 'on'}\n")
        f.write(f"LOADING_LED_GPIO_PIN = {int(data['led_gpio_pin'])}\n")


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trainline Settings</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            min-height: 100vh;
        }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        h1 {
            text-align: center;
            color: #ffb000;
            margin-bottom: 8px;
            font-size: 1.6em;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 24px;
            font-size: 0.9em;
        }
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid #1a1a4e;
        }
        .card h2 {
            color: #ffb000;
            font-size: 1.1em;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #1a1a4e;
        }
        .field { margin-bottom: 14px; }
        .field:last-child { margin-bottom: 0; }
        label {
            display: block;
            font-size: 0.85em;
            color: #aaa;
            margin-bottom: 4px;
        }
        input[type="text"], input[type="password"], input[type="number"], select {
            width: 100%;
            padding: 10px 12px;
            border-radius: 8px;
            border: 1px solid #2a2a5e;
            background: #0f3460;
            color: #e0e0e0;
            font-size: 1em;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #ffb000;
        }
        .hint {
            font-size: 0.75em;
            color: #666;
            margin-top: 3px;
        }
        .checkbox-field {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .checkbox-field input { width: auto; }
        .checkbox-field label { margin-bottom: 0; }
        button {
            width: 100%;
            padding: 14px;
            background: #ffb000;
            color: #1a1a2e;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            margin-top: 8px;
        }
        button:hover { background: #ffc340; }
        .saved {
            text-align: center;
            background: #0a3d20;
            color: #4caf50;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
            border: 1px solid #1b5e20;
        }
        .row { display: flex; gap: 12px; }
        .row .field { flex: 1; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Trainline</h1>
        <p class="subtitle">Configure your departure display</p>

        {% if saved %}
        <div class="saved">Settings saved. Changes will apply automatically on the next data refresh. Display hardware settings (brightness, GPIO, HAT PWM) still require a restart.</div>
        {% endif %}

        <form method="post">
            <div class="card">
                <h2>Station</h2>
                <div class="field">
                    <label for="station_code">Station Code (CRS)</label>
                    <input type="text" id="station_code" name="station_code"
                           value="{{ c.STATION_CODE }}" maxlength="3"
                           style="text-transform: uppercase;">
                    <div class="hint">e.g. PAD, KGX, EUS, BHM, MAN, LDS, EDB, GLC</div>
                </div>
            </div>

            <div class="card">
                <h2>API Credentials</h2>
                <div class="field">
                    <label for="darwin_token">Darwin API Token</label>
                    <input type="password" id="darwin_token" name="darwin_token"
                           value="{{ c.DARWIN_API_TOKEN }}">
                    <div class="hint">Register free at realtime.nationalrail.co.uk/OpenLDBWSRegistration</div>
                </div>
                <div class="field">
                    <label for="huxley_url">Huxley2 URL</label>
                    <input type="text" id="huxley_url" name="huxley_url"
                           value="{{ c.HUXLEY_URL }}">
                    <div class="hint">Default: https://huxley2.azurewebsites.net</div>
                </div>
            </div>

            <div class="card">
                <h2>Display</h2>
                <div class="row">
                    <div class="field">
                        <label for="brightness">Brightness (0-100)</label>
                        <input type="number" id="brightness" name="brightness"
                               value="{{ c.BRIGHTNESS }}" min="0" max="100">
                    </div>
                    <div class="field">
                        <label for="gpio_slowdown">GPIO Slowdown (0-4)</label>
                        <input type="number" id="gpio_slowdown" name="gpio_slowdown"
                               value="{{ c.GPIO_SLOWDOWN }}" min="0" max="4">
                    </div>
                </div>
                <div class="field">
                    <label for="hat_pwm">HAT PWM (soundcard)</label>
                    <select id="hat_pwm" name="hat_pwm">
                        <option value="True" {{ 'selected' if c.HAT_PWM_ENABLED else '' }}>Enabled</option>
                        <option value="False" {{ 'selected' if not c.HAT_PWM_ENABLED else '' }}>Disabled</option>
                    </select>
                    <div class="hint">Enable if solder bridge added to HAT</div>
                </div>
            </div>

            <div class="card">
                <h2>Data</h2>
                <div class="row">
                    <div class="field">
                        <label for="max_departures">Max Departures</label>
                        <input type="number" id="max_departures" name="max_departures"
                               value="{{ c.MAX_DEPARTURES }}" min="1" max="20">
                    </div>
                    <div class="field">
                        <label for="refresh_interval">Refresh Interval (seconds)</label>
                        <input type="number" id="refresh_interval" name="refresh_interval"
                               value="{{ c.REFRESH_INTERVAL }}" min="30" max="300">
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Loading LED (optional)</h2>
                <div class="checkbox-field">
                    <input type="checkbox" id="loading_led" name="loading_led"
                           {{ 'checked' if c.LOADING_LED_ENABLED else '' }}>
                    <label for="loading_led">Enable GPIO loading LED</label>
                </div>
                <div class="field" style="margin-top: 12px;">
                    <label for="led_gpio_pin">GPIO Pin</label>
                    <input type="number" id="led_gpio_pin" name="led_gpio_pin"
                           value="{{ c.LOADING_LED_GPIO_PIN }}" min="0" max="27">
                </div>
            </div>

            <button type="submit">Save Settings</button>
        </form>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    saved = False
    if request.method == "POST":
        save_config(request.form)
        saved = True

    config = load_config()
    return render_template_string(TEMPLATE, c=config, saved=saved)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
