from src.pddl.Action import Action


class TemporalPlanInstantAction:
    action: Action

    def __init__(self, action: Action, time: float):
        self.action = action
        self.time = time

    @staticmethod
    def format_time(value: float) -> str:
        return f"{value:.6f}".rstrip("0").rstrip(".")

    def __str__(self):
        return f"({self.format_time(self.time)}:{self.action})"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.time < other.time
