from typing import Callable
from pydantic import BaseModel
import pyray


class Ghost(BaseModel):
    """Represent an enemy AI ghost entity in the game loop.

    Attributes:
        x (float): Accurate decimal horizontal map location coordinate.
        y (float): Accurate decimal vertical map location coordinate.
        id (int): Identifier tag applied for custom tracking arrays.
        current_dir (tuple[int, int]): Heading delta step tuple (X, Y).
        mode (str): Active behavioral routing condition tag.
        flee (int): State check flag tracking evasion behavior.
        speed (float): Movement scale adjustment steps per frame tick.
        target_x (int): Horizontal cell marker grid waypoint focus.
        target_y (int): Vertical cell marker grid waypoint focus.
        flee_timer (float): Active remaining seconds for panic status.
        eaten (int): Binary flag for captured, returning-to-base states.
        respawn_timer (float): Active countdown delay before resetting.
        home_x (int): Map center baseline horizontal origin home base.
        home_y (int): Map center baseline vertical origin home base.
    """

    x: float
    y: float
    id: int
    current_dir: tuple[int, int] = (0, 0)
    mode: str
    flee: int = 0
    speed: float
    target_x: int = 0
    target_y: int = 0
    flee_timer: float = 0
    eaten: int = 0
    respawn_timer: float = 0.0
    home_x: int = 0
    home_y: int = 0

    def move(
        self,
        distances: dict[tuple[int, int], int],
        dt: float,
        get_square: Callable,
        can_move: Callable,
    ) -> None:
        """Advance entity locations using target path weight calculations.

        Args:
            distances (dict): Precalculated cell weights to targets.
            dt (float): Elapsed fractional frame duration index.
            get_square (Callable): Spatial tile resolution function.
            can_move (Callable): Directional collision evaluation callback.
        """
        if self.eaten:
            return

        dx, dy = self.current_dir

        step = self.speed * dt
        self.x += dx * step
        self.y += dy * step

        reached = self.current_dir == (0, 0)
        if dx != 0 and (
            (dx > 0 and self.x >= self.target_x)
            or (dx < 0 and self.x <= self.target_x)
        ):
            self.x = float(self.target_x)
            reached = True
        if dy != 0 and (
            (dy > 0 and self.y >= self.target_y)
            or (dy < 0 and self.y <= self.target_y)
        ):
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

    def random(self) -> None:
        """Generate random movement trajectories when routing breaks down."""
        pass

    def ambush(
        self,
        player_x: float,
        player_y: float,
        player_dir: tuple[int, int],
        reachable_cells: Callable,
        ahead: int = 3,
    ) -> tuple[int, int]:
        """Intercept player movement paths by targeting projected ahead
          offsets.

        Args:
            player_x (float): Horizontal target position metric coordinate.
            player_y (float): Vertical target position metric coordinate.
            player_dir (tuple): Directional delta array tracking targets.
            reachable_cells (Callable): Accessible graph lookup filter.
            ahead (int): Total cell offsets projected forward.

        Returns:
            tuple[int, int]: Computed destination target tracking coordinates.
        """
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

    def draw(
        self,
        offset_x: int,
        offset_y: int,
        side_len: int,
        texture: pyray.Texture,
    ) -> None:
        """Render sprite visual sheets onto viewport layouts.

        Args:
            offset_x (int): Horizontal frame window margin alignment.
            offset_y (int): Vertical frame window margin alignment.
            side_len (int): Dimensions of localized tracking grid box sizes.
            texture (pyray.Texture): Reference pointer holding graphical
              source.
        """
        center_x = offset_x + self.x * side_len + side_len / 2
        center_y = offset_y + self.y * side_len + side_len / 2

        source_rec = pyray.Rectangle(0, 0, texture.width, texture.height)
        data_rec = pyray.Rectangle(
            int(center_x), int(center_y), side_len, side_len
        )
        origin = pyray.Vector2(side_len / 2, side_len / 2)

        pyray.draw_texture_pro(
            texture, source_rec, data_rec, origin, 0.0, pyray.WHITE
        )
