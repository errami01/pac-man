import pyray

class GameTimer:
    def __init__(self, duration_seconds):
        self.duration = duration_seconds
        self.time_left = duration_seconds
        self.is_finished = False

    def update(self):
        # pyray.get_frame_time() returns delta time in seconds
        dt = pyray.get_frame_time() 
        
        if self.time_left > 0:
            self.time_left -= dt
        else:
            self.time_left = 0
            self.is_finished = True

    def reset(self):
        self.time_left = self.duration
        self.is_finished = False
