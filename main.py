import random

from kivy import Config, platform
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.relativelayout import RelativeLayout

Config.set("graphics", "width", "1200")
Config.set("graphics", "height", "500")

from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Line, Color, Ellipse, Bezier, Quad, Triangle
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from user_interactions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up
    from transform import transform_perspective, transform, transform_2D

    is_game_over = False
    is_game_started = False

    V_LINES_AMOUNT = 12  # should be even
    V_LINES_SPACING = 0.25
    vertical_lines = []

    H_LINES_AMOUNT = 10
    H_LINES_SPACING = 0.12
    horizontal_lines = []

    current_offset_y = 0
    SPEED = 0.3 / 60  # ship constantly travels 50% of screen per second

    current_offset_x = 0
    SPEED_X = 0.7 / 60  # ship can slide up to 70% of screen per second
    current_speed_x = 0

    tiles = []
    QUAD_AMOUNT = 18
    current_loop = 0
    tiles_coordinates = []

    ship = None
    ship_positions = []
    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.043
    ship_y_pos = 0.1

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_tiles()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tile_coord()
        self.init_ship()
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1 / 60)

    def is_desktop(self):
        if platform in ("win", "linux", "macosx"):
            return True
        return False

    def init_vertical_lines(self):
        with self.canvas:
            for i in range(self.V_LINES_AMOUNT):
                self.vertical_lines.append(Line())

    def init_tiles(self):
        with self.canvas:
            for i in range(self.QUAD_AMOUNT):
                self.tiles.append(Quad())

    def init_horizontal_lines(self):
        with self.canvas:
            for i in range(self.H_LINES_AMOUNT):
                self.horizontal_lines.append(Line())

    def init_tile_coord(self):
        for i in range(self.QUAD_AMOUNT):
            self.tiles_coordinates.append((0, i))

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def ship_update(self):
        ship_width_in_pixels = self.width * self.SHIP_WIDTH
        ship_height_in_pixels = self.height * self.SHIP_HEIGHT
        ship_y_pos = self.height * self.ship_y_pos
        center_of_screen = self.width / 2

        x_left_wing_pos = center_of_screen - (ship_width_in_pixels / 2)  # should be slightly to left
        x_right_wing_pos = x_left_wing_pos + ship_width_in_pixels  # slightly to right
        y_wings_pos = ship_y_pos  # same for both wings
        x_nose_pos = center_of_screen
        y_nose_pos = ship_y_pos + ship_height_in_pixels

        self.ship_positions = [(x_left_wing_pos, y_wings_pos), (x_nose_pos, y_nose_pos), (x_right_wing_pos, y_wings_pos)]

        x1, y1 = self.transform(*self.ship_positions[0])
        x2, y2 = self.transform(*self.ship_positions[1])
        x3, y3 = self.transform(*self.ship_positions[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def is_ship_on_track(self) -> bool:
        for i in range(len(self.tiles_coordinates)):
            # if self.tiles_coordinates[i][1] > (self.current_loop+1):  # we need to check collisions only in first 2 rows
                # return False
            if self.is_ship_on_current_tile(self.tiles_coordinates[i]):  # collision "if" matched, we still on track
                return True
        return False

    def is_ship_on_current_tile(self, current_tile_coordinates: tuple) -> bool:
        x_min, y_min = self.get_tile_coord(current_tile_coordinates[0], current_tile_coordinates[1])
        x_max, y_max = self.get_tile_coord(current_tile_coordinates[0] + 1, current_tile_coordinates[1] + 1)

        for i in range(len(self.ship_positions)):
            x_ship_pos, y_ship_pos = self.ship_positions[i]
            if x_min < x_ship_pos < x_max and y_min < y_ship_pos < y_max:
                return True
        return False

    def x_line_coord(self, index) -> float:
        spacing = self.width * self.V_LINES_SPACING
        central_line_x = int(self.width / 2)
        offset = index - 0.5
        x_line = central_line_x + offset * spacing + self.current_offset_x
        return x_line

    def y_line_coord(self, index) -> float:
        spacing = self.height * self.H_LINES_SPACING
        y_line = index * spacing - self.current_offset_y
        return y_line

    def get_tile_coord(self, ti_x, ti_y) -> tuple:
        ti_y -= self.current_loop
        x = self.x_line_coord(ti_x)
        y = self.y_line_coord(ti_y)
        return x, y

    def clear_tile_coord(self):
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_loop:
                del self.tiles_coordinates[i]

    def create_tile_coord(self):
        for i in range(len(self.tiles_coordinates), self.QUAD_AMOUNT):
            # seed patterns:
            # -1 -> left
            # 0  -> middle
            # 1  -> right

            seed = random.randint(-1, 1)
            x_last, y_last = self.tiles_coordinates[-1]

            y_last += 1
            self.tiles_coordinates.append((x_last, y_last))

            if not self.is_seed_in_track(seed):
                seed = -seed

            if seed == -1:
                x_last += 1
                self.tiles_coordinates.append((x_last, y_last))  # append parallel tile
                y_last += 1
                self.tiles_coordinates.append((x_last, y_last))  # append parallel/forward tile

            elif seed == 1:
                x_last -= 1  # mind "-=":  it is the difference between seed -1 and 1
                self.tiles_coordinates.append((x_last, y_last))
                y_last += 1
                self.tiles_coordinates.append((x_last, y_last))

    def is_seed_in_track(self, seed) -> bool:
        start_index = int(-self.V_LINES_AMOUNT / 2 + 1)
        end_index = start_index + self.V_LINES_AMOUNT - 1
        last_x, last_y = self.tiles_coordinates[-1]

        if seed == 1:
            return (last_x + seed) > (end_index - 1)  # -1 because it just works
        else:
            return (last_x + seed) < start_index

    def update_tile(self):
        for i in range(self.QUAD_AMOUNT):
            current_tile_coordinates = self.tiles_coordinates[i]

            xmin, ymin = self.get_tile_coord(current_tile_coordinates[0], current_tile_coordinates[1])
            xmax, ymax = self.get_tile_coord(current_tile_coordinates[0] + 1, current_tile_coordinates[1] + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            self.tiles[i].points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        # -1 0 1 2
        start_index = int(-self.V_LINES_AMOUNT / 2 + 1)
        for index in range(start_index, start_index + self.V_LINES_AMOUNT):
            line_x = self.x_line_coord(index)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[index].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):
        start_index = int(-self.V_LINES_AMOUNT / 2 + 1)
        end_index = start_index + self.V_LINES_AMOUNT - 1

        xmin = self.x_line_coord(start_index)
        xmax = self.x_line_coord(end_index)

        for i in range(self.H_LINES_AMOUNT):
            line_y = self.y_line_coord(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tile()
        self.ship_update()
        if not self.is_ship_on_track() and not self.is_game_over:
            self.is_game_over = True
        time_factor = dt * 60

        if not self.is_game_over and self.is_game_started:
            speed_in_pixels = self.SPEED * self.height
            self.current_offset_y += speed_in_pixels * time_factor
            self.current_offset_x += self.current_speed_x * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y > spacing_y:
                self.current_offset_y -= spacing_y
                self.current_loop += 1
                self.clear_tile_coord()
                self.create_tile_coord()

    def button_clicked(self):
        self.is_game_started = True

class DeGameApp(App):
    pass


DeGameApp().run()
