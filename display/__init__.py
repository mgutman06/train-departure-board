import sys
from setup import frames
from utilities.animator import Animator
from utilities.trains import Departures, load_config
from scenes.destination import DestinationScene
from scenes.departureinfo import DepartureInfoScene
from scenes.callingpoints import CallingPointsScene
from scenes.loadingpulse import LoadingPulseScene
from scenes.loadingled import LoadingLEDScene
from scenes.trainidle import TrainIdleScene
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions


def services_match(services_a, services_b):
    """Check if two service lists contain the same departures."""
    get_ids = lambda services: [
        f"{s['scheduled']}-{s['destination']}" for s in services
    ]
    return set(get_ids(services_a)) == set(get_ids(services_b))


try:
    from config import BRIGHTNESS, GPIO_SLOWDOWN, HAT_PWM_ENABLED
except (ModuleNotFoundError, NameError):
    BRIGHTNESS = 100
    GPIO_SLOWDOWN = 4
    HAT_PWM_ENABLED = False

try:
    from config import LOADING_LED_ENABLED
except (ModuleNotFoundError, NameError, ImportError):
    LOADING_LED_ENABLED = False

try:
    from config import REFRESH_INTERVAL
except (ModuleNotFoundError, NameError, ImportError):
    REFRESH_INTERVAL = 60


class Display(
    DestinationScene,
    DepartureInfoScene,
    CallingPointsScene,
    LoadingLEDScene if LOADING_LED_ENABLED else LoadingPulseScene,
    TrainIdleScene,
    Animator,
):
    def __init__(self):
        # Setup Display
        options = RGBMatrixOptions()
        options.hardware_mapping = "regular"
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = BRIGHTNESS
        options.pwm_lsb_nanoseconds = 50
        options.led_rgb_sequence = "RGB"
        options.pixel_mapper_config = ""
        options.show_refresh_rate = 0
        options.gpio_slowdown = GPIO_SLOWDOWN
        options.disable_hardware_pulsing = not HAT_PWM_ENABLED
        options.drop_privileges = True
        self.matrix = RGBMatrix(options=options)

        # Setup canvas
        self.canvas = self.matrix.CreateFrameCanvas()
        self.canvas.Clear()

        # Data to render
        self._data_index = 0
        self._data = []
        self._station_name = ""

        # Start fetching train departures
        self.departures = Departures()
        self.departures.grab_data()

        # Initialise animator and scenes
        super().__init__()

        # Overwrite any default settings from
        # Animator or Scenes
        self.delay = frames.PERIOD

    def draw_square(self, x0, y0, x1, y1, colour):
        for x in range(x0, x1):
            _ = graphics.DrawLine(self.canvas, x, y0, x, y1, colour)

    @Animator.KeyFrame.add(0)
    def clear_screen(self):
        self.canvas.Clear()

    @Animator.KeyFrame.add(frames.PER_SECOND * 4)
    def check_for_loaded_data(self, count):
        if self.departures.new_data:
            there_is_data = len(self._data) > 0 or not self.departures.data_is_empty

            new_data = self.departures.data
            self._station_name = self.departures.station_name

            data_is_different = not services_match(self._data, new_data)

            if data_is_different:
                self._data_index = 0
                self._data_all_looped = False
                self._data = new_data

            reset_required = there_is_data and data_is_different

            if reset_required:
                self.reset_scene()

    @Animator.KeyFrame.add(1)
    def sync(self, count):
        _ = self.matrix.SwapOnVSync(self.canvas)

    @Animator.KeyFrame.add(frames.PER_SECOND * REFRESH_INTERVAL)
    def grab_new_data(self, count):
        # Reload refresh interval from config so web UI changes apply live
        cfg = load_config()
        new_divisor = int(frames.PER_SECOND * cfg.get("REFRESH_INTERVAL", REFRESH_INTERVAL))
        if self.grab_new_data.properties["divisor"] != new_divisor:
            self.grab_new_data.properties["divisor"] = new_divisor

        if not (self.departures.processing and self.departures.new_data) and (
            self._data_all_looped or len(self._data) <= 1
        ):
            self.departures.grab_data()

    def run(self):
        try:
            print("Train Tracker running - Press CTRL-C to stop")
            self.play()
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)
