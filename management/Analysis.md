# Project Analysis & Technical Choices

- **Library Choice (Pyray)**: Selected for its similarity to the MLX library (C-based wrapper) and robust documentation. It allows for high-performance 2D rendering while remaining Pythonic.

- **Data Format (JSON)**: Used for configuration and highscores because it meets the requirement for "JSON with comments" (using a custom parser) and is easily editable by users.
- **Architecture**: We chose a Scene Management pattern. This allows for clean transitions between the Main Menu, Game, and Game Over screens without memory leaks.
- **External Integration**: The A-Maze-ing package was wrapped in a dedicated MapLoader class to decouple our game logic from the specific group's implementation, allowing us to swap it easily if their package broke.

# Risk Analysis & Mitigation

| Risk	| Impact	| Likelihood	| Mitigation Strategy
| :--- | :--- | :--- | :--- |
| **Incompatible Maze Generator**	| High	| Medium	| Created an adapter class to standardize the maze data format regardless of the assigned package.|
| **PyInstaller Path Errors**	| High	| High	| Implemented the resource_path() helper function early to handle bundled vs. dev paths.
| **Library Version Conflicts**	| Medium	| Low	| Used a requirements.txt and recommended venv usage to team members.|
| **Performance (Python Lag)**	| Medium	| Low	| Optimized the ghost "chase" logic to run only every 5 frames instead of every frame.