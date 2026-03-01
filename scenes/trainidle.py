from datetime import datetime

from setup.rgbcompat import graphics

from utilities.animator import Animator
from setup import colours, fonts, screen

# Layout
TRAIN_Y = 23
CAR_HEIGHT = 10
CAR_PAD = 2
CAR_GAP = 3
CHAR_WIDTH = 4
ENGINE_WIDTH = 18

# -- Engine colours --
BOILER_COLOUR = graphics.Color(50, 55, 60)
CAB_COLOUR = graphics.Color(175, 30, 30)
CAB_ROOF_COLOUR = graphics.Color(45, 45, 50)
CHIMNEY_COLOUR = graphics.Color(40, 40, 45)
DOME_COLOUR = graphics.Color(185, 165, 50)
HEADLAMP_COLOUR = graphics.Color(255, 255, 180)

# -- Car body colours (one per car for variety) --
CAR_BODY_COLOURS = [
    graphics.Color(10, 90, 60),      # British racing green
    graphics.Color(135, 25, 25),     # LMS crimson / maroon
    graphics.Color(30, 50, 135),     # Royal blue
    graphics.Color(130, 55, 20),     # Chocolate brown
]
CAR_STRIPE_COLOUR = graphics.Color(200, 180, 100)
CAR_ROOF_COLOUR = graphics.Color(50, 50, 55)
WINDOW_COLOUR = graphics.Color(95, 165, 215)

# -- Wheels & track --
WHEEL_COLOUR = graphics.Color(175, 175, 185)
WHEEL_HUB_COLOUR = graphics.Color(110, 110, 120)
TRACK_COLOUR = graphics.Color(100, 100, 110)
TIE_COLOUR = graphics.Color(75, 45, 20)

# -- Coupling & smoke --
COUPLING_COLOUR = graphics.Color(115, 115, 125)
SMOKE_COLOUR = colours.GREY
SMOKE_COLOUR_DIM = graphics.Color(70, 70, 75)


class TrainIdleScene(object):
    def __init__(self):
        super().__init__()
        self._idle_x = -140

    def _draw_wheel(self, canvas, cx, cy):
        """Draw a 3x3 diamond-shaped wheel centred on (cx, cy)."""
        c = WHEEL_COLOUR
        canvas.SetPixel(cx, cy - 1, c.red, c.green, c.blue)
        canvas.SetPixel(cx - 1, cy, c.red, c.green, c.blue)
        canvas.SetPixel(cx + 1, cy, c.red, c.green, c.blue)
        canvas.SetPixel(cx, cy + 1, c.red, c.green, c.blue)
        h = WHEEL_HUB_COLOUR
        canvas.SetPixel(cx, cy, h.red, h.green, h.blue)

    def _draw_engine(self, canvas, x, y):
        """Draw a detailed steam locomotive. x = left edge, y = body bottom."""
        bc = BOILER_COLOUR
        cc = CAB_COLOUR

        # Boiler (main cylinder)
        for row in range(0, 7):
            graphics.DrawLine(canvas, x + 2, y - row, x + 14, y - row, bc)
        graphics.DrawLine(canvas, x + 3, y - 7, x + 13, y - 7, bc)
        graphics.DrawLine(canvas, x + 4, y - 8, x + 12, y - 8, bc)

        # Cab (rear, taller — overwrites left portion of boiler)
        for row in range(0, 10):
            graphics.DrawLine(canvas, x, y - row, x + 3, y - row, cc)

        # Cab roof
        cr = CAB_ROOF_COLOUR
        graphics.DrawLine(canvas, x - 1, y - 10, x + 4, y - 10, cr)
        graphics.DrawLine(canvas, x, y - 11, x + 3, y - 11, cr)

        # Cab window
        wc = WINDOW_COLOUR
        canvas.SetPixel(x + 1, y - 7, wc.red, wc.green, wc.blue)
        canvas.SetPixel(x + 2, y - 7, wc.red, wc.green, wc.blue)
        canvas.SetPixel(x + 1, y - 8, wc.red, wc.green, wc.blue)
        canvas.SetPixel(x + 2, y - 8, wc.red, wc.green, wc.blue)

        # Chimney
        ch = CHIMNEY_COLOUR
        graphics.DrawLine(canvas, x + 13, y - 8, x + 13, y - 12, ch)
        graphics.DrawLine(canvas, x + 14, y - 8, x + 14, y - 12, ch)
        graphics.DrawLine(canvas, x + 12, y - 13, x + 15, y - 13, ch)

        # Steam dome (brass)
        dc = DOME_COLOUR
        canvas.SetPixel(x + 8, y - 9, dc.red, dc.green, dc.blue)
        canvas.SetPixel(x + 9, y - 9, dc.red, dc.green, dc.blue)
        canvas.SetPixel(x + 8, y - 10, dc.red, dc.green, dc.blue)
        canvas.SetPixel(x + 9, y - 10, dc.red, dc.green, dc.blue)

        # Front / cow-catcher
        graphics.DrawLine(canvas, x + 14, y, x + 16, y, bc)
        graphics.DrawLine(canvas, x + 15, y - 1, x + 16, y - 1, bc)

        # Headlamp
        hl = HEADLAMP_COLOUR
        canvas.SetPixel(x + 17, y - 2, hl.red, hl.green, hl.blue)

        # Wheels (3x3 diamonds)
        for wx in (x + 3, x + 7, x + 11, x + 16):
            self._draw_wheel(canvas, wx, y + 2)

    def _draw_car(self, canvas, x, y, width, text, text_colour, body_colour):
        """Draw a passenger car with roof, windows, stripe and wheels."""
        bc = body_colour

        # Car body (filled)
        for row in range(0, CAR_HEIGHT):
            graphics.DrawLine(canvas, x, y - row, x + width, y - row, bc)

        # Roof overhang (above body, extends 1 px each side)
        rc = CAR_ROOF_COLOUR
        graphics.DrawLine(canvas, x - 1, y - CAR_HEIGHT, x + width + 1, y - CAR_HEIGHT, rc)
        graphics.DrawLine(canvas, x, y - CAR_HEIGHT + 1, x + width, y - CAR_HEIGHT + 1, rc)

        # Cream / gold lining stripe
        sc = CAR_STRIPE_COLOUR
        graphics.DrawLine(canvas, x + 1, y - 5, x + width - 1, y - 5, sc)

        # Windows (2x2 blocks with gaps)
        wc = WINDOW_COLOUR
        for wx in range(x + 2, x + width - 2, 3):
            canvas.SetPixel(wx, y - 7, wc.red, wc.green, wc.blue)
            canvas.SetPixel(wx + 1, y - 7, wc.red, wc.green, wc.blue)
            canvas.SetPixel(wx, y - 8, wc.red, wc.green, wc.blue)
            canvas.SetPixel(wx + 1, y - 8, wc.red, wc.green, wc.blue)

        # Text label inside lower portion
        graphics.DrawText(canvas, fonts.extrasmall, x + CAR_PAD, y - 1, text_colour, text)

        # Wheels (3x3 diamonds)
        self._draw_wheel(canvas, x + 3, y + 2)
        self._draw_wheel(canvas, x + width - 3, y + 2)

    @Animator.KeyFrame.add(2)
    def train_idle(self, count):
        if len(self._data) > 0:
            return

        self.canvas.Clear()
        now = datetime.now()

        # Car contents (left to right on screen)
        cars = [
            (self._station_name[:8], colours.AMBER),
            (now.strftime("%a"), colours.AMBER_DIM),
            (now.strftime("%d %b"), colours.AMBER_DIM),
            (now.strftime("%H:%M"), colours.AMBER),
        ]

        # Calculate widths
        car_widths = [len(text) * CHAR_WIDTH + CAR_PAD * 2 for text, _ in cars]
        total_width = ENGINE_WIDTH + sum(w + CAR_GAP for w in car_widths)

        # Sleepers (wooden ties beneath rail)
        tc = TIE_COLOUR
        for tx in range(0, screen.WIDTH, 5):
            self.canvas.SetPixel(tx, TRAIN_Y + 4, tc.red, tc.green, tc.blue)
            self.canvas.SetPixel(tx + 1, TRAIN_Y + 4, tc.red, tc.green, tc.blue)

        # Rail
        graphics.DrawLine(
            self.canvas, 0, TRAIN_Y + 3, screen.WIDTH - 1, TRAIN_Y + 3, TRACK_COLOUR
        )

        # Draw cars left to right, then engine at front (rightmost)
        x = int(self._idle_x)
        for i, ((text, colour), width) in enumerate(zip(cars, car_widths)):
            body_colour = CAR_BODY_COLOURS[i % len(CAR_BODY_COLOURS)]
            self._draw_car(self.canvas, x, TRAIN_Y, width, text, colour, body_colour)
            # Coupling connector
            cx = x + width
            graphics.DrawLine(
                self.canvas, cx + 1, TRAIN_Y - 1, cx + CAR_GAP - 1, TRAIN_Y - 1,
                COUPLING_COLOUR,
            )
            graphics.DrawLine(
                self.canvas, cx + 1, TRAIN_Y, cx + CAR_GAP - 1, TRAIN_Y,
                COUPLING_COLOUR,
            )
            x += width + CAR_GAP

        # Engine at the front
        self._draw_engine(self.canvas, x, TRAIN_Y)

        # Smoke puffs above chimney
        smoke_x = x + 13
        s = SMOKE_COLOUR
        sd = SMOKE_COLOUR_DIM
        puff = count % 4
        self.canvas.SetPixel(smoke_x, TRAIN_Y - 14 - puff, s.red, s.green, s.blue)
        self.canvas.SetPixel(smoke_x + 1, TRAIN_Y - 15 - puff, s.red, s.green, s.blue)
        trail = (count + 2) % 4
        self.canvas.SetPixel(smoke_x - 1, TRAIN_Y - 16 - trail, sd.red, sd.green, sd.blue)

        # Slow scroll
        self._idle_x += 0.5
        if self._idle_x > screen.WIDTH:
            self._idle_x = -total_width

    @Animator.KeyFrame.add(0)
    def reset_idle(self):
        self._idle_x = -140
