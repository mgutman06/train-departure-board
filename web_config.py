import importlib.util
import os
#import yaml
from flask import Flask, render_template_string, request, redirect


CONFIG_FILE = "config.py"

app = Flask(__name__)

def load_config():
    spec = importlib.util.spec_from_file_location("config", CONFIG_FILE)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        f.write("ZONE_HOME = {\n")
        f.write(f'    "tl_y": {data["zone_home_tl_y"]},\n')
        f.write(f'    "tl_x": {data["zone_home_tl_x"]},\n')
        f.write(f'    "br_y": {data["zone_home_br_y"]},\n')
        f.write(f'    "br_x": {data["zone_home_br_x"]}\n')
        f.write("}\n\n")

        f.write("ZONE_OVERHEAD = {\n")
        f.write(f'    "tl_y": {data["zone_overhead_tl_y"]},\n')
        f.write(f'    "tl_x": {data["zone_overhead_tl_x"]},\n')
        f.write(f'    "br_y": {data["zone_overhead_br_y"]},\n')
        f.write(f'    "br_x": {data["zone_overhead_br_x"]}\n')
        f.write("}\n\n")

        f.write(f"LOCATION_HOME = [{data['location_lat']}, {data['location_lon']}, {data['location_alt']}]\n")
        f.write(f'WEATHER_LOCATION = "{data["weather_location"]}"\n')
        f.write(f'OPENWEATHER_API_KEY = "{data["api_key"]}"\n')
        f.write(f'TEMPERATURE_UNITS = "{data["units"]}"\n')
        f.write(f"MIN_ALTITUDE = {data['min_altitude']}\n")
        f.write(f"BRIGHTNESS = {data['brightness']}\n")
        f.write(f"GPIO_SLOWDOWN = {data['gpio_slowdown']}\n")
        f.write(f'JOURNEY_CODE_SELECTED = "{data["journey_code"]}"\n')
        f.write(f'JOURNEY_BLANK_FILLER = "{data["journey_filler"]}"\n')
        f.write(f"HAT_PWM_ENABLED = {data['hat_pwm']}\n")
        f.write(f"RAINFALL_ENABLED = {data['rainfall']}\n")


@app.route("/", methods=["GET", "POST"])
def index():
    config = load_config()
    if request.method == "POST":
        save_config(request.form)
        return redirect("/")

    return render_template_string("""
        <h1>Config Editor</h1>
        <form method="post">
            <h2>Zone Home</h2>
            tl_y: <input name="zone_home_tl_y" value="{{c.ZONE_HOME['tl_y']}}"><br>
            tl_x: <input name="zone_home_tl_x" value="{{c.ZONE_HOME['tl_x']}}"><br>
            br_y: <input name="zone_home_br_y" value="{{c.ZONE_HOME['br_y']}}"><br>
            br_x: <input name="zone_home_br_x" value="{{c.ZONE_HOME['br_x']}}"><br>

            <h2>Weather</h2>
            Location: <input name="weather_location" value="{{c.WEATHER_LOCATION}}"><br>
            API Key: <input name="api_key" value="{{c.OPENWEATHER_API_KEY}}"><br>
            Units: <input name="units" value="{{c.TEMPERATURE_UNITS}}"><br>

           <h2>Zone Overhead</h2>
           tl_y: <input name="zone_overhead_tl_y" value="{{c.ZONE_OVERHEAD['tl_y']}}"><br>
           tl_x: <input name="zone_overhead_tl_x" value="{{c.ZONE_OVERHEAD['tl_x']}}"><br>
           br_y: <input name="zone_overhead_br_y" value="{{c.ZONE_OVERHEAD['br_y']}}"><br>
           br_x: <input name="zone_overhead_br_x" value="{{c.ZONE_OVERHEAD['br_x']}}"><br>

           <h2>Home Location</h2>
           Latitude: <input name="location_lat" value="{{c.LOCATION_HOME[0]}}"><br>
           Longitude: <input name="location_lon" value="{{c.LOCATION_HOME[1]}}"><br>
           Altitude: <input name="location_alt" value="{{c.LOCATION_HOME[2]}}"><br>


            <h2>System</h2>
            Min Altitude: <input name="min_altitude" value="{{c.MIN_ALTITUDE}}"><br>
            Brightness: <input name="brightness" value="{{c.BRIGHTNESS}}"><br>
            GPIO Slowdown: <input name="gpio_slowdown" value="{{c.GPIO_SLOWDOWN}}"><br>
            Journey Code: <input name="journey_code" value="{{c.JOURNEY_CODE_SELECTED}}"><br>
            Filler: <input name="journey_filler" value="{{c.JOURNEY_BLANK_FILLER}}"><br>
            PWM Enabled: <input name="hat_pwm" value="{{c.HAT_PWM_ENABLED}}"><br>
            Rainfall Enabled: <input name="rainfall" value="{{c.RAINFALL_ENABLED}}"><br>
            
            <br><button type="submit">Save</button>
        </form>
    """, c=config)

if __name__ == "__main__":
    # Host only on local network
    app.run(host="0.0.0.0", port=5000, debug=True)
