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

    @Animator.KeyFrame.add(0)
    def destination(self):
        if len(self._data) == 0:
            return

        origin = self._data[self._data_index]["origin"]

        # Clear the destination area
        self.draw_square(0, 0, screen.WIDTH, DESTINATION_Y + 1, colours.BLACK)

        # Draw origin station name (where train is coming from)
        _ = graphics.DrawText(
            self.canvas,
            DESTINATION_FONT,
            1,
            DESTINATION_Y,
            DESTINATION_COLOUR,
            origin if origin else "Unknown",
        )
