import pyray
from .config_parser import Parser
from .menu import Menu
from .game import Game

class MainWindow:
    def __init__(self, config_path: str):
        self.parser = Parser(config_path)
        self.menu = Menu(self, self.parser)
        self.game = Game(self, self.parser)
        self.pacman_tex = None

        self.scene = self.game

    def start(self):
        pyray.init_window(800, 800, "Pac-man")
        pyray.set_target_fps(60)

        self.pacman_tex = pyray.load_texture("res/pacman.png")

        while not pyray.window_should_close():
            pyray.begin_drawing()
            pyray.clear_background(pyray.BLACK)

            self.scene.render()

            pyray.end_drawing()

        pyray.close_window()
