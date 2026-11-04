"""Command budget for one Terminus trial.

Harbor counts episodes in max_turns, and its parser already clips one command
to 60 seconds. The task instruction is a different limit: 30 commands, 60
seconds each, and 15 minutes of wall clock. Ask this object before each
command. A spent budget means that command does not run.
"""
import time


def clip_duration(duration, cap):
    return min(float(duration), float(cap))


class CommandBudget:
    def __init__(self, limits, clock=None):
        self.limits = limits
        self.clock = clock or time.monotonic
        self.started = self.clock()
        self.ran = 0
        self.stop = None

    def take(self, duration):
        """Return the duration to use, or None when the command must not run.

        None sets stop to wall_clock or max_steps.
        """
        if self.stop is not None:
            return None
        if self.clock() - self.started >= float(self.limits["wall_clock_sec"]):
            self.stop = "wall_clock"
            return None
        if self.ran >= int(self.limits["max_steps"]):
            self.stop = "max_steps"
            return None
        self.ran += 1
        return clip_duration(duration, self.limits["command_timeout_sec"])
