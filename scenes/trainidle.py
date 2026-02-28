from datetime import datetime

from rgbmatrix import graphics

from utilities.animator import Animator
from setup import colours, fonts, screen

# Layout
STATION_FONT = fonts.small
STATION_Y = 12
CLOCK_FONT = fonts.regular
CLOCK_Y = 28
TRAIN_Y = 20

TRAIN_COLOUR = colours.AMBER
TRACK_COLOUR = colours.AMBER_DARK
SMOKE_COLOUR = colours.GREY


class TrainIdleScene(object):
    def __init__(self):
        super().__init__()
        self._train_x = -30
        self._last_idle_time = None

    def _draw_train(self, canvas, x, y):
        """Draw a simple side-view steam train."""
        # Engine body
        graphics.DrawLine(canvas, x, y, x + 14, y, TRAIN_COLOUR)
        graphics.DrawLine(canvas, x, y - 1, x + 14, y - 1, TRAIN_COLOUR)
        graphics.DrawLine(canvas, x + 2, y - 2, x + 14, y - 2, TRAIN_COLOUR)
        graphics.DrawLine(canvas, x + 4, y - 3, x + 10, y - 3, TRAIN_COLOUR)

        # Chimney
        graphics.DrawLine(canvas, x + 12, y - 3, x + 12, y - 5, TRAIN_COLOUR)
        graphics.DrawLine(canvas, x + 13, y - 3, x + 13, y - 5, TRAIN_COLOUR)

        # Cab (rear)
        graphics.DrawLine(canvas, x, y - 2, x + 1, y - 2, TRAIN_COLOUR)
        graphics.DrawLine(canvas, x, y - 3, x + 1, y - 3, TRAIN_COLOUR)
        graphics.DrawLine(canvas, x, y - 4, x + 1, y - 4, TRAIN_COLOUR)

        # Wheels
        canvas.SetPixel(x + 2, y + 1, TRAIN_COLOUR.red, TRAIN_COLOUR.green, TRAIN_COLOUR.blue)
        canvas.SetPixel(x + 6, y + 1, TRAIN_COLOUR.red, TRAIN_COLOUR.green, TRAIN_COLOUR.blue)
        canvas.SetPixel(x + 10, y + 1, TRAIN_COLOUR.red, TRAIN_COLOUR.green, TRAIN_COLOUR.blue)
        canvas.SetPixel(x + 13, y + 1, TRAIN_COLOUR.red, TRAIN_COLOUR.green, TRAIN_COLOUR.blue)

        # Track
        graphics.DrawLine(canvas, 0, y + 2, screen.WIDTH - 1, y + 2, TRACK_COLOUR)

    @Animator.KeyFrame.add(2)
    def train_idle(self, count):
        if len(self._data) > 0:
            return

        self.canvas.Clear()

        # Draw station name
        station = self._station_name
        graphics.DrawText(
            self.canvas, STATION_FONT, 1, 8, colours.STATION_NAME_COLOUR, station
        )

        # Draw clock
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        graphics.DrawText(
            self.canvas, CLOCK_FONT, 1, CLOCK_Y, colours.CLOCK_COLOUR, current_time
        )

        # Draw "No departures" text
        graphics.DrawText(
            self.canvas, fonts.extrasmall, 34, CLOCK_Y, colours.AMBER_DARK, "No deps"
        )

        # Animate train
        self._draw_train(self.canvas, int(self._train_x), TRAIN_Y)
        self._train_x += 0.5
        if self._train_x > screen.WIDTH + 30:
            self._train_x = -30
