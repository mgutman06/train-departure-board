from rgbmatrix import graphics

from utilities.animator import Animator
from setup import colours, fonts, screen

# Layout
CALLING_Y = 30
CALLING_FONT = fonts.regular
CALLING_TEXT_HEIGHT = 9
CALLING_COLOUR = colours.CALLING_POINTS_COLOUR
OPERATOR_COLOUR = colours.OPERATOR_COLOUR


class CallingPointsScene(object):
    def __init__(self):
        super().__init__()
        self._scroll_x = screen.WIDTH
        self._data_all_looped = False

    @Animator.KeyFrame.add(1)
    def calling_points(self, count):
        if len(self._data) == 0:
            return

        dep = self._data[self._data_index]
        calling = dep.get("calling_points", [])
        operator = dep.get("operator", "")

        # Build scrolling text
        if calling:
            scroll_text = "From: " + ", ".join(calling)
        elif operator:
            scroll_text = operator
        else:
            scroll_text = dep["destination"]

        # Clear the calling points area
        self.draw_square(
            0,
            CALLING_Y - CALLING_TEXT_HEIGHT,
            screen.WIDTH,
            screen.HEIGHT,
            colours.BLACK,
        )

        # Draw scrolling text
        text_length = graphics.DrawText(
            self.canvas,
            CALLING_FONT,
            self._scroll_x,
            CALLING_Y,
            CALLING_COLOUR if calling else OPERATOR_COLOUR,
            scroll_text,
        )

        # Advance scroll position
        self._scroll_x -= 1

        # When text has fully scrolled off screen, advance to next departure
        if self._scroll_x + text_length < 0:
            self._scroll_x = screen.WIDTH
            if len(self._data) > 1:
                self._data_index = (self._data_index + 1) % len(self._data)
                self._data_all_looped = (not self._data_index) or self._data_all_looped
                self.reset_scene()

    @Animator.KeyFrame.add(0)
    def reset_scrolling(self):
        self._scroll_x = screen.WIDTH
