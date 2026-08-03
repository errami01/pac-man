import pyray
from .config_parser import Parser
from .menu import Menu
from .helper import get_resource_path

class MainWindow:
    def __init__(self, config_path: str):
        self.parser = Parser(config_path)
        self.menu = Menu(self, self.parser)
        self.pacman_tex = None

        self.go_to_menu()

    def start(self):
        pyray.init_window(800, 800, "Pac-man")
        pyray.set_target_fps(60)

        self.pacman_tex = pyray.load_texture(get_resource_path("res/pacman.png"))

        while not pyray.window_should_close():
            pyray.begin_drawing()
            pyray.clear_background(pyray.BLACK)

            self.scene.render()

            pyray.end_drawing()

        pyray.close_window()
    
    def go_to_menu(self):
        from .menu import Menu
        self.scene = Menu(self, self.parser)

    def go_to_game(self):
        from .game.game_scene import Game
        self.scene = Game(self, self.parser)
