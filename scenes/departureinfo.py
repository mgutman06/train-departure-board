from utilities.animator import Animator
from setup import colours, fonts, screen

from rgbmatrix import graphics

# Layout
INFO_Y = 21
INFO_FONT = fonts.small
INDEX_FONT = fonts.extrasmall
INDEX_Y = 21

BAR_Y = 14
BAR_PADDING = 2


class DepartureInfoScene(object):
    def __init__(self):
        super().__init__()

    @Animator.KeyFrame.add(0)
    def departure_info(self):
        if len(self._data) == 0:
            return

        dep = self._data[self._data_index]
        time_text = dep["scheduled"]
        platform = dep["platform"]
        status = dep["status"]
        cancelled = dep["cancelled"]

        # Clear the info area
        self.draw_square(0, BAR_Y, screen.WIDTH, INFO_Y + 1, colours.BLACK)

        # Draw dividing bar
        graphics.DrawLine(
            self.canvas, 0, BAR_Y, screen.WIDTH - 1, BAR_Y, colours.DIVIDER_COLOUR
        )

        # Draw departure time
        x_pos = 1
        time_length = graphics.DrawText(
            self.canvas, INFO_FONT, x_pos, INFO_Y, colours.TIME_COLOUR, time_text
        )
        x_pos += time_length + 2

        # Draw platform if available
        if platform:
            plt_text = f"P{platform}"
            plt_length = graphics.DrawText(
                self.canvas, INFO_FONT, x_pos, INFO_Y, colours.PLATFORM_COLOUR, plt_text
            )
            x_pos += plt_length + 2

        # Draw status (right-aligned area)
        if cancelled:
            status_colour = colours.STATUS_CANCELLED
        elif status == "On time":
            status_colour = colours.STATUS_ON_TIME
        else:
            status_colour = colours.STATUS_DELAYED

        # Calculate status position to fit on the right
        # If there are multiple services, show index too
        if len(self._data) > 1:
            index_text = f"{self._data_index + 1}/{len(self._data)}"
            # Draw index at far right
            index_x = screen.WIDTH - (len(index_text) * 4) - 1
            graphics.DrawText(
                self.canvas, INDEX_FONT, index_x, INFO_Y, colours.INDEX_COLOUR, index_text
            )
            # Draw status between platform and index
            status_x = max(x_pos, index_x - (len(status) * 5) - 2)
            graphics.DrawText(
                self.canvas, INDEX_FONT, status_x, INFO_Y, status_colour, status
            )
        else:
            # Just draw status after platform
            graphics.DrawText(
                self.canvas, INDEX_FONT, x_pos, INFO_Y, status_colour, status
            )
