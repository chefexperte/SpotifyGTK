from threading import Thread
from time import sleep


class DelayedThread:
    thr: Thread = None
    callback: () = None
    args: [] = None
    delay: int = None
    timer: int = None

    def __init__(self, callback: (), args: [], delay: int):
        """
        Create a new thread with a resettable delay

        :param callback: The callback that is called when the timer runs out
        :param args: the args the callback is called with
        :param delay: The delay in ms
        """
        self.delay = delay
        self.callback = callback
        self.args = args
        self.timer = delay
        self.thr = Thread(target=self._countdown, args=[])
        self.thr.start()

    def _countdown(self):
        sleep(0.05)
        self.timer -= 50
        if self.timer <= 0:
            if self.callback is None:
                return
            cb = Thread(target=self.callback, args=self.args)
            cb.start()
            return
        self._countdown()

    def reset_timer(self):
        self.timer = self.delay

    def is_running(self):
        return self.timer != 0
