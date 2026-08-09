import json
import re
from .helper import get_resource_path
from typing import Dict


class Parser:
    """A parser to load, clean, and validate configuration files.

    Attributes:
        content (dict): The parsed JSON configuration data.
        highscore_filename (str): The validated highscore filename.
        lives (int): The validated number of player lives.
        pacgum (int): The validated number of pacgums.
        points_per_pacgum (int): Points awarded per pacgum.
        points_per_super_pacgum (int): Points awarded per super pacgum.
        points_per_ghost (int): Points awarded per ghost eaten.
        seed (int): The random seed for level generation.
        level_max_time (int): The maximum time allowed for a level.
    """

    def __init__(self, path: str):
        """Initialize the parser and validate all configuration inputs.

        Args:
            path (str): The relative path to the configuration file.
        """
        config_path = get_resource_path(path)
        try:
            self.content = self._load_commented_json(config_path)
        except Exception as e:
            print(f"Error loading config.json:\n {e}")
            print("Clamp to default values")
            self.content = {}

        self.highscore_filename = self._validate_highscore_filename()
        self.lives = self._validate_inputs("lives", 3)
        self.pacgum = self._validate_inputs("pacgum", 42)
        self.points_per_pacgum = self._validate_inputs(
            "points_per_pacgum", 10
        )
        self.points_per_super_pacgum = self._validate_inputs(
            "points_per_super_pacgum", 50
        )
        self.points_per_ghost = self._validate_inputs(
            "points_per_ghost", 200
        )
        self.seed = self._validate_inputs("seed", 42)
        self.level_max_time = self._validate_inputs("level_max_time", 90)

    def _load_commented_json(self, filepath: str) -> Dict:
        """Load a JSON file while stripping out single and multi-line
          comments.

        Args:
            filepath (str): The absolute path to the file.

        Returns:
            dict: The parsed JSON content as a dictionary.
        """
        rst: Dict
        with open(filepath, "r") as file:
            content = file.read()

        # Remove # comments and C++ style // comments
        content = re.sub(r"(?m)^[ \t]*([#]|//).*$", "", content)

        # Remove C-style /* */ multi-line comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        # Parse the cleaned string as standard JSON
        rst = json.loads(content)
        return rst

    def _validate_highscore_filename(self) -> str:
        """Validate the highscore filename and ensure it has a .json
          extension.

        Returns:
            str: The verified filename, defaulting to 'highscore.json'.
        """
        file_name = "highscore.json"
        if (
            "highscore_filename" in self.content
            and len(self.content["highscore_filename"])
        ):
            name = self.content["highscore_filename"]
            arr = name.split(".")
            if len(arr) > 1 and arr[-1] == "json":
                file_name = name
            else:
                file_name = f"{name}.json"
        return file_name

    def _validate_inputs(self, prop: str, default_value: int) -> int:
        """Validate that a configuration property is an integer between 1 and
          999.

        Args:
            prop (str): The key name of the property to check.
            default_value (int): The fallback value if validation fails.

        Returns:
            int: The validated property value or the default value.
        """
        if (
            prop in self.content
            and isinstance(self.content[prop], int)
            and not isinstance(self.content[prop], bool)
            and 0 < self.content[prop] <= 999
        ):
            return int(self.content[prop])
        return default_value
