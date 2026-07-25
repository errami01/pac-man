import json
import pyray
from .scene import Scene
from .game.game_scene import Game
from .config_parser import Parser

class Menu(Scene):
    def __init__(self, app, parser: Parser):
        self.app = app
        self.parser = parser

    def render(self):
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_SPACE):
            self.app.scene = Game(self.app, self.parser)
            return

        self._draw_menu()

    def _draw_menu(self):
        highscores = self._load_highscores()

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
                        int((pyray.get_screen_width() - pyray.measure_text(score_text, 10)) / 2),
                        270 + i * 10,
                        10,
                        pyray.RAYWHITE
                )

    def _load_highscores(self) -> dict:
        try:
            with open(self.parser.highscore_filename) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
