import threading
import time

# pylint: disable=protected-access

class TimerGroup:
    """
    A group of timers, which can be paused and unpaused together.
    Please do not access instance variables directly, instead use the
    is_paused(), pause(), and resume() methods
    """
    def __init__(self):
        self._timers: list[Timer] = []
        self._paused = False
        self._sema = threading.Semaphore(value=0)
        self._lock = threading.Lock()
        # lock protects all instance variables, as well as all
        # instance variables in the individual timers.
        threading.Thread(target=self._timer_loop, daemon=True).start()

    def is_paused(self):
        with self._lock: # with clause releases lock on return
            return self._paused

    def pause(self):
        """
        Pauses this group of timers. If group is already paused, does nothing.
        """
        cur = time.time()
        with self._lock:
            if self._paused:
                return # with clause releases lock on return
            self._paused = True
            for timer in self._timers:
                if timer._running:
                    timer._time_remaining = timer._end_time - cur
                    timer._end_time = None

    def resume(self):
        """
        Resumes this group of timers. If group is not paused, does nothing
        """
        cur = time.time()
        with self._lock:
            if not self._paused:
                return # with clause releases lock on return
            self._paused = False
            for timer in self._timers:
                if timer._running:
                    timer._end_time = timer._time_remaining + cur
                    timer._time_remaining = None
        self._sema.release() # wake timer thread

    def reset_all(self):
        """
        Resets all timers to not running, and sets this group to unpaused.
        """
        with self._lock:
            self._paused = False
            for timer in self._timers:
                timer._running = False
                timer._end_time = None
                timer._time_remaining = None

    def _timer_loop(self):
        """
        In a loop, will wait for timer expiry
        """
        while True:
            self._sema.acquire(timeout=self._timer_loop_update())

    def _timer_loop_update(self):
        """
        Runs callbacks of all expired timers, and returns the time to
        wait until the next timer expires (None if no timers will expire).
        Time to wait will be 0.99 * (min_expiry_time - curren_time),
        which causes the timer loop to spin a bit but results in more accurate timing.
        Does nothing if group is paused (no callbacks should run during a pause).
        """
        with self._lock:
            if self._paused:
                return None
            callbacks = []
            min_time = None
            cur = time.time()
            for t in self._timers:
                if t._running and t._end_time < cur:
                    callbacks.append(t._callback)
                    t._running = False
                    t._end_time = None
                elif t._running:
                    if min_time is None or t._end_time < min_time:
                        min_time = t._end_time

        # do all callbacks (outside lock for deadlock reasons)
        for c in callbacks:
            c()
        # return time to wait before next update
        return None if min_time is None else max(0, 0.99 * (min_time - time.time()))

class Timer:
    """
    A timer, bound to a specific callback. Each timer is part of a specific TimerGroup.
    Please do not access instance variables directly, instead use the
    status() method to get instance variables. Use start() and reset() to control timer.
    """
    def __init__(self, timergroup: TimerGroup, callback):
        self._timergroup = timergroup
        self._callback = callback
        self._running = False
        self._end_time = None # only used when running
        self._time_remaining = None # only used when running and group is paused
        with self._timergroup._lock:
            self._timergroup._timers.append(self)

    def status(self):
        """
        returns the tuple (end_time, time_remaining)
        if timer is not running: end_time = None,  time_remaining = None
        if timer is paused:      end_time = None,  time_remaining = float
        if timer is running:     end_time = float, time_remaining = None
        """
        with self._timergroup._lock: # will release on return
            return (self._end_time, self._time_remaining)

    def start(self, duration):
        """
        Starts a timer. If timer is already running, restarts timer.
        """
        cur = time.time()
        with self._timergroup._lock:
            if self._timergroup._paused:
                self._end_time = None
                self._time_remaining = duration
            else:
                self._end_time = duration + cur
                self._time_remaining = None
            self._running = True
        self._timergroup._sema.release() # wake up timergroup thread

    def reset(self):
        """
        Resets the timer to not running. If timer is not running, does nothing.
        """
        with self._timergroup._lock:
            self._running = False
            self._end_time = None
            self._time_remaining = None
