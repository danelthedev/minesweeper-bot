from PIL import ImageGrab, Image, ImageDraw
import numpy as np


class BoardProcessor:

    def __init__(self, cell_size=52):
        self.cell_size = cell_size

        self.columns = 0
        self.rows = 0
        self.game_grid = [[]]
        self.corners = []

        self.flag_positions = []


    def initialize_board(self):
        # Extract the two corners
        top_left = self.corners[0]
        bottom_right = self.corners[1]

        exact_corner_color = [(112, 120, 128), (30, 38, 46)]

        img = ImageGrab.grab()

        ok = False
        for i in range(self.cell_size):
            for j in range(self.cell_size):
                print(top_left[0] - i, top_left[1])
                if img.getpixel((top_left[0] - i, top_left[1])) in exact_corner_color and img.getpixel(
                        (top_left[0], top_left[1] - j)) in exact_corner_color:
                    top_left = (top_left[0] - i - 4, top_left[1] - j - 4)
                    print(f'Top left corner: {top_left}')
                    ok = True
                    break
            if ok:
                break

        ok = False
        for i in range(self.cell_size):
            for j in range(self.cell_size):
                if img.getpixel((bottom_right[0] - i, bottom_right[1])) in exact_corner_color and img.getpixel(
                        (bottom_right[0], bottom_right[1] - j)) in exact_corner_color:
                    bottom_right = (bottom_right[0] - i, bottom_right[1] - j)
                    print(f'Bottom right corner: {bottom_right}')
                    ok = True
                    break
            if ok:
                break

        # Calculate the dimensions based on corners
        width = bottom_right[0] - top_left[0]
        height = bottom_right[1] - top_left[1]

        self.columns = width // self.cell_size + 1
        self.rows = height // self.cell_size + 1
        self.game_grid = [[None for _ in range(self.columns)] for _ in range(self.rows)]

        self.corners = [top_left, bottom_right]


    def update_game_board(self):
        top_left = self.corners[0]
        bottom_right = self.corners[1]

        # Capture the screen and get colors for the Minesweeper grid
        bbox = (top_left[0], top_left[1], top_left[0] + (self.columns * self.cell_size), top_left[1] + (self.rows * self.cell_size))
        img = ImageGrab.grab(bbox)

        for row in range(self.rows):
            for col in range(self.columns):
                # Calculate the pixel position for the current cell in the screenshot
                pixel_x = col * self.cell_size + self.cell_size // 2
                pixel_y = row * self.cell_size + self.cell_size // 2

                whitelisted_colors = [(124, 199, 255), (102, 194, 102), (255, 119, 136), (238, 136, 255),
                                      (221, 170, 34), (102, 204, 204), (153, 153, 153), (208, 216, 224)]
                unclicked_color = (76, 84, 92)
                empty_tile_color = (56, 64, 72)
                bomb_color = (0, 0, 0)

                # Get the pixel color of the current cell and the nearest pixels and average them
                nonbackground_pixels = 0
                pixel_color = np.array([0, 0, 0])
                for i in range(10):
                    for j in range(10):
                        if img.getpixel((pixel_x + i, pixel_y + j)) == bomb_color:
                            return False

                        if img.getpixel((pixel_x + i,
                                         pixel_y + j)) in whitelisted_colors:  # Avoid the specific background color
                            nonbackground_pixels += 1
                            pixel_color += np.array(img.getpixel((pixel_x + i, pixel_y + j)))
                        if img.getpixel((pixel_x + i, pixel_y + j)) == unclicked_color:
                            nonbackground_pixels = -1
                            self.game_grid[row][col] = None
                            break

                if nonbackground_pixels > 0:
                    pixel_color = tuple(pixel_color // nonbackground_pixels)
                    self.game_grid[row][col] = whitelisted_colors.index(tuple(pixel_color)) + 1
                elif nonbackground_pixels == 0:
                    self.game_grid[row][col] = 0

        for flag in self.flag_positions:
            self.game_grid[flag[0]][flag[1]] = -1

        return True

    def cleanup(self):
        self.columns = 0
        self.rows = 0
        self.game_grid = [[]]

        self.running = True

        self.flag_positions = []
