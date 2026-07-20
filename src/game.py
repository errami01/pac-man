from .scene import Scene
from .config_parser import Parser
from mazegenerator import MazeGenerator
from pydantic import BaseModel
import pyray

class Square(BaseModel):
    north: int
    east: int
    south: int
    west: int
    x: int
    y: int

class Map:
    def __init__(self, maze: list[list[int]]):
        self.squares: list[Square] = []

        for y in range(len(maze)):
            for x in range(len(maze[y])):
                bin = format(maze[y][x], "04b")

                self.squares.append(Square(
                    north=int(bin[3]),
                    east=int(bin[2]),
                    south=int(bin[1]),
                    west=int(bin[0]),
                    x=x,
                    y=y
                ))

class Game(Scene):
    def __init__(self, app, parser: Parser, padding: int = 20):
        self.app = app
        self.parser = parser
        self.map = Map(self._get_maze())
        self.padding = padding

    def render(self):
        self._draw_borders()
        self._render_pacman(self.app.pacman_tex)

    def _layout(self):
        cols = max(square.x for square in self.map.squares) + 1
        rows = max(square.y for square in self.map.squares) + 1

        side_len = min(
            (pyray.get_screen_width() - (self.padding * 2)) // cols,
            (pyray.get_screen_height() - (self.padding * 2)) // rows
        )

        offset_x = (pyray.get_screen_width() - (side_len * cols)) // 2
        offset_y = (pyray.get_screen_height() - (side_len * rows)) // 2

        return side_len, offset_x, offset_y

    def _draw_borders(self):
        side_len, offset_x, offset_y = self._layout()

        for square in self.map.squares:
            x = offset_x + square.x * side_len
            y = offset_y + square.y * side_len

            if square.north:
                pyray.draw_line(x, y, x + side_len, y, pyray.RAYWHITE)

            if square.south:
                pyray.draw_line(x, y + side_len, x + side_len, y + side_len, pyray.RAYWHITE)

            if square.west:
                pyray.draw_line(x, y, x, y + side_len, pyray.RAYWHITE)

            if square.east:
                pyray.draw_line(x + side_len, y, x + side_len, y + side_len, pyray.RAYWHITE)

            if square.north and square.south and square.east and square.west:
                pyray.draw_rectangle(
                    x,
                    y,
                    side_len,
                    side_len,
                    pyray.YELLOW
                )

    def _render_pacman(self, pacman_tex: pyray.Texture):
        side_len, offset_x, offset_y = self._layout()
        cols = max(square.x for square in self.map.squares) + 1
        rows = max(square.y for square in self.map.squares) + 1

        pixel_x = offset_x + (cols // 2) * side_len
        pixel_y = offset_y + (rows // 2) * side_len

        scale = side_len / pacman_tex.width

        pyray.draw_texture_ex(pacman_tex, (pixel_x, pixel_y), 0.0, scale, pyray.WHITE)

        if pyray.is_key_down(pyray.KeyboardKey.KEY_W):
            self._move(pacman_tex, "up")

    def _move(self, pacman_tex: pyray.Texture, direction: str):
        pass

    def _get_maze(self):
        generator = MazeGenerator(
            seed=self.parser.seed
        )

        return generator.maze

