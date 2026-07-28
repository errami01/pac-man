import random
import pyray
from pydantic import BaseModel
from ..config_parser import Parser

class Square(BaseModel):
    north: int
    east: int
    south: int
    west: int
    x: int
    y: int

class Pacgum(BaseModel):
    square: Square

class Map:
    def __init__(self, maze: list[list[int]], parser: Parser):
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

        self.pacgums: list[Pacgum] = self._spawn_pacgums(
            parser.pacgum,
            (max(square.x for square in self.squares) + 1) // 2,
            (max(square.y for square in self.squares) + 1) // 2,
        )
        self.super_pacgums: list[Pacgum] = self._spawn_super_pacgums()

    def draw_borders(self):
        side_len, offset_x, offset_y = self.get_layout()

        for square in self.squares:
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

    def get_layout(self, padding: int = 20):
        cols = max(square.x for square in self.squares) + 1
        rows = max(square.y for square in self.squares) + 1

        side_len = min(
            (pyray.get_screen_width() - (padding * 2)) // cols,
            (pyray.get_screen_height() - (padding * 2)) // rows
        )

        offset_x = (pyray.get_screen_width() - (side_len * cols)) // 2
        offset_y = (pyray.get_screen_height() - (side_len * rows)) // 2

        return side_len, offset_x, offset_y

    def get_square(self, x: int, y: int) -> Square | None:
        for square in self.squares:
            if square.x == x and square.y == y:
                return square

        return None

    def get_corners(self) -> list[tuple[int, int]]:
        cols = max(square.x for square in self.squares) + 1
        rows = max(square.y for square in self.squares) + 1

        return [
            (0, 0),
            (cols - 1, 0),
            (0, rows - 1),
            (cols - 1, rows - 1)
        ]

    def get_reachable_cells(self, start_x: int, start_y: int) -> set[tuple[int, int]]:
        visited: set[tuple[int, int]] = set()
        queue = [(start_x, start_y)]

        while queue:
            x, y = queue.pop()
            if (x, y) in visited:
                continue

            visited.add((x, y))
            square = self.get_square(x, y)
            if square is None:
                continue

            for nx, ny in self.get_neighbors(square):
                if (nx, ny) not in visited:
                    queue.append((nx, ny))

        return visited

    def get_neighbors(self, square: Square) -> list[tuple[int, int]]:
        neighbors = []

        if not square.north:
            neighbors.append((square.x, square.y - 1))
        if not square.south:
            neighbors.append((square.x, square.y + 1))
        if not square.east:
            neighbors.append((square.x + 1, square.y))
        if not square.west:
            neighbors.append((square.x - 1, square.y))

        return neighbors

    def _spawn_pacgums(self, num: int, player_x: int, player_y: int) -> list[Pacgum]:
        reachable = self.get_reachable_cells(player_x, player_y)

        candidates = list((reachable - {(player_x, player_y)}) - set(self.get_corners()))
        count = min(num, len(candidates))

        chosen = random.sample(candidates, count)

        result = []
        for x, y in chosen:
            square = self.get_square(x, y)

            if square is None:
                continue

            result.append(Pacgum(square=square))

        return result

    def _spawn_super_pacgums(self) -> list[Pacgum]:
        result = []

        for corner in self.get_corners():
            square = self.get_square(corner[0], corner[1])

            if square is None:
                continue

            result.append(Pacgum(square=square))

        return result

    def draw_pacgums(self):
        side_len, offset_x, offset_y = self.get_layout()
        radius = side_len * 0.12

        for gum in self.pacgums:
            center_x = offset_x + gum.square.x * side_len + side_len / 2
            center_y = offset_y + gum.square.y * side_len + side_len / 2

            pyray.draw_circle(int(center_x), int(center_y), radius, pyray.GRAY)

        for gum in self.super_pacgums:
            center_x = offset_x + gum.square.x * side_len + side_len / 2
            center_y = offset_y + gum.square.y * side_len + side_len / 2

            pyray.draw_circle(int(center_x), int(center_y), radius, pyray.RAYWHITE)
