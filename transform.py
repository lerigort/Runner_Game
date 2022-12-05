def transform(self, x, y):
    # return self.transform_2D(x, y)
    return self.transform_perspective(x, y)


def transform_2D(self, x, y):
    return x, y


def transform_perspective(self, x, y):
    lin_y = y * self.coord_perspective_y / self.height
    if lin_y > self.coord_perspective_y:
        lin_y = self.coord_perspective_y

    diff_y = self.coord_perspective_y - lin_y
    diff_x = x - self.coord_perspective_x

    modif_y = diff_y / self.coord_perspective_y
    modif_y = pow(modif_y, 1)

    per_x = self.coord_perspective_x + diff_x * modif_y
    per_y = self.coord_perspective_y - modif_y * self.coord_perspective_y

    return per_x, per_y
