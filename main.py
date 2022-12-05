import random

from kivy import Config, platform

Config.set("graphics", "width", "1200")
Config.set("graphics", "height", "500")

from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Line, Color, Ellipse, Bezier, Quad
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget


class MainWidget(Widget):
    from user_interactions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up
    from transform import transform_perspective, transform, transform_2D

    V_LINES_AMOUNT = 4  # should be even
    V_LINES_SPACING = 0.12
    vertical_lines = []

    H_LINES_AMOUNT = 10
    H_LINES_SPACING = 0.12
    horizontal_lines = []

    current_offset_y = 0
    SPEED = 1

    current_offset_x = 0
    SPEED_X = 2.5
    current_speed_x = 0

    tiles = []
    QUAD_AMOUNT = 8
    current_loop = 0
    tiles_coordinates = []

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_tiles()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.tile_coord_generator()
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

    def tile_coord_generator(self):
        for i in range(self.QUAD_AMOUNT):
            self.tiles_coordinates.append((0, i))

    def x_line_coord(self, index):
        spacing = self.width * self.V_LINES_SPACING
        central_line_x = int(self.width / 2)
        offset = index - 0.5
        x_line = central_line_x + offset * spacing + self.current_offset_x
        return x_line

    def y_line_coord(self, index):
        spacing = self.height * self.H_LINES_SPACING
        y_line = index * spacing - self.current_offset_y
        return y_line

    def get_tile_coord(self, ti_x, ti_y):
        ti_y -= self.current_loop
        x = self.x_line_coord(ti_x)
        y = self.y_line_coord(ti_y)
        return x, y

    def clear_tile(self):
        for i in range(len(self.tiles_coordinates)-1):
            if self.tiles_coordinates[i][1] < self.current_loop-1:
                del self.tiles_coordinates[i]
                print("foo")

    def create_tile(self):
        # seed patterns:
        # -1 -> left
        # 0  -> middle
        # 1  -> right
        seed = random.randint(-1, 1)
        x_last, y_last = self.tiles_coordinates[-1]

        if seed != 0:
            x_last += seed
            self.tiles_coordinates.append((x_last, y_last))
            y_last += 1
            self.tiles_coordinates.append((x_last, y_last))
        else:
            self.tiles_coordinates.append((x_last, y_last + 1))


    def update_tile(self):
        for i in range(len(self.tiles_coordinates)):
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
        time_factor = dt * 60

        self.current_offset_y += self.SPEED * time_factor
        self.current_offset_x += self.current_speed_x * time_factor

        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y > spacing_y:
            self.current_offset_y -= spacing_y
            self.current_loop += 1
            # self.clear_tile()
            # self.create_tile()


class DeGameApp(App):
    pass


DeGameApp().run()
