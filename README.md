*This project has been created as part of the 42 curriculum by msturma and aberrami.*
# Pac-Man: Ghosts! More Ghosts!

# Description
This project is a complete, playable Pac-Man clone built in Python 3.10+. The goal is to navigate a procedurally generated maze, collect all "pacgums," and avoid four unique ghosts. The project emphasizes object-oriented programming, robust error handling (no tracebacks), and a modular architecture. It features a persistent highscore system, multiple levels with time limits, and a dedicated cheat mode for evaluation.

# Instructions
## Installation
Ensure you have Python 3.10 or later installed. This project uses pyray (Raylib) for graphics.
```bash
# Using the Makefile
make install
```
## Execution
The program requires exactly one argument: a JSON configuration file.
```bash
# Run via Python
python3 pac-man.py config.json

# Or using the Makefile
make run
```
## Packaging
To generate the standalone executable for distribution (Itch.io):
```bash
pyinstaller --noconfirm --onefile --windowed --add-data "config.json:." --add-data "res:res" pac-man.py
```
The resulting binary can be found in the dist/ folder.

The game can be downloaded from itcho.io:
```
https://pacman42t.itch.io/pac-man/download/9fZGgnroMADOwwvMDw27hFkORFN6W7tRUrjn1ssb
```

# Resources
- Graphics: Raylib (pyray) - Used as the MLX-equivalent graphical library.
- Coding Standards: PEP 257 for docstrings and Flake8 for linting.
- AI Usage: AI was used for:
    - Assisting with the resource_path logic for PyInstaller to ensure assets load correctly in the bundled executable.
    - Debugging complex state transitions within the Scene manager.
    - Generating the initial boilerplate for the highscore JSON structure.

# Configuration
The game is configured via config.json. The parser supports standard JSON plus comments (lines starting with #).

Key Parameters:
- lives: Number of starting lives (Default: 3).
- level_max_time: Time limit per level in seconds (Default: 90).
- points_per_pacgum: Score per small dot (Default: 10).
- seed: Fixed seed for the first level's maze generation.
- highscore_filename: Path to the persistent score file.

# Highscore
The highscore system is stored in a JSON file (highscores.json).
- Implementation: We chose JSON for its human-readability and ease of persistence. The system loads the Top 10 scores at startup and saves them immediately when a game ends.
- Robustness: The system handles missing files and invalid formats by reverting to an empty list rather than crashing, as per Section V.5.
- Constraints: Player names are limited to 10 alphanumeric characters.

# Maze Generation
This project integrates the A-Maze-ing package assigned to us:
- Usage: Our Map class adapts to the external package's interface.
- Configuration: We explicitly set PERFECT = False to ensure the generator creates loops and corridors suitable for a Pac-Man layout.
- Resilience: If the generator fails to produce a maze, the game logs a clear error message and safely returns to the menu.

# Implementation
The game is built on a State Machine logic.
- Core Engine: Uses pyray for a 60-FPS game loop.
- Level Timing: Implemented a Timer class that tracks remaining time and triggers a "Level Failed" state if it reaches zero.
- Input Handling: Supports both WASD and Arrow keys.
- Cheat Mode: Features toggles for Invincibility (K), Level Skip (L), and Ghost Freeze (F) to assist peer reviewers.

# General Software Architecture
The project follows a modular, object-oriented approach:
- pac-man.py: The entry point and command-line argument parser.
- src/main_window.py: Orchestrates the Raylib window lifecycle.
- src/scene.py & src/menu.py: Handles different game states (Main Menu, In-Game, Game Over, Victory).
- src/game/:
    - map.py: Draw the map using the external maze generator.
    - ghost.py & pacman.py: Entity logic (AI chase behaviors and player movement).
    - timer.py: Precision timing for level progression.
- config_parser.py: Custom logic to handle JSON with # comments.
```
PAC-MAN
└── 📁src
    └── 📁game
        ├── game_scene.py
        ├── ghost.py
        ├── map.py
        ├── timer.py
    ├── __init__.py
    ├── config_parser.py
    ├── helper.py
    ├── main_window.py
    ├── menu.py
    ├── result.py
    └── scene.py
└── 📁res
    ├── pacman.png
    ├── ...
└── config.json
└── pac-man.py
```

# Project Management
We used a structured approach to drive development:
- msturma: Focus on Game Engine, rendering pipeline, and Cheat Mode implementation.
- aberrami: Focus on Quality Assurance (Flake8/Mypy), Documentation (PEP 257), Pause/Timer systems, Highscore logic, and Packaging for Itch.io.

More about project management, including a project timeline and risk analysis, can be found in the [PROJECT_MANAGEMENT_DIRECTORY](./management)


<!--https://pngimg.com/image/73648
https://www.pngmart.com/image/14728 -->
