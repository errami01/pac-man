from ..result import Result
from ..scene import Scene
from ..config_parser import Parser
from mazegenerator import MazeGenerator
from .ghost import Ghost
from .map import Map, Square
import pyray
import random
from ..menu import PauseMenu
from .timer import GameTimer
from ..helper import get_resource_path
from .cheat import Cheat


class Game(Scene):
    def __init__(self, app, parser: Parser, padding: int = 20):
        self.app = app
        self.parser = parser
        self.map = Map(self._get_maze(self.parser.seed), self.parser)
        self.padding = padding

        self.pacman_tex = pyray.load_texture(get_resource_path("res/pacman.png"))
        self.blinky_tex = pyray.load_texture(get_resource_path("res/blinky.png"))
        self.pinky_tex = pyray.load_texture(get_resource_path("res/pinky.png"))
        self.inky_tex = pyray.load_texture(get_resource_path("res/inky.png"))
        self.clyde_tex = pyray.load_texture(get_resource_path("res/clyde.png"))
        self.fright_tex = pyray.load_texture(get_resource_path("res/fright.png"))

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
        self.flee_timer = 0.0

        self.pause_menu = PauseMenu(self.app, parser)
        self.level_count = 1
        self.game_state: str = "RUNNING"
        self.game_timer = GameTimer(self.parser.level_max_time)

    def render(self):
        self._update_game_state()
        if self.game_state == "RUNNING":
            self._handle_input()
            self._move(pyray.get_frame_time())
            self._tick_flee_timer(pyray.get_frame_time())
            self._tick_ghost_respawn(pyray.get_frame_time())
            self._move_ghosts(pyray.get_frame_time())
            self._handle_ghost_collision()
            self.map.draw_borders()
            self.map.draw_pacgums()

            self._draw_ghosts()
            self._render_pacman(self.app.pacman_tex)
            self._collect_pacgums()
            self._draw_bottom_hud()
            self.game_timer.update()
            if self.game_timer.is_finished:
                self._end(False)
        else:
            self.pause_menu.render()

    def _handle_input(self):
        if pyray.is_key_down(pyray.KeyboardKey.KEY_W):
            self.next_dir = (0, -1)
        elif pyray.is_key_down(pyray.KeyboardKey.KEY_S):
            self.next_dir = (0, 1)
        elif pyray.is_key_down(pyray.KeyboardKey.KEY_A):
            self.next_dir = (-1, 0)
        elif pyray.is_key_down(pyray.KeyboardKey.KEY_D):
            self.next_dir = (1, 0)

    def _update_game_state(self):
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_SPACE):
            if self.game_state == "RUNNING":
                self.game_state = "PAUSE"
            else:
                self._update_cheats()
                self.game_state = "RUNNING"

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

    def _tick_flee_timer(self, dt: float):
        if self.flee_timer <= 0:
            return

        self.flee_timer = max(0.0, self.flee_timer - dt)

        if self.flee_timer == 0:
            for ghost in self.ghosts:
                ghost.flee = 0

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
                self.flee_timer = 10.0
                for ghost in self.ghosts:
                    ghost.flee = 1
            else:
                remaining_super.append(gum)

        self.map.pacgums = remaining
        self.map.super_pacgums = remaining_super

        if len(self.map.pacgums) == 0 and len(self.map.super_pacgums) == 0:
            if self.level_count == 3:
                self._end(True)

            self._generate_new_level()
            self.level_count += 1

    def _draw_bottom_hud(self):
        pyray.draw_text(
            f"Score: {self.score}",
            30,
            pyray.get_screen_height() - 20,
            20,
            pyray.RAYWHITE
        )

        if self.pause_menu.cheats.invincibility:
            pyray.draw_text(
                "Lives: ∞",
                160,
                pyray.get_screen_height() - 20,
                20,
                pyray.RAYWHITE
            )
        else:
            pyray.draw_text(
                f"Lives: {self.lives}",
                160,
                pyray.get_screen_height() - 20,
                20,
                pyray.RAYWHITE
            )

        pyray.draw_text(
            f"Time: {self.game_timer.time_left:.0f}",
            290,
            pyray.get_screen_height() - 20,
            20,
            pyray.RAYWHITE
        )
        pyray.draw_text(
            f"Level: {self.level_count}",
            420,
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

    def _get_maze(self, seed: int):
        generator = MazeGenerator(
            seed=seed
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
                home_x=corner[0],
                home_y=corner[1],
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
            if ghost.flee == 0:
                if ghost.mode == "chase":
                    target = (self.player_x, self.player_y)

                elif ghost.mode == "ambush":
                    target = ghost.ambush(self.player_x, self.player_y, self.current_dir, self.map.get_reachable_cells)

                elif ghost.mode == "scatter":
                    target = self.map.get_corners()[ghost.id]

                else:
                    target = random.choice(list(self.map.get_reachable_cells(self.player_x, self.player_y)))
            else:
                target = max(distances.items(), key=lambda x: x[1])[0]

            distances = self._distance_map(*target)
            ghost.move(distances, dt, self.map.get_square, self._can_move)

    def _draw_ghosts(self):
        side_len, offset_x, offset_y = self.map.get_layout()

        for ghost, texture in zip(self.ghosts, self.ghost_textures):
            if ghost.eaten:
                continue

            if ghost.flee == 0:
                ghost.draw(offset_x, offset_y, side_len, texture)
            else:
                ghost.draw(offset_x, offset_y, side_len, self.fright_tex)

    def _handle_ghost_collision(self):
        if self.pause_menu.cheats.invincibility:
            return

        for ghost in self.ghosts:
            if ghost.eaten:
                continue

            if round(ghost.x) == round(self.draw_x) and round(ghost.y) == round(self.draw_y):
                if ghost.flee == 0:
                    self._handle_player_death()
                else:
                    ghost.eaten = 1
                    ghost.respawn_timer = 5.0
                    ghost.current_dir = (0, 0)
                    self.score += self.parser.points_per_ghost

    def _handle_player_death(self):
        if self.lives == 1:
            self._end(False)

        self.player_x = (max(square.x for square in self.map.squares) + 1) // 2
        self.player_y = (max(square.y for square in self.map.squares) + 1) // 2

        self.draw_x = float(self.player_x)
        self.draw_y = float(self.player_y)

        self.progress = 0.0

        self.current_dir = (0, 0)
        self.next_dir = (0, 0)
        self.last_dir = (-1, 0)
        self.ghosts = self._spawn_ghosts()
        self.lives -= 1

    def _update_cheats(self):
        self.speed += self.pause_menu.cheats.increased_speed
        self.lives += self.pause_menu.cheats.extra_lives

        if self.pause_menu.cheats.ghost_freeze:
            for ghost in self.ghosts:
                ghost.speed = 0.0
        else:
            for ghost in self.ghosts:
                ghost.speed = 2.5

    def _tick_ghost_respawn(self, dt: float):
        for ghost in self.ghosts:
            if not ghost.eaten:
                continue

            ghost.respawn_timer = max(0.0, ghost.respawn_timer - dt)

            if ghost.respawn_timer == 0:
                ghost.x, ghost.y = float(ghost.home_x), float(ghost.home_y)
                ghost.target_x, ghost.target_y = ghost.home_x, ghost.home_y
                ghost.current_dir = (0, 0)
                ghost.eaten = 0
                ghost.flee = 0

    def _generate_new_level(self):
        self.map = Map(self._get_maze(0), self.parser)
        self.player_x = (max(square.x for square in self.map.squares) + 1) // 2
        self.player_y = (max(square.y for square in self.map.squares) + 1) // 2

        self.draw_x = float(self.player_x)
        self.draw_y = float(self.player_y)

        self.progress = 0.0

        self.current_dir = (0, 0)
        self.next_dir = (0, 0)
        self.last_dir = (-1, 0)
        self.ghosts = self._spawn_ghosts()
        self.game_timer.reset()

    def _end(self, win: bool):
        self.app.scene = Result(self.app, self.parser, win, self.score)
