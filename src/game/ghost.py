from pydantic import BaseModel
from typing import Callable
import pyray

class Ghost(BaseModel):
    x: float
    y: float
    id: int
    current_dir: tuple[int, int] = (0, 0)
    mode: str
    flee: int = 0
    speed: float
    target_x: int = 0
    target_y: int = 0

    def move(self, distances: dict[tuple[int, int], int], dt: float, get_square: Callable, can_move: Callable):
        dx, dy = self.current_dir
    
        step = self.speed * dt
        self.x += dx * step
        self.y += dy * step

        reached = self.current_dir == (0, 0)
        if dx != 0 and ((dx > 0 and self.x >= self.target_x) or (dx < 0 and self.x <= self.target_x)):
            self.x = float(self.target_x)
            reached = True
        if dy != 0 and ((dy > 0 and self.y >= self.target_y) or (dy < 0 and self.y <= self.target_y)):
            self.y = float(self.target_y)
            reached = True

        if reached:
            gx, gy = int(self.x), int(self.y)
            square = get_square(gx, gy)
            if square is None:
                self.current_dir = (0, 0)
                return

            opposite = (-dx, -dy)

            best_dir = (0, 0)
            best_score = None

            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            offset = self.id % len(directions)
            directions = directions[offset:] + directions[:offset]

            for cdx, cdy in directions:
                if (cdx, cdy) == opposite:
                    continue

                if not can_move(square, (cdx, cdy)):
                    continue

                neighbor_square = get_square(gx + cdx, gy + cdy)
                if neighbor_square is None:
                    continue

                dist = distances.get((gx + cdx, gy + cdy))
                if dist is None:
                    continue

                if best_score is None or dist < best_score:
                    best_score = dist
                    best_dir = (cdx, cdy)

            if best_score is None:
                if can_move(square, opposite):
                    best_dir = opposite
                else:
                    best_dir = (0, 0)

            self.current_dir = best_dir
            self.target_x = gx + best_dir[0]
            self.target_y = gy + best_dir[1]

    def random(self):
        pass

    def ambush(self, player_x: float, player_y: float, player_dir: tuple[int, int], reachable_cells: Callable, ahead: int = 3):
        px, py = round(player_x), round(player_y)
        dx, dy = player_dir

        if dx == 0 and dy == 0:
            return (px, py)

        tx, ty = px + dx * ahead, py + dy * ahead

        reachable = reachable_cells(px, py)
        if (tx, ty) in reachable:
            return (tx, ty)

        while (tx, ty) not in reachable and (tx, ty) != (px, py):
            tx -= dx
            ty -= dy

        return (tx, ty)

    def draw(self, offset_x: int, offset_y: int, side_len: int, texture: pyray.Texture):
        center_x = offset_x + self.x * side_len + side_len / 2
        center_y = offset_y + self.y * side_len + side_len / 2

        source_rec = pyray.Rectangle(0, 0, texture.width, texture.height)
        data_rec = pyray.Rectangle(
            int(center_x),
            int(center_y),
            side_len,
            side_len
        )
        origin = pyray.Vector2(side_len / 2, side_len / 2)

        pyray.draw_texture_pro(
            texture,
            source_rec,
            data_rec,
            origin,
            0.0,
            pyray.WHITE
        )
