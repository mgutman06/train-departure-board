from rgbmatrix import graphics

from utilities.animator import Animator
from setup import colours, fonts, screen

# Layout
DESTINATION_Y = 12
DESTINATION_FONT = fonts.large
DESTINATION_COLOUR = colours.DESTINATION_COLOUR


class DestinationScene(object):
    def __init__(self):
        super().__init__()
        self._origin_scroll_x = 1
        self._origin_needs_scroll = False

    @Animator.KeyFrame.add(0)
    def destination(self):
        if len(self._data) == 0:
            return

        origin = self._data[self._data_index].get("origin", "") or "Unknown"

        # Clear the destination area
        self.draw_square(0, 0, screen.WIDTH, DESTINATION_Y + 1, colours.BLACK)

        # Draw origin station name
        text_width = graphics.DrawText(
            self.canvas,
            DESTINATION_FONT,
            1,
            DESTINATION_Y,
            DESTINATION_COLOUR,
            origin,
        )

        # Check if scrolling is needed
        self._origin_needs_scroll = text_width > screen.WIDTH - 2
        self._origin_scroll_x = 1

    @Animator.KeyFrame.add(1)
    def scroll_origin(self, count):
        if len(self._data) == 0:
            return
        if not self._origin_needs_scroll:
            return

        origin = self._data[self._data_index].get("origin", "") or "Unknown"

        # Advance scroll position (1px per frame = 10px/s at 10fps)
        self._origin_scroll_x -= 1

        # Clear the destination area
        self.draw_square(0, 0, screen.WIDTH, DESTINATION_Y + 1, colours.BLACK)

        # Draw at scroll position
        text_width = graphics.DrawText(
            self.canvas,
            DESTINATION_FONT,
            self._origin_scroll_x,
            DESTINATION_Y,
            DESTINATION_COLOUR,
            origin,
        )

        # Reset when text has fully scrolled off left edge
        if self._origin_scroll_x + text_width < 0:
            self._origin_scroll_x = screen.WIDTH
