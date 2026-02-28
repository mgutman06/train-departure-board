from rgbmatrix import graphics

from utilities.animator import Animator
from setup import colours, screen

# Layout
TRACK_Y = 27
TRACK_X_START = 3
TRACK_X_END = 60
MAX_DOTS = 10
MAX_MINUTES = 20  # at this many minutes out, train shows at second-to-last stop

# Colours
TRACK_LINE_COLOUR = colours.AMBER_DARK
PASSED_STOP_COLOUR = colours.AMBER_DIM
DEST_STOP_COLOUR = colours.AMBER
TRAIN_MARKER_COLOUR = colours.GREEN


class CallingPointsScene(object):
    def __init__(self):
        super().__init__()
        self._data_all_looped = False

    @Animator.KeyFrame.add(0)
    def route_progress(self):
        # Always allow data refresh since we don't cycle through services
        self._data_all_looped = True

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
            is_dest = (i == len(positions) - 1)
            c = DEST_STOP_COLOUR if is_dest else PASSED_STOP_COLOUR

            # Draw dot (3px wide)
            self.canvas.SetPixel(x, TRACK_Y, c.red, c.green, c.blue)
            self.canvas.SetPixel(x - 1, TRACK_Y, c.red, c.green, c.blue)
            self.canvas.SetPixel(x + 1, TRACK_Y, c.red, c.green, c.blue)
            if is_dest:
                # Slightly larger for destination
                self.canvas.SetPixel(x, TRACK_Y - 1, c.red, c.green, c.blue)
                self.canvas.SetPixel(x, TRACK_Y + 1, c.red, c.green, c.blue)

        # Position train marker based on mins_until
        mins_str = dep.get("mins_until", "")
        if dep.get("cancelled", False) or not mins_str:
            return  # no marker for cancelled or unknown

        if mins_str == "Due":
            mins = 0
        elif mins_str.endswith("min"):
            try:
                mins = int(mins_str[:-3])
            except ValueError:
                return
        else:
            return

        # Place train between second-to-last and last dot based on ETA
        if len(positions) >= 2:
            from_x = positions[-2]
            to_x = positions[-1]
            progress = 1.0 - min(mins / MAX_MINUTES, 1.0)
            train_x = int(from_x + (to_x - from_x) * progress)
        else:
            train_x = positions[0]

        # Draw train marker (bright block above track)
        c = TRAIN_MARKER_COLOUR
        self.canvas.SetPixel(train_x - 1, TRACK_Y - 2, c.red, c.green, c.blue)
        self.canvas.SetPixel(train_x, TRACK_Y - 2, c.red, c.green, c.blue)
        self.canvas.SetPixel(train_x + 1, TRACK_Y - 2, c.red, c.green, c.blue)
        self.canvas.SetPixel(train_x, TRACK_Y - 1, c.red, c.green, c.blue)
