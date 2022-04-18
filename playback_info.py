class PlaybackInfo:
    title: str = None
    position: int = None
    duration: int = None
    volume: int = None
    playing: bool = None

    def __init__(self, title, position, duration):
        self.title = title
        self.position = position
        self.duration = duration
