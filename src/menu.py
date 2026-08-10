import json
from typing import Any, Dict, Union
import pyray
from .config_parser import Parser
from .game.cheat import Cheat
from .helper import validate_loaded_scores
from .scene import Scene


class Menu(Scene):
    """A scene representing the main game menu.

    This scene displays the game title, high scores leaderboard, and listens
    for input to initiate game transitions.
    """

    def __init__(self, app: Any, parser: Parser) -> None:
        """Initializes the main Menu scene.

        Args:
            app: The main application instance governing scene transitions.
            parser (Parser): The configuration parser containing game settings.
        """
        self.app = app
        self.parser = parser
        self.highscores = validate_loaded_scores(self._load_highscores())

    def render(self) -> None:
        """Renders the menu contents and polls for game start commands."""
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_SPACE):
            self.app.go_to_game()
            return

        self._draw_menu()

    def _draw_menu(self) -> None:
        """Loads and draws the Pac-Man title and verified high score
          entries."""

        pyray.draw_text(
            "Pac-Man",
            int((pyray.get_screen_width() - pyray.measure_text(
                "Pac-Man", 60)) / 2),
            80,
            60,
            pyray.YELLOW
        )

        pyray.draw_text(
            "Press SPACE to play",
            int((pyray.get_screen_width() - pyray.measure_text(
                "Press SPACE to play", 20)) / 2),
            140,
            20,
            pyray.RAYWHITE
        )
        pyray.draw_text(
            "How To Play:",
            int((pyray.get_screen_width() - pyray.measure_text(
                "How To Play:", 20)) / 2),
            200,
            20,
            pyray.GOLD
        )
        pyray.draw_text(
            "Navigate the maze, eat all the pacgums, and avoid "
            "the ghosts to survive.",
            int((pyray.get_screen_width() - pyray.measure_text(
                "Navigate the maze, eat all the pacgums, "
                "and avoid the ghosts to survive.", 16)) / 2),
            230,
            16,
            pyray.RAYWHITE
        )
        pyray.draw_text(
            "UP [W]     DOWN [S]    RIGHT[D]    LEFT[A]",
            int((pyray.get_screen_width() - pyray.measure_text(
                "UP [W]     DOWN [S]    RIGHT[D]    LEFT[A]", 16,)) / 2),
            260,
            16,
            pyray.RAYWHITE
        )
        pyray.draw_text(
            "EXIT [ESC]",
            int((pyray.get_screen_width() - pyray.measure_text(
                "EXIT [ESC]", 16)) / 2),
            290,
            16,
            pyray.RAYWHITE
        )

        pyray.draw_text(
            "highscores:",
            int((pyray.get_screen_width() - pyray.measure_text(
                "highscores:", 20)) / 2),
            320,
            20,
            pyray.GOLD
        )

        if len(self.highscores.keys()) == 0:
            pyray.draw_text(
                "no highscores yet",
                int((pyray.get_screen_width() - pyray.measure_text(
                    "no highscores yet", 10)) / 2),
                350,
                10,
                pyray.RAYWHITE
            )
        else:
            i = 1
            for score in self.highscores:
                score_text = f"{i}. {score} - {self.highscores[score]} pts"

                pyray.draw_text(
                    score_text,
                    int((pyray.get_screen_width() - pyray.measure_text(
                        score_text, 20)) / 2),
                    320 + (i * 30),
                    20,
                    pyray.RAYWHITE
                )
                i += 1

    def _load_highscores(self) -> Dict[str, int]:
        """Reads and deserializes high scores from the configuration path.

        Returns:
            Dict[str, int]: A dictionary of player records, or empty on
              failure.
        """
        highscores: Dict[str, int]
        try:
            with open(self.parser.highscore_filename) as f:
                highscores = json.load(f)
                return highscores
        except Exception as e:
            if not isinstance(e, FileNotFoundError):
                print(f"Error:\n  {e}")
            return {}


class PauseMenu(Scene):
    """A scene that interrupts standard gameplay to handle pauses and cheats.

    This menu lets players change cheat attributes such as speed, lives, or
    invincibility through interactive checkboxes and button rows.
    """

    def __init__(self, app: Any, parser: Parser) -> None:
        """Initializes the PauseMenu with default cheat settings.

        Args:
            app: The main application instance governing scene transitions.
            parser (Parser): The configuration parser containing game settings.
        """
        self.app = app
        self.parser = parser
        self.cheats = Cheat()

    def _draw_menu(self) -> None:
        """Renders standard pause text commands along with game cheat logs."""
        pyray.draw_text(
            "Pause",
            int((pyray.get_screen_width() - pyray.measure_text(
                "Pause", 40)) / 2),
            80,
            40,
            pyray.YELLOW
        )
        pyray.draw_text(
            "RESUME [SPACE]",
            int((pyray.get_screen_width() - pyray.measure_text(
                "RESUME [SPACE]", 20)) / 2),
            140,
            20,
            pyray.RAYWHITE
        )
        pyray.draw_text(
            "END GAME [BACKSPACE]",
            int((pyray.get_screen_width() - pyray.measure_text(
                "END GAME [BACKSPACE]", 20)) / 2),
            200,
            20,
            pyray.RAYWHITE
        )

        self._draw_cheats()

    def _draw_cheats(self) -> None:
        """Aligns and executes layout options for game cheat toggles."""
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

    def _draw_checkbox_row(self, x: int, y: int, label_gap: int,
                           label: str, cond: bool) -> bool:
        """Draws an interactive Boolean checkbox element.

        Args:
            x (int): Horizontal draw placement coordinate.
            y (int): Vertical draw placement coordinate.
            label_gap (int): Pixel distance
            between the checkbox and text label.
            label (str): Text identifier for the option row.
            cond (bool): Current toggle state of the option row checkbox.

        Returns:
            bool: The modified or original state conditional.
        """
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
            if pyray.is_mouse_button_pressed(
                    pyray.MouseButton.MOUSE_BUTTON_LEFT):
                cond = not cond

        return cond

    def _draw_number_input(self, x: int, y: int, label_gap: int,
                           label: str, value: Union[int, float]) -> Any:
        """Draws an interactive text container with dynamic adjustment buttons.

        Args:
            x (int): Horizontal draw placement coordinate.
            y (int): Vertical draw placement coordinate.
            label_gap (int): Pixel distance between the widgets and text label.
            label (str): Text identifier for the configuration.
            value (Union[int, float]): Number state variable to be manipulated.

        Returns:
            Any: The updated numeric entry value.
        """
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
        value_x = int(minus_rect.x + 20 + (
            30 - pyray.measure_text(value_text, 15)) / 2)
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
        if (pyray.check_collision_point_rec(mouse_pos, minus_rect)
                and pyray.is_mouse_button_pressed(
                    pyray.MouseButton.MOUSE_BUTTON_LEFT)):
            if isinstance(value, float):
                value = max(0.0, value - 0.5)
            else:
                value = max(0, value - 1)
        if (pyray.check_collision_point_rec(mouse_pos, plus_rect)
                and pyray.is_mouse_button_pressed(
                    pyray.MouseButton.MOUSE_BUTTON_LEFT)):
            if isinstance(value, float):
                value = min(10.0, value + 0.5)
            else:
                value = min(10, value + 1)

        return value

    def render(self) -> None:
        """
        Renders the pause scene UI components and scans for break triggers.
        """
        self._draw_menu()
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_BACKSPACE):
            self.app.scene = Menu(self.app, self.parser)
