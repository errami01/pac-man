import json
import pyray
from .scene import Scene
from .config_parser import Parser
from pathlib import Path
from typing import List, Dict
from .helper import validate_loaded_scores

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

    def _validate_char(self, char: int) -> bool:
        is_space = (char == 32)
        is_numeric = (48 <= char <= 57)
        is_uppercase = (65 <= char <= 90)
        is_lowercase = (97 <= char <= 122)

        return is_space or is_numeric or is_uppercase or is_lowercase

    def _handle_name_input(self):
        char = pyray.get_char_pressed()
        while char > 0:
            if self._validate_char(char) and len(self.player_name) < 10:
                self.player_name += chr(char)
            char = pyray.get_char_pressed()

        if pyray.is_key_pressed(
            pyray.KeyboardKey.KEY_BACKSPACE) and len(self.player_name) > 0:
            self.player_name = self.player_name[:-1]

        if pyray.is_key_pressed(
            pyray.KeyboardKey.KEY_ENTER) and len(self.player_name) >= 3:
            self._save_highscore()
            self.app.go_to_menu()

    def _add_score(self, current_scores: Dict[str, int]) -> Dict[str, int]:
        current_scores = validate_loaded_scores(current_scores)
        scores_list = list(current_scores.items())
        num_scores = len(scores_list)
        pos = 0
        if num_scores == 10 and self.score <= scores_list[num_scores-1][1] :
            return current_scores
        if (self.player_name in current_scores and current_scores[self.player_name] < self.score):
            del current_scores[self.player_name]
            scores_list = list(current_scores.items())
        elif self.player_name in current_scores and current_scores[self.player_name] >= self.score:
            return current_scores
        for item in scores_list:
            if self.score > item[1]:
                break
            pos += 1
        scores_list.insert(pos, (self.player_name, self.score))
        if len(scores_list) > 10:
            scores_list = scores_list[:10]
        
        return dict(scores_list)     

    def _save_highscore(self) -> None:
        highscores_file = Path(self.parser.highscore_filename)
        highscores_file.parent.mkdir(exist_ok=True, parents=True)

        try:
            with open(self.parser.highscore_filename, "r+") as f:
                current_highscores = json.load(f)
                current_highscores = self._add_score(current_highscores)
                f.seek(0)
                json.dump(current_highscores, f, indent=2)
                f.truncate()
            
        except Exception as e:
            if not isinstance(e, FileNotFoundError):
                print(f"Error:\n  {e}")
                print("Creating new highscore file")
            with open(self.parser.highscore_filename, "w") as f:
                json.dump({self.player_name: self.score}, f, indent=2)


