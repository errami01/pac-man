from abc import ABC


class Scene(ABC):
    def render(self) -> None:
        ...
