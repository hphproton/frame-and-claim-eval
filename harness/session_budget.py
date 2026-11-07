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
        self.state = "known" if poller is None else "unknown"

    def note_trial_cost(self, cost):
        try:
            self.recorded_cost += float(cost or 0.0)
        except (TypeError, ValueError):
            self.state = "unknown"

    def before_trial(self):
        """None to continue, or a reason to stop before starting a trial."""
        if self.poller is not None and (self.polled_cost is None or self.trials_since_poll >= self.poll_every):
            try:
                snap = self.poller()
                if not isinstance(snap, dict) or "spent_usd" not in snap:
                    self.state = "unknown"
                    return "budget_unknown"
                self.polled_cost = float(snap["spent_usd"])
                self.trials_since_poll = 0
                self.state = "known"
            except (TypeError, ValueError, OSError, RuntimeError):
                self.state = "unknown"
                return "budget_unknown"
        if self.state != "known":
            return "budget_unknown"
        spent = self.recorded_cost
        if self.polled_cost is not None:
            spent = max(spent, self.polled_cost)
        if spent >= self.limit_usd:
            return "budget"
        return None

    def after_trial(self):
        self.trials_since_poll += 1
