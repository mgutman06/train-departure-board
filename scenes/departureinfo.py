from utilities.animator import Animator
from setup import colours, fonts, screen

from rgbmatrix import graphics

# Layout
INFO_Y = 21
INFO_FONT = fonts.small
STATUS_FONT = fonts.extrasmall

BAR_Y = 14


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
        mins_until = dep.get("mins_until", "")

        # Clear the info area
        self.draw_square(0, BAR_Y, screen.WIDTH, INFO_Y + 1, colours.BLACK)

        # Draw dividing bar
        graphics.DrawLine(
            self.canvas, 0, BAR_Y, screen.WIDTH - 1, BAR_Y, colours.DIVIDER_COLOUR
        )

        # Draw arrival time
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

        # Determine status display text and colour
        if cancelled:
            status_colour = colours.STATUS_CANCELLED
            display_text = status
        elif mins_until:
            status_colour = colours.STATUS_ON_TIME
            display_text = mins_until
        elif status == "On time":
            status_colour = colours.STATUS_ON_TIME
            display_text = status
        else:
            status_colour = colours.STATUS_DELAYED
            display_text = status

        # Draw status/ETA right-aligned to avoid any overlap
        status_width = len(display_text) * 4  # extrasmall font ~4px per char
        status_x = screen.WIDTH - status_width - 1
        # Ensure status doesn't collide with time/platform
        status_x = max(status_x, x_pos)

        graphics.DrawText(
            self.canvas, STATUS_FONT, status_x, INFO_Y, status_colour, display_text
        )
