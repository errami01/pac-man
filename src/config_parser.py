import json
import re
from .helper import get_resource_path

class Parser:
    # Load your configuration safely
    def __init__(self, path: str):
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
        self.points_per_pacgum = self._validate_inputs("points_per_pacgum", 10)
        self.points_per_super_pacgum = self._validate_inputs("points_per_super_pacgum", 50)
        self.points_per_ghost = self._validate_inputs("points_per_ghost", 200)
        self.seed = self._validate_inputs("seed", 42)
        self.level_max_time = self._validate_inputs("level_max_time", 90)

    def _load_commented_json(self, filepath):
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Remove # comments and C++ style // comments
        content = re.sub(r'(?m)^[ \t]*([#]|//).*$', '', content)
        
        # Remove C-style /* */ multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Parse the cleaned string as standard JSON
        return json.loads(content)

    def _validate_highscore_filename(self) -> str:
        file_name = "highscore.json"
        if ("highscore_filename" in self.content and 
            len(self.content["highscore_filename"])):
            arr = self.content["highscore_filename"].split(".")
            if len(arr) > 1 and arr[-1] == "json":
                file_name = self.content["highscore_filename"]
            else:
                file_name = f"{self.content["highscore_filename"]}.json"
        return file_name

    def _validate_inputs(self, prop: str, default_value: int) -> int:
        if (prop in self.content
            and isinstance(self.content[prop], int)
            and not isinstance(self.content[prop], bool)
            and self.content[prop] > 0
            and self.content[prop] <= 999):
            return self.content[prop]
        return default_value

