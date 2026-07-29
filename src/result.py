import json
import pyray
from .scene import Scene
from .config_parser import Parser
from pathlib import Path

class Result(Scene):
    def __init__(self, app, parser: Parser, win: bool, score: int):
        self.app = app
        self.parser = parser
        self.win = win 
        self.score = score
        self.player_name = ""

    def render(self):
        if self.win:
            pyray.draw_text(
                "Congratulations",
                int((pyray.get_screen_width() - pyray.measure_text("Congratulations", 40)) / 2),
                80,
                40,
                pyray.YELLOW
            )

        else:
            pyray.draw_text(
                "Game Over",
                int((pyray.get_screen_width() - pyray.measure_text("Game Over", 40)) / 2),
                80,
                40,
                pyray.YELLOW
            )

        pyray.draw_text(
                f"Score: {self.score}",
                int((pyray.get_screen_width() - pyray.measure_text(f"Score: {self.score}", 20)) / 2),
                160,
                20,
                pyray.RAYWHITE
        )

        pyray.draw_text(
            "Enter your name:",
            int((pyray.get_screen_width() - pyray.measure_text("Enter your name:", 20)) / 2),
            int(pyray.get_screen_height() / 2) - 40,
            20,
            pyray.RAYWHITE
        )

        pyray.draw_text(
            f"{self.player_name}_",
            int((pyray.get_screen_width() - pyray.measure_text(f"{self.player_name}_", 30)) / 2),
            int(pyray.get_screen_height() / 2),
            30,
            pyray.YELLOW
        )

        self._handle_name_input()

    def _handle_name_input(self):
        char = pyray.get_char_pressed()

        while char > 0:
            if 32 <= char <= 125 and len(self.player_name) < 20:
                self.player_name += chr(char)
            char = pyray.get_char_pressed()

        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_BACKSPACE) and len(self.player_name) > 0:
            self.player_name = self.player_name[:-1]

        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_ENTER) and len(self.player_name) >= 3:
            self._save_highscore()
            self.app.go_to_menu()

    def _save_highscore(self):
        highscores_file = Path(self.parser.highscore_filename)
        highscores_file.parent.mkdir(exist_ok=True, parents=True)

        try:
            with open(self.parser.highscore_filename, "r+") as f:
                current_highscores = json.load(f)
                current_highscores[self.player_name] = self.score
                f.seek(0)
                json.dump(current_highscores, f, indent=2)
        except FileNotFoundError:
            with open(self.parser.highscore_filename, "w") as f:
                json.dump({self.player_name: self.score}, f, indent=2)
