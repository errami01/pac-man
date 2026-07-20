import json

class Parser:
    def __init__(self, path: str):
        with open(path) as f:
            self.content = json.load(f)

        self.highscore_filename = self.content["highscore_filename"] if "highscore_filename" in self.content else "highscore.json"
        self.lives = self.content["lives"] if "lives" in self.content else 3
        self.pacgum = self.content["pacgum"] if "pacgum" in self.content else 42
        self.points_per_pacgum = self.content["points_per_pacgum"] if "points_per_pacgum" in self.content else 10
        self.points_per_super_pacgum = self.content["points_per_super_pacgum"] if "poitns_per_super_pacgum" in self.content else 50
        self.points_per_ghost = self.content["points_per_ghost"] if "points_per_ghost" in self.content else 200
        self.seed = self.content["seed"] if "seed" in self.content else 42
        self.level_max_time = self.content["level_max_time"] if "level_max_time" in self.content else 90
