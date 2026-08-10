import pyray
from .config_parser import Parser
from .helper import get_resource_path
from .menu import Menu
from .scene import Scene


class MainWindow:
    """Manages the main window lifecycle, game loop, and global resources."""

    def __init__(self, config_path: str) -> None:
        """Initializes game parser settings and navigates to the main menu.

        Args:
            config_path (str): File system path to configuration asset.
        """
        self.parser = Parser(config_path)
        self.menu = Menu(self, self.parser)
        self.pacman_tex: pyray.Texture
        self.scene: Scene

        self.go_to_menu()

    def start(self) -> None:
        """Initializes the window, loads textures, and starts the game loop."""
        pyray.set_config_flags(pyray.ConfigFlags.FLAG_WINDOW_HIGHDPI)
        pyray.init_window(800, 800, "Pac-man")
        pyray.set_target_fps(60)

        self.pacman_tex = pyray.load_texture(
            get_resource_path("res/pacman.png")
        )

        while not pyray.window_should_close():
            pyray.begin_drawing()
            pyray.clear_background(pyray.BLACK)

            self.scene.render()

            pyray.end_drawing()

        pyray.close_window()

    def go_to_menu(self) -> None:
        """Transitions the application state back to the main menu view."""
        from .menu import Menu
        self.scene = Menu(self, self.parser)

    def go_to_game(self) -> None:
        """Transitions application scene state into the active core game."""
        from .game.game_scene import Game
        self.scene = Game(self, self.parser)
