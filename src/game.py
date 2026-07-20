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
    def __init__(self, app, parser: Parser, side_len: int = 30):
        self.app = app
        self.parser = parser
        self.map = Map(self._get_maze())
        self.side_len = side_len

    def render(self):
        self._draw_borders()

    def _draw_borders(self):
        for square in self.map.squares:
            if square.north:
                pyray.draw_line(
                    square.x * self.side_len,
                    square.y * self.side_len,
                    (square.x * self.side_len) + self.side_len,
                    square.y * self.side_len,
                    pyray.RAYWHITE
                )

            if square.south:
                pyray.draw_line(
                    square.x * self.side_len,
                    (square.y * self.side_len) + self.side_len,
                    (square.x * self.side_len) + self.side_len,
                    (square.y * self.side_len) + self.side_len,
                    pyray.RAYWHITE
                )

            if square.west:
                pyray.draw_line(
                    square.x * self.side_len,
                    square.y * self.side_len,
                    square.x * self.side_len,
                    (square.y * self.side_len) + self.side_len,
                    pyray.RAYWHITE
                )

            if square.east:
                pyray.draw_line(
                    (square.x * self.side_len) + self.side_len,
                    square.y * self.side_len,
                    (square.x * self.side_len) + self.side_len,
                    (square.y * self.side_len) + self.side_len,
                    pyray.RAYWHITE
                )

    def _get_maze(self):
        generator = MazeGenerator(
            seed=self.parser.seed
        )

        return generator.maze

