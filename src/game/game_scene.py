from ..scene import Scene
from ..config_parser import Parser
from mazegenerator import MazeGenerator
from .ghost import Ghost
from .map import Map, Square
import pyray
import random

class Game(Scene):
    def __init__(self, app, parser: Parser, padding: int = 20):
        self.app = app
        self.parser = parser
        self.map = Map(self._get_maze(), self.parser)
        self.padding = padding

        self.pacman_tex = pyray.load_texture("res/pacman.png")
        self.blinky_tex = pyray.load_texture("res/blinky.png")
        self.pinky_tex = pyray.load_texture("res/pinky.png")
        self.inky_tex = pyray.load_texture("res/inky.png")
        self.clyde_tex = pyray.load_texture("res/clyde.png")

        self.ghost_textures = [self.blinky_tex, self.pinky_tex, self.inky_tex, self.clyde_tex]

        self.player_x = (max(square.x for square in self.map.squares) + 1) // 2
        self.player_y = (max(square.y for square in self.map.squares) + 1) // 2

        self.draw_x = float(self.player_x)
        self.draw_y = float(self.player_y)

        self.progress = 0.0

        self.current_dir = (0, 0)
        self.next_dir = (0, 0)
        self.last_dir = (-1, 0)
        self.speed = 5.0

        self.score = 0
        self.lives = self.parser.lives

        self.ghosts = self._spawn_ghosts()

        for ghost in self.ghosts:
            print(f"Ghost: {ghost.id}, mode: {ghost.mode}")

    def render(self):
        self._handle_input()
        self._move(pyray.get_frame_time())
        self._move_ghosts(pyray.get_frame_time())

        self.map.draw_borders()
        self.map.draw_pacgums()

        self._draw_ghosts()
        self._render_pacman(self.app.pacman_tex)
        self._collect_pacgums()
        self._draw_bottom_hud()

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
        if self.progress == 0.0:
            current = self.map.get_square(self.player_x, self.player_y)
            if current is None:
                return

            if self._can_move(current, self.next_dir):
                self.current_dir = self.next_dir
            elif not self._can_move(current, self.current_dir):
                self.current_dir = (0, 0)

        if self.current_dir == (0, 0):
            self.draw_x, self.draw_y = float(self.player_x), float(self.player_y)
            return

        self.progress += self.speed * dt

        while self.progress >= 1.0:
            self.progress -= 1.0

            dx, dy = self.current_dir
            self.player_x += dx
            self.player_y += dy

            current = self.map.get_square(self.player_x, self.player_y)
            if current is not None:
                if self._can_move(current, self.next_dir):
                    self.current_dir = self.next_dir
                elif not self._can_move(current, self.current_dir):
                    self.current_dir = (0, 0)
                    self.progress = 0.0
                    break

        dx, dy = self.current_dir
        self.draw_x = self.player_x + dx * self.progress
        self.draw_y = self.player_y + dy * self.progress

    def _collect_pacgums(self):
        grid_x, grid_y = self.player_x, self.player_y

        remaining = []
        remaining_super = []
        for gum in self.map.pacgums:
            if gum.square.x == grid_x and gum.square.y == grid_y:
                self.score += self.parser.points_per_pacgum
            else:
                remaining.append(gum)

        for gum in self.map.super_pacgums:
            if gum.square.x == grid_x and gum.square.y == grid_y:
                self.score += self.parser.points_per_super_pacgum
            else:
                remaining_super.append(gum)

        self.map.pacgums = remaining
        self.map.super_pacgums = remaining_super

    def _draw_bottom_hud(self):
        pyray.draw_text(
            f"Score: {self.score}",
            30,
            pyray.get_screen_height() - 20,
            20,
            pyray.RAYWHITE
        )

    def _render_pacman(self, pacman_tex: pyray.Texture):
        side_len, offset_x, offset_y = self.map.get_layout()

        pixel_x = offset_x + self.draw_x * side_len
        pixel_y = offset_y + self.draw_y * side_len

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

    def _spawn_ghosts(self) -> list[Ghost]:
        result = []
        modes = ["chase", "ambush", "scatter", "random"]

        i = 0
        for corner, mode in zip(self.map.get_corners(), modes):
            result.append(Ghost(
                x=corner[0],
                y=corner[1],
                id=i,
                speed=2.5,
                mode=mode
            ))

            i += 1

        return result

    def _distance_map(self, start_x: int, start_y: int) -> dict[tuple[int, int], int]:
        distances = {(start_x, start_y): 0}
        queue = [(start_x, start_y)]

        while queue:
            x, y = queue.pop(0)
            square = self.map.get_square(x, y)
            if square is None:
                continue

            for nx, ny in self.map.get_neighbors(square):
                if (nx, ny) not in distances:
                    distances[(nx, ny)] = distances[(x, y)] + 1
                    queue.append((nx, ny))

        return distances

    def _move_ghosts(self, dt: float):
        distances = self._distance_map(self.player_x, self.player_y)

        for ghost in self.ghosts:
            if ghost.mode == "chase":
                target = (self.player_x, self.player_y)

            elif ghost.mode == "ambush":
                target = ghost.ambush(self.player_x, self.player_y, self.current_dir, self.map.get_reachable_cells)

            elif ghost.mode == "scatter":
                target = self.map.get_corners()[ghost.id]

            else:
                target = random.choice(list(self.map.get_reachable_cells(self.player_x, self.player_y)))

            distances = self._distance_map(*target)
            ghost.move(distances, dt, self.map.get_square, self._can_move)

    def _draw_ghosts(self):
        side_len, offset_x, offset_y = self.map.get_layout()

        for ghost, texture in zip(self.ghosts, self.ghost_textures):
            ghost.draw(offset_x, offset_y, side_len, texture)
