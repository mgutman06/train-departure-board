from datetime import datetime

from rgbmatrix import graphics

from utilities.animator import Animator
from setup import colours, fonts, screen

# Layout
TRAIN_Y = 20
CAR_HEIGHT = 7
CAR_PAD = 2
CAR_GAP = 3
CHAR_WIDTH = 4
ENGINE_WIDTH = 15

TRAIN_COLOUR = colours.AMBER
TRACK_COLOUR = colours.AMBER_DARK
SMOKE_COLOUR = colours.GREY


class TrainIdleScene(object):
    def __init__(self):
        super().__init__()
        self._idle_x = -120

    def _draw_engine(self, canvas, x, y):
        """Draw steam engine. x=leftmost point, y=bottom of body."""
        c = TRAIN_COLOUR
        # Engine body
        graphics.DrawLine(canvas, x, y, x + 14, y, c)
        graphics.DrawLine(canvas, x, y - 1, x + 14, y - 1, c)
        graphics.DrawLine(canvas, x + 2, y - 2, x + 14, y - 2, c)
        graphics.DrawLine(canvas, x + 4, y - 3, x + 10, y - 3, c)

        # Chimney
        graphics.DrawLine(canvas, x + 12, y - 3, x + 12, y - 5, c)
        graphics.DrawLine(canvas, x + 13, y - 3, x + 13, y - 5, c)

        # Cab (rear)
        graphics.DrawLine(canvas, x, y - 2, x + 1, y - 2, c)
        graphics.DrawLine(canvas, x, y - 3, x + 1, y - 3, c)
        graphics.DrawLine(canvas, x, y - 4, x + 1, y - 4, c)

        # Wheels
        for wx in (x + 2, x + 6, x + 10, x + 13):
            canvas.SetPixel(wx, y + 1, c.red, c.green, c.blue)

    def _draw_car(self, canvas, x, y, width, text, text_colour):
        """Draw a rail car with text inside. x=leftmost point, y=bottom of body."""
        c = TRAIN_COLOUR
        # Car body outline
        graphics.DrawLine(canvas, x, y - CAR_HEIGHT + 1, x + width, y - CAR_HEIGHT + 1, c)
        graphics.DrawLine(canvas, x, y, x + width, y, c)
        graphics.DrawLine(canvas, x, y - CAR_HEIGHT + 1, x, y, c)
        graphics.DrawLine(canvas, x + width, y - CAR_HEIGHT + 1, x + width, y, c)

        # Text inside car
        graphics.DrawText(canvas, fonts.extrasmall, x + CAR_PAD, y - 1, text_colour, text)

        # Wheels
        canvas.SetPixel(x + 2, y + 1, c.red, c.green, c.blue)
        canvas.SetPixel(x + width - 2, y + 1, c.red, c.green, c.blue)

    @Animator.KeyFrame.add(2)
    def train_idle(self, count):
        if len(self._data) > 0:
            return

        self.canvas.Clear()
        now = datetime.now()

        # Car contents (last car → first car, left to right on screen)
        cars = [
            (self._station_name[:8], colours.AMBER),
            (now.strftime("%a"), colours.AMBER_DIM),
            (now.strftime("%d %b"), colours.AMBER_DIM),
            (now.strftime("%H:%M"), colours.AMBER),
        ]

        # Calculate widths
        car_widths = [len(text) * CHAR_WIDTH + CAR_PAD * 2 for text, _ in cars]
        total_width = ENGINE_WIDTH + sum(w + CAR_GAP for w in car_widths)

        # Track (always visible)
        graphics.DrawLine(
            self.canvas, 0, TRAIN_Y + 2, screen.WIDTH - 1, TRAIN_Y + 2, TRACK_COLOUR
        )

        # Draw cars left to right, then engine at the front (rightmost)
        x = int(self._idle_x)
        for (text, colour), width in zip(cars, car_widths):
            self._draw_car(self.canvas, x, TRAIN_Y, width, text, colour)
            # Coupling connector to next car
            cx = x + width
            graphics.DrawLine(
                self.canvas, cx + 1, TRAIN_Y - 1, cx + CAR_GAP - 1, TRAIN_Y - 1,
                TRAIN_COLOUR,
            )
            x += width + CAR_GAP

        # Engine at the front
        self._draw_engine(self.canvas, x, TRAIN_Y)

        # Smoke puffs above chimney
        smoke_x = x + 12
        s = SMOKE_COLOUR
        puff = count % 4
        self.canvas.SetPixel(smoke_x, TRAIN_Y - 6 - puff, s.red, s.green, s.blue)
        self.canvas.SetPixel(smoke_x + 1, TRAIN_Y - 7 - puff, s.red, s.green, s.blue)

        # Slow scroll
        self._idle_x += 0.5
        if self._idle_x > screen.WIDTH:
            self._idle_x = -total_width

    @Animator.KeyFrame.add(0)
    def reset_idle(self):
        self._idle_x = -120
