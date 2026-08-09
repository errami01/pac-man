import pyray


class GameTimer:
    """A countdown timer for managing game events based on frame time.

    Tracks remaining time and updates status flags automatically.
    """

    def __init__(self, duration_seconds: float) -> None:
        """Initialize the timer with a specific duration.

        Args:
            duration_seconds (float): The total time for the countdown.
        """
        self.duration = duration_seconds
        self.time_left = duration_seconds
        self.is_finished = False

    def update(self) -> None:
        """Update the countdown by subtracting the elapsed frame time.

        Sets the timer state to finished when the countdown reaches zero.
        """
        # pyray.get_frame_time() returns delta time in seconds
        dt = pyray.get_frame_time()

        if self.time_left > 0:
            self.time_left -= dt
        else:
            self.time_left = 0
            self.is_finished = True

    def reset(self) -> None:
        """Reset the timer back to its initial starting duration."""
        self.time_left = self.duration
        self.is_finished = False
