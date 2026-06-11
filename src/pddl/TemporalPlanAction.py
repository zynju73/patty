from src.pddl.Action import Action
from src.pddl.DurativeAction import DurativeAction


class TemporalPlanAction:
    action: DurativeAction

    def __init__(self, action: DurativeAction, time: float, duration: float):
        self.action = action
        self.time = time
        self.duration = duration

    @staticmethod
    def format_time(value: float) -> str:
        return f"{value:.6f}".rstrip("0").rstrip(".")

    def __str__(self):
        return f"({self.format_time(self.time)}:{self.action.originalName}) [{self.format_time(self.duration)}]"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.time < other.time
