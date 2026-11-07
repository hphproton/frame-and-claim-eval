"""Session spend, checked between trials. There is no per-trial cap.

The approved amount is the session_budget_usd value in the run config. It is
never inferred from a plan. Inter-trial accounting cannot stop a request that
is already in flight from spending past the remainder. This module does not
open a socket and does not read credentials. A live poll is a callable the
caller supplies. A missing or failed poll fails closed before the next trial.
"""


class SessionBudget:
    def __init__(self, limit_usd, poll_every=1, poller=None):
        if limit_usd is None:
            raise ValueError("session budget requires an explicit limit")
        self.limit_usd = float(limit_usd)
        self.poll_every = max(1, int(poll_every))
        self.poll_every_recorded = self.poll_every
        self.poller = poller
        self.recorded_cost = 0.0
        self.polled_cost = None
        self.trials_since_poll = 0
        self.max_trial_cost = 0.0
        self._spent_mark = None
        self.state = "known" if poller is None else "unknown"

    def note_trial_cost(self, cost):
        try:
            self.recorded_cost += float(cost or 0.0)
        except (TypeError, ValueError):
            self.state = "unknown"

    def spent(self):
        spent = self.recorded_cost
        if self.polled_cost is not None:
            spent = max(spent, self.polled_cost)
        return spent

    def _poll(self):
        snap = self.poller()
        if not isinstance(snap, dict) or "spent_usd" not in snap:
            self.state = "unknown"
            raise RuntimeError("budget poll returned no spent_usd")
        self.polled_cost = float(snap["spent_usd"])
        self.trials_since_poll = 0
        self.state = "known"
        return self.spent()

    def poll_spent(self):
        """Read the poller now. A missing poller returns the recorded total."""
        if self.poller is None:
            return self.spent()
        return self._poll()

    def before_trial(self):
        """None to continue, or a reason to stop before starting a trial.

        After one trial has a cost, the next trial is refused when repeating
        that cost would pass the limit. A trial already in flight can still
        finish above the limit.
        """
        if self.poller is not None and (self.polled_cost is None or self.trials_since_poll >= self.poll_every):
            try:
                self._poll()
            except (TypeError, ValueError, OSError, RuntimeError):
                self.state = "unknown"
                return "budget_unknown"
        if self.state != "known":
            return "budget_unknown"
        spent = self.spent()
        if self._spent_mark is not None:
            self.max_trial_cost = max(self.max_trial_cost, spent - self._spent_mark)
        self._spent_mark = spent
        if spent >= self.limit_usd:
            return "budget"
        if self.max_trial_cost > 0 and spent + self.max_trial_cost > self.limit_usd:
            return "budget"
        return None

    def after_trial(self):
        self.trials_since_poll += 1
