from rgbmatrix import graphics
import random
from setup import colours, screen
from utilities.animator import Animator

# Setup
PLANE_COLOUR = colours.BLUE
COCKPIT_COLOUR = colours.PINK
SUN_COLOUR = colours.YELLOW
CLOUD_COLOUR = colours.WHITE

def draw_filled_circle(canvas, cx, cy, radius, colour):
    """Approximate a filled circle by drawing horizontal lines inside the radius."""
    for dy in range(-radius, radius + 1):
        dx = int((radius**2 - dy**2) ** 0.5)  # circle equation x^2 + y^2 = r^2
        graphics.DrawLine(canvas, cx - dx, cy + dy, cx + dx, cy + dy, colour)

class PlaneIdleScene(object):
    def __init__(self):
        super().__init__()
        self.plane_x = -20  # start offscreen
        self.clouds = [
            {"x": random.randint(0, screen.WIDTH), "y": random.randint(5, 20)}
            for _ in range(3)
        ]

    def draw_plane(self, canvas, x, y):
        # Fuselage
        graphics.DrawLine(canvas, x, y, x+13, y, PLANE_COLOUR)
        graphics.DrawLine(canvas, x, y-1, x+13, y-1, PLANE_COLOUR)

        # Tail
        graphics.DrawLine(canvas, x, y-2, x+2, y-2, PLANE_COLOUR)

        # Wing
        graphics.DrawLine(canvas, x+5, y-3, x+8, y-3, PLANE_COLOUR)
        graphics.DrawLine(canvas, x+5, y+1, x+8, y+1, PLANE_COLOUR)

        # Cockpit
        graphics.DrawLine(canvas, x+12, y-1, x+13, y-1, COCKPIT_COLOUR)
        graphics.DrawLine(canvas, x+12, y, x+13, y, COCKPIT_COLOUR)

    def draw_sun(self, canvas):
        # Smaller filled sun
        draw_filled_circle(canvas, screen.WIDTH-8, 8, 3, SUN_COLOUR)

    def draw_cloud(self, canvas, x, y):
        # Cloud made of overlapping filled circles
        draw_filled_circle(canvas, x, y, 3, CLOUD_COLOUR)
        draw_filled_circle(canvas, x+4, y+1, 3, CLOUD_COLOUR)
        draw_filled_circle(canvas, x-4, y+1, 3, CLOUD_COLOUR)

    @Animator.KeyFrame.add(2)  # slow down animation (was 1)
    def animate(self, count):
        if len(self._data) > 0:
           return
        # Clear screen
        self.canvas.Clear()

        # Draw sun
        self.draw_sun(self.canvas)

        # Draw clouds
        for cloud in self.clouds:
            self.draw_cloud(self.canvas, cloud["x"], cloud["y"])
            cloud["x"] -= 1
            if cloud["x"] < -8:  # wrap around
                cloud["x"] = screen.WIDTH + 8
                cloud["y"] = random.randint(5, 20)

        # Draw airplane
        self.draw_plane(self.canvas, self.plane_x, 20)
        self.plane_x += 1  # slower movement (can change to += 0.5 if needed)
        if self.plane_x > screen.WIDTH + 20:
            self.plane_x = -20
