from kivy.uix.relativelayout import RelativeLayout


def on_touch_down(self, touch):
    if not self.is_game_over and self.is_game_started:
        if touch.x > self.width / 2:  # right part of de screen, niggah
            self.current_speed_x = self.SPEED_X
        else:
            self.current_speed_x = -self.SPEED_X
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    self.current_speed_x = 0
    pass


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None


def on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0
    return True


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    slide_in_pixels = self.SPEED_X * self.width

    if keycode[1] == 'd':
        self.current_speed_x = -slide_in_pixels
    if keycode[1] == 'a':
        self.current_speed_x = slide_in_pixels
    if keycode[1] == "right":
        self.current_speed_x = -slide_in_pixels
    if keycode[1] == 'left':
        self.current_speed_x = slide_in_pixels
    if keycode[1] == "up":
        self.ship_y_pos += 0.02
    if keycode[1] == "down":
        self.ship_y_pos -= 0.02
    if keycode[1] == "w":
        self.ship_y_pos += 0.02
    if keycode[1] == "s":
        self.ship_y_pos -= 0.02

    return True
