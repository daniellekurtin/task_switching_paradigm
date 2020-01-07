from math import ceil


# Create a grid by specifying rectangles to be repeated
class Grid:

    def __init__(self, width_in_cells, height_in_cells, psychopy_rect, start_coords):
        # we would copy this stuff across, but here we do some shorthand hacks
        self.width = width_in_cells
        self.height = height_in_cells
        self.rect = psychopy_rect
        # bump the start coordinates to account for rectangles drawing centred on their start points
        self.start = (start_coords[0] - ceil(self.rect.width * self.width / 2),
                      start_coords[1] - ceil(self.rect.height * self.height / 2))

    # Return the pixel offset of the cell at coordinates r, c
    def coord_to_pixel_offset(self, r, c):
        return (
            self.start[0] + (c * self.rect.width),  # columns increase x offset
            self.start[1] + (r * self.rect.height)  # rows increase y offset
        )

    def draw(self):
        # Iterate through the cells to draw them in the appropriate places
        for r in range(self.width):
            for c in range(self.height):
                # Set grid cell position properties
                rect = self.rect
                rect.pos = self.coord_to_pixel_offset(r, c)

                rect.draw()

    def click_is_in(self, coordinates):
        # Adjust coordinates to account for rects being centred on their offset rather than starting there
        coords = (
            coordinates[0] + ceil(self.rect.width / 2),
            coordinates[1] + ceil(self.rect.height / 2)
        )
        xmin = self.start[0]
        xmax = self.start[0] + self.width * self.rect.width
        ymin = self.start[1]
        ymax = self.start[1] + self.height * self.rect.height

        return xmin <= coords[0] <= xmax and ymin <= coords[1] <= ymax
