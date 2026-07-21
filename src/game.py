from .scene import Scene
from .config_parser import Parser
from mazegenerator import MazeGenerator
from pydantic import BaseModel
import pyray
import random

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

        self.player_x = float((max(square.x for square in self.map.squares) + 1) // 2)
        self.player_y = float((max(square.y for square in self.map.squares) + 1) // 2)
        self.current_dir = (0, 0)
        self.next_dir = (0, 0)
        self.last_dir = (-1, 0)
        self.speed = 5.0

        self.score = 0
        self.lives = self.parser.lives

        self.pacgums: list[Pacgum] = self._spawn_pacgums()

    def render(self):
        self._handle_input()
        self._move(pyray.get_frame_time())
        self._draw_borders()
        self._draw_pacgums()
        self._render_pacman(self.app.pacman_tex)
        self._collect_pacgums()
        self._draw_bottom_hud()

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

    def _get_square(self, x: int, y: int) -> Square | None:
        for square in self.map.squares:
            if square.x == x and square.y == y:
                return square

        return None

    def _handle_input(self):
        if pyray.is_key_down(pyray.KeyboardKey.KEY_W):
            self.next_dir = (0, -1)
        elif pyray.is_key_down(pyray.KeyboardKey.KEY_S):
            self.next_dir = (0, 1)
        elif pyray.is_key_down(pyray.KeyboardKey.KEY_A):
            self.next_dir = (-1, 0)
        elif pyray.is_key_down(pyray.KeyboardKey.KEY_D):
            self.next_dir = (1, 0)

    def _can_move(self, square: Square, direction: tuple[int, int]) -> bool:
        dx, dy = direction
        if dx == 0 and dy == 0:
            return True

        if dy == -1:
            return not square.north
        if dx == -1:
            return not square.west
        if dy == 1:
            return not square.south
        if dx == 1:
            return not square.east

        return False

    def _move(self, dt: float):
        epsilon = 0.001
        at_center = (
            abs(self.player_x - round(self.player_x)) < epsilon and
            abs(self.player_y - round(self.player_y)) < epsilon
        )

        if at_center:
            grid_x, grid_y = round(self.player_x), round(self.player_y)
            self.player_x, self.player_y = float(grid_x), float(grid_y)
            
            current = self._get_square(grid_x, grid_y)
            if current is None:
                return

            if self._can_move(current, self.next_dir):
                self.current_dir = self.next_dir

            if not self._can_move(current, self.next_dir):
                self.current_dir = (0, 0)

        dx, dy = self.current_dir
        self.player_x += dx * self.speed * dt
        self.player_y += dy * self.speed * dt

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

    def _draw_pacgums(self):
        side_len, offset_x, offset_y = self._layout()
        radius = side_len * 0.12

        for gum in self.pacgums:
            center_x = offset_x + gum.square.x * side_len + side_len / 2
            center_y = offset_y + gum.square.y * side_len + side_len / 2

            pyray.draw_circle(int(center_x), int(center_y), radius, pyray.RAYWHITE)

    def _collect_pacgums(self):
        grid_x, grid_y = round(self.player_x), round(self.player_y)

        remaining = []
        for gum in self.pacgums:
            if gum.square.x == grid_x and gum.square.y == grid_y:
                self.score += self.parser.points_per_pacgum
            else:
                remaining.append(gum)

        self.pacgums = remaining

    def _draw_bottom_hud(self):
        pyray.draw_text(
            f"Score: {self.score}",
            30,
            pyray.get_screen_height() - 20,
            20,
            pyray.RAYWHITE
        )

    def _render_pacman(self, pacman_tex: pyray.Texture):
        side_len, offset_x, offset_y = self._layout()

        pixel_x = offset_x + self.player_x * side_len
        pixel_y = offset_y + self.player_y * side_len

        source_rec = pyray.Rectangle(0, 0, pacman_tex.width, pacman_tex.height)
        dest_rec = pyray.Rectangle(
            pixel_x + side_len // 2,
            pixel_y + side_len // 2,
            side_len,
            side_len
        )
        origin = pyray.Vector2(side_len / 2, side_len / 2)

        pyray.draw_texture_pro(
            pacman_tex,
            source_rec,
            dest_rec,
            origin,
            self._facing_angle(),
            pyray.WHITE
        )


    def _facing_angle(self) -> float:
        angles = {
            (-1, 0): 0.0,
            (0, -1): 90.0,
            (1, 0): 180.0,
            (0, 1): 270.0
        }

        if self.current_dir != (0, 0):
            self.last_dir = self.current_dir

        return angles[self.last_dir]

    def _get_maze(self):
        generator = MazeGenerator(
            seed=self.parser.seed
        )

        return generator.maze

    def _neighbors(self, square: Square) -> list[tuple[int, int]]:
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

    def _reachable_cells(self, start_x: int, start_y: int) -> set[tuple[int, int]]:
        visited: set[tuple[int, int]] = set()
        queue = [(start_x, start_y)]

        while queue:
            x, y = queue.pop()
            if (x, y) in visited:
                continue

            visited.add((x, y))
            square = self._get_square(x, y)
            if square is None:
                continue

            for nx, ny in self._neighbors(square):
                if (nx, ny) not in visited:
                    queue.append((nx, ny))

        return visited

    def _spawn_pacgums(self) -> list[Pacgum]:
        start_x, start_y = round(self.player_x), round(self.player_y)
        reachable = self._reachable_cells(start_x, start_y)

        candidates = list(reachable - {(start_x, start_y)})
        count = min(self.parser.pacgum, len(candidates))

        chosen = random.sample(candidates, count)
        square = (self._get_square(x, y) for x, y in chosen)

        result = []
        for x, y in chosen:
            square = self._get_square(x, y)

            if square is None:
                continue

            result.append(Pacgum(square=square))

        return result
