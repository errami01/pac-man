import sys
from src.main_window import MainWindow

def main():
    window = MainWindow(sys.argv[1])
    window.start()

if __name__ == "__main__":
    main()
