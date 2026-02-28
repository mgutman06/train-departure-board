from rgbmatrix import graphics

from utilities.animator import Animator
from setup import colours, screen

# Layout
TRACK_Y = 27
TRACK_X_START = 3
TRACK_X_END = 60
MAX_DOTS = 10
DISPLAY_FRAMES = 50  # 5 seconds per service at 10fps

# Colours
TRACK_LINE_COLOUR = colours.AMBER_DARK
PASSED_STOP_COLOUR = colours.AMBER_DIM
DEST_STOP_COLOUR = colours.AMBER
TRAIN_MARKER_COLOUR = colours.GREEN


class CallingPointsScene(object):
    def __init__(self):
        super().__init__()
        self._route_frame = 0
        self._data_all_looped = False

    @Animator.KeyFrame.add(1)
    def route_progress(self, count):
        if len(self._data) == 0:
            return

        dep = self._data[self._data_index]
        calling = dep.get("calling_points", [])

        # Total stops: origin + calling points + our station
        total_stops = len(calling) + 2
        shown_stops = min(total_stops, MAX_DOTS)

        # Clear the bottom area
        self.draw_square(0, TRACK_Y - 4, screen.WIDTH, screen.HEIGHT, colours.BLACK)

        # Draw track line
        graphics.DrawLine(
            self.canvas, TRACK_X_START, TRACK_Y,
            TRACK_X_END, TRACK_Y, TRACK_LINE_COLOUR
        )

        # Calculate evenly spaced dot positions
        if shown_stops <= 1:
            positions = [TRACK_X_END]
        else:
            positions = [
                TRACK_X_START + i * (TRACK_X_END - TRACK_X_START) // (shown_stops - 1)
                for i in range(shown_stops)
            ]

        # Draw stop dots
        for i, x in enumerate(positions):
            is_origin = (i == 0)
            is_dest = (i == len(positions) - 1)

            if is_origin:
                c = TRAIN_MARKER_COLOUR  # Green dot where the train is
            elif is_dest:
                c = DEST_STOP_COLOUR
            else:
                c = PASSED_STOP_COLOUR

            # Draw dot (3px wide)
            self.canvas.SetPixel(x, TRACK_Y, c.red, c.green, c.blue)
            self.canvas.SetPixel(x - 1, TRACK_Y, c.red, c.green, c.blue)
            self.canvas.SetPixel(x + 1, TRACK_Y, c.red, c.green, c.blue)
            if is_dest or is_origin:
                # Slightly larger for origin and destination
                self.canvas.SetPixel(x, TRACK_Y - 1, c.red, c.green, c.blue)
                self.canvas.SetPixel(x, TRACK_Y + 1, c.red, c.green, c.blue)

        self._route_frame += 1

        # Cycle to next service after display duration
        if self._route_frame >= DISPLAY_FRAMES:
            self._route_frame = 0
            if len(self._data) > 1:
                self._data_index = (self._data_index + 1) % len(self._data)
                self._data_all_looped = (not self._data_index) or self._data_all_looped
                self.reset_scene()

    @Animator.KeyFrame.add(0)
    def reset_route(self):
        self._route_frame = 0
