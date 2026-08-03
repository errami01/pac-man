import sys
import os
from src.main_window import MainWindow

def main():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    # If packed with PyInstaller, fallback to the internal temp directory
    elif getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        config_path = os.path.join(sys._MEIPASS, "config.json")
    # Native script fallback
    else:
        config_path = "config.json"
    window = MainWindow(config_path)
    window.start()

if __name__ == "__main__":
    main()
