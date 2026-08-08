import json
import pyray
from .scene import Scene
from .config_parser import Parser
from .helper import validate_loaded_scores
from .game.cheat import Cheat


class Menu(Scene):
    def __init__(self, app, parser: Parser):
        self.app = app
        self.parser = parser

    def render(self):
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_SPACE):
            self.app.go_to_game()
            return

        self._draw_menu()

    def _draw_menu(self):
        highscores = self._load_highscores()
        highscores = validate_loaded_scores(highscores)

        pyray.draw_text(
            "Pac-Man",
            int((pyray.get_screen_width() - pyray.measure_text("Pac-Man", 40)) / 2),
            80,
            40,
            pyray.YELLOW
        )

        pyray.draw_text(
            "Press SPACE to play",
            int((pyray.get_screen_width() - pyray.measure_text("Press SPACE to play", 20)) / 2),
            140,
            20,
            pyray.RAYWHITE
        )

        pyray.draw_text(
            "highscores:",
            int((pyray.get_screen_width() - pyray.measure_text("highscores:", 20)) / 2),
            200,
            20,
            pyray.RAYWHITE
        )

        if len(highscores.keys()) == 0:
            pyray.draw_text(
                "no highscores yet",
                int((pyray.get_screen_width() - pyray.measure_text("no highscores yet", 10)) / 2),
                250,
                10,
                pyray.RAYWHITE
            )
        else:
            i = 1
            for score in highscores:
                score_text = f"{i}. {score} - {highscores[score]} pts"

                pyray.draw_text(
                        score_text,
                        int((pyray.get_screen_width() - pyray.measure_text(score_text, 20)) / 2),
                        270 + (i * 20),
                        20,
                        pyray.RAYWHITE
                )
                i += 1

    def _load_highscores(self) -> dict:
        try:
            with open(self.parser.highscore_filename) as f:
                return json.load(f)
        except Exception as e:
            if not isinstance(e, FileNotFoundError):
                print(f"Error:\n  {e}")
            return {}


class PauseMenu(Scene):
    def __init__(self, app, parser: Parser):
        self.app = app
        self.parser = parser
        self.cheats = Cheat()

    def _draw_menu(self):
        pyray.draw_text(
            "Pause",
            int((pyray.get_screen_width() - pyray.measure_text("Pause", 40)) / 2),
            80,
            40,
            pyray.YELLOW
        )
        pyray.draw_text(
            "RESUME [SPACE]",
            int((pyray.get_screen_width() - pyray.measure_text("RESUME [SPACE]", 20)) / 2),
            140,
            20,
            pyray.RAYWHITE
        )
        pyray.draw_text(
            "END GAME [BACKSPACE]",
            int((pyray.get_screen_width() - pyray.measure_text("END GAME [BACKSPACE]", 20)) / 2),
            200,
            20,
            pyray.RAYWHITE
        )

        self._draw_cheats()

    def _draw_cheats(self):
        row_height = 22
        checkbox_label_gap = 10
        start_y = 250

        max_label_width = pyray.measure_text("Increase speed", 15)

        x = int((pyray.get_screen_width() - 30 - max_label_width) / 2)

        self.cheats.invincibility = self._draw_checkbox_row(
            x, start_y, checkbox_label_gap,
            "Invincibility", self.cheats.invincibility
        )
        self.cheats.ghost_freeze = self._draw_checkbox_row(
            x, start_y + row_height, checkbox_label_gap,
            "Ghost freeze", self.cheats.ghost_freeze
        )
        self.cheats.extra_lives = self._draw_number_input(
            x, start_y + row_height * 2, checkbox_label_gap,
            "Extra lives", self.cheats.extra_lives
        )

        self.cheats.increased_speed = self._draw_number_input(
            x, start_y + row_height * 3, checkbox_label_gap,
            "Increase speed", self.cheats.increased_speed
        )

    def _draw_checkbox_row(self, x: int, y: int, label_gap: int, label: str, cond: bool) -> bool:
        pyray.draw_text(label, x + 20 + label_gap, y + 2, 15, pyray.RAYWHITE)

        checkbox = pyray.Rectangle(x, y, 20, 20)
        pyray.draw_rectangle_lines(
                int(checkbox.x),
                int(checkbox.y),
                int(checkbox.width),
                int(checkbox.height),
                pyray.RAYWHITE
        )

        if cond:
            pyray.draw_rectangle(
                x + 4,
                y + 4,
                12,
                12,
                pyray.YELLOW
            )

        mouse_pos = pyray.get_mouse_position()
        if pyray.check_collision_point_rec(mouse_pos, checkbox):
            if pyray.is_mouse_button_pressed(pyray.MouseButton.MOUSE_BUTTON_LEFT):
                cond = not cond

        return cond

    def _draw_number_input(self, x: int, y: int, label_gap: int, label: str, value: int) -> int:
        pyray.draw_text(label, x + label_gap + 20, y + 2, 15, pyray.RAYWHITE)

        controls_x = x + label_gap + 140

        minus_rect = pyray.Rectangle(controls_x, y, 20, 20)
        plus_rect = pyray.Rectangle(controls_x + 50, y, 20, 20)

        pyray.draw_rectangle_lines(
                int(minus_rect.x),
                int(minus_rect.y),
                20,
                20,
                pyray.RAYWHITE
        )

        pyray.draw_text(
                "-",
                int(minus_rect.x + 7),
                int(minus_rect.y + 2),
                15,
                pyray.RAYWHITE
        )

        value_text = str(value)
        value_x = int(minus_rect.x + 20 + (30 - pyray.measure_text(value_text, 15)) / 2)
        pyray.draw_text(value_text, value_x, y + 2, 15, pyray.YELLOW)

        pyray.draw_rectangle_lines(
                int(plus_rect.x),
                int(plus_rect.y),
                20,
                20,
                pyray.RAYWHITE
        )
        pyray.draw_text(
                "+",
                int(plus_rect.x + 7),
                int(plus_rect.y + 2),
                15,
                pyray.RAYWHITE
        )

        mouse_pos = pyray.get_mouse_position()
        if pyray.check_collision_point_rec(mouse_pos, minus_rect) and pyray.is_mouse_button_pressed(pyray.MouseButton.MOUSE_BUTTON_LEFT):
            if isinstance(value, float):
                value = max(0.0, value - 0.5)
            else:
                value = max(0, value - 1)
        if pyray.check_collision_point_rec(mouse_pos, plus_rect) and pyray.is_mouse_button_pressed(pyray.MouseButton.MOUSE_BUTTON_LEFT):
            if isinstance(value, float):
                value = min(10.0, value + 0.5)
            else:
                value = min(10, value + 1)

        return value

    def render(self):
        self._draw_menu()
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_BACKSPACE):
            self.app.scene = Menu(self.app, self.parser)
