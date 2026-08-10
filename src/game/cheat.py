from pydantic import BaseModel


class Cheat(BaseModel):
    skip_level: bool = False
    invincibility: bool = False
    ghost_freeze: bool = False
    extra_lives: int = 0
    increased_speed: float = 0.0
