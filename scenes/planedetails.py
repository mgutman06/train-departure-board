from rgbmatrix import graphics

from utilities.animator import Animator
from setup import colours, fonts, screen

# Setup
PLANE_DETAILS_COLOUR = colours.PINK
PLANE_DISTANCE_FROM_TOP = 30
PLANE_TEXT_HEIGHT = 9
PLANE_FONT = fonts.regular
ALTITUDE_COLOUR = colours.YELLOW
ALTITUDE_TEXT_HEIGHT = 7

class PlaneDetailsScene(object):
    def __init__(self):
        super().__init__()
        self.plane_position = screen.WIDTH
        self._data_all_looped = False

    @Animator.KeyFrame.add(1)
    def plane_details(self, count):

        # Guard against no data
        if len(self._data) == 0:
            return

        plane = f'{self._data[self._data_index]["plane"]}'
        # Convert Alt to ft and round
        altitude_km = self._data[self._data_index].get("altitude")
        if altitude_km is not None:
            altitude_ft = int(round(float(altitude_km), -2))
            altitude_text = f" ALT: {altitude_ft:,}ft"
        else:
            altitude_text = ""

        details_text = plane + altitude_text

        # Draw background
        self.draw_square(
            0,
            PLANE_DISTANCE_FROM_TOP - PLANE_TEXT_HEIGHT,
            screen.WIDTH,
            screen.HEIGHT,
            colours.BLACK,
        )

        # Draw text
        plane_text_length = graphics.DrawText(
            self.canvas,
            PLANE_FONT,
            self.plane_position,
            PLANE_DISTANCE_FROM_TOP,
            PLANE_DETAILS_COLOUR,
            plane,
        ) if plane else 0

        # Draw altitude immediately after plane text (yellow)
        alt_text_length = graphics.DrawText(
            self.canvas,
            PLANE_FONT,
            self.plane_position + plane_text_length,
            PLANE_DISTANCE_FROM_TOP,
            ALTITUDE_COLOUR,
            altitude_text,
        )

        # Total length of scrolling text (both parts)
        total_length = plane_text_length + alt_text_length

        # Handle scrolling
        self.plane_position -= 1
        if self.plane_position + total_length < 0:
            self.plane_position = screen.WIDTH
            if len(self._data) > 1:
                self._data_index = (self._data_index + 1) % len(self._data)
                self._data_all_looped = (not self._data_index) or self._data_all_looped
                self.reset_scene()

    @Animator.KeyFrame.add(0)
    def reset_scrolling(self):
        self.plane_position = screen.WIDTH
