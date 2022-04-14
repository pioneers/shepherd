import time
import threading
import ydl
from utils import YDL_TARGETS

class TimerThread(threading.Thread):
    '''
    Subclass that is the actual thread that will be running.
    There will only be one for the entire Timer class.
    '''
    def __init__(self):
        super().__init__()
        self.daemon = True # will stop abruptly when main thread dies


    def run(self):
        """When started, thread will run and process Timers in queue until the queue is empty."""
        while Timer.eventQueue:
            if not Timer.paused:
                time_to_wait = Timer.update_all()
                if time_to_wait > 0:
                    time.sleep(0.99 * time_to_wait)
                    # 0.99 makes it run a few extra cycles, but more accurate


class Timer:
    """
    This class should spawn another thread that will keep track of a target time
    and compare it to the current system time in order to see how much time is left
    """
    MIN_TIMER_TIME = 1 # TODO: put this in Utils.py
    eventQueue = []
    queueLock = threading.Lock()
    thread = TimerThread()
    paused = False
    pauseStart = 0

    @classmethod
    def update_all(cls):
        """
        Checks to see if any of the timers has run out, and does the timer's callback if so
        (may run multiple callbacks). Returns the time remaining until the next timer
        (could be negative if timers expire at the same time).
        This assumes that a timer will never have its end_time spontanously decrease,
        and that all timers last at least MIN_TIMER_TIME
        """
        cls.queueLock.acquire()
        current_time = time.time()
        finished = [t for t in cls.eventQueue if t.end_time <  current_time]
        keep     = [t for t in cls.eventQueue if t.end_time >= current_time]
        # want to end immediately if queue is empty
        min_time = current_time if len(keep) == 0 else min((t.end_time for t in keep))
        cls.eventQueue = keep
        cls.queueLock.release()
        for t in finished:
            t.end_timer()
        # current time is recalculated for accuracy
        return min(cls.MIN_TIMER_TIME, min_time - time.time())


    @classmethod
    def reset_all(cls):
        """Resets Timer Thread when game changes"""
        cls.queueLock.acquire()
        for t in cls.eventQueue:
            t.active = False
        cls.eventQueue = []
        cls.queueLock.release()
        # since queue is empty, timer thread will stop

    @classmethod
    def pause(cls):
        """Pause timer and get when it was paused"""
        if cls.paused:
            print("Already paused")
        else:
            cls.queueLock.acquire()
            cls.pauseStart = time.time()    
            cls.paused = True
            print(f"Pause status: {cls.paused}")
            cls.queueLock.release()


    @classmethod
    def resume(cls):
        """Unpause timer and add difference of current time and when timer was paused
        to all timers."""
        if not cls.paused:
            print("Not paused yet")
        else:
            cls.queueLock.acquire()
            pauseEnd = time.time()
            for t in cls.eventQueue:
                t.end_time += (pauseEnd - cls.pauseStart)
            cls.paused = False
            print(f"Pause status: {cls.paused}")
            cls.queueLock.release()

    def __init__(self, timer_type):
        """
        timer_type - a Enum representing the type of timer that this is:
                        TIMER_TYPES.MATCH - represents the time of the current
        """
        self.active = False
        self.timer_type = timer_type
        self.end_time = None


    def start_timer(self, duration):
        """Starts a new timer with the duration (seconds) and sets timer to active.
           If Timer is already running, restarts timer"""
        Timer.queueLock.acquire()
        if self.active:
            self.end_time = time.time() + duration
        else:
            self.end_time = time.time() + duration
            Timer.eventQueue.append(self)
            self.active = True

        if not Timer.thread.is_alive():
            Timer.thread = TimerThread()
            Timer.thread.start()
        Timer.queueLock.release()


    def end_timer(self):
        """Does the callback for current timer and sets it to inactive.
           Note that current timer should not be in the event queue, to avoid deadlock"""
        if not self.active:
            return #if timer was just reset
        self.active = False #in case callback restarts the timer, do this first
        if self.timer_type is not None and "FUNCTION" in self.timer_type:
            ydl.ydl_send(YDL_TARGETS.SHEPHERD, self.timer_type["FUNCTION"])


    def reset(self):
        """Stops the current timer (if any) and sets timer to inactive"""
        Timer.queueLock.acquire()
        if self.active:
            if self in Timer.eventQueue:
                Timer.eventQueue.remove(self)
            self.active = False
        Timer.queueLock.release()


    def is_running(self):
        """
        Returns true if the timer is currently running.
        Specifically, returns true if it's in the event queue,
        or about to do its callback
        """
        return self.active
