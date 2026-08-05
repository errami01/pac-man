import json
import pyray
from .scene import Scene
from .config_parser import Parser
from .helper import validate_loaded_scores

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

    def render(self):
        self._draw_menu()
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_BACKSPACE):
            self.app.scene = Menu(self.app, self.parser)
