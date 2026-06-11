import traceback
import sys
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path
from typing import TextIO

from src.pddl.Domain import Domain, GroundedDomain
from src.pddl.Plan import Plan
from src.pddl.Problem import Problem
from src.search.AStarSearchMax import AStarSearchMax
from src.search.ChainSearch import ChainSearch
from src.search.Search import Search
from src.search.StepSearch import StepSearch
from src.utils.Arguments import Arguments
from src.utils.LogPrint import LogPrint, LogPrintLevel
from src.utils.TimeStat import TimeStat


class TeeOutput:
    def __init__(self, terminal: TextIO, output_file: TextIO):
        self.terminal = terminal
        self.output_file = output_file

    def write(self, message: str):
        self.terminal.write(message)
        self.output_file.write(message)

    def flush(self):
        self.terminal.flush()
        self.output_file.flush()


def main():
    args = Arguments()
    if args.isHelp:
        exit(0)

    if args.saveOutput:
        output_path = get_output_path(args)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fout:
            tee_out = TeeOutput(terminal=sys.stdout, output_file=fout)
            tee_err = TeeOutput(terminal=sys.stderr, output_file=fout)
            with redirect_stdout(tee_out), redirect_stderr(tee_err):
                run(args)
        return

    run(args)


def get_output_path(args: Arguments) -> Path:
    if args.saveOutput != "RESULTS":
        return Path(args.saveOutput)

    problem_path = Path(args.problem)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("results") / f"{problem_path.stem}_{timestamp}.out"


def run(args: Arguments):

    solver: Search or None = None
    try:
        console: LogPrint = LogPrint(args.verboseLevel)
        ts: TimeStat = TimeStat()
        ts.start("Overall")
        domain: Domain = Domain.fromFile(args.domain)
        problem: Problem = Problem.fromFile(args.problem)

        ts.start("Grounding", console=console)
        gDomain: GroundedDomain = domain.ground(problem, console=console)
        ts.end("Grounding", console=console)

        isTemporal = len(gDomain.durativeActions) > 0
        if args.search == "astar":
            solver = AStarSearchMax(gDomain, problem, args)
        elif args.search == "step":
            solver = StepSearch(gDomain, problem, args)
        else:
            solver = ChainSearch(gDomain, problem, args)
        plan: Plan = solver.solve()

        console.log(plan.toValString(), LogPrintLevel.PLAN)
        console.log("------", LogPrintLevel.STATS)
        console.log(f"Max Rolling: {plan.getMaxRolling()}", LogPrintLevel.STATS)
        console.log(f"Distinct Actions: {len(plan.getDistinctActions())}", LogPrintLevel.STATS)
        console.log("------", LogPrintLevel.STATS)
        isValid = plan.validate(problem, avoidRaising=True, logger=console)
        if isValid:
            console.log("Plan is valid", LogPrintLevel.PLAN)
            if args.savePlan:
                fn = args.savePlan if args.savePlan != "PROBLEM" else args.problem + ".plan"
                with open(fn, "w") as f:
                    f.write(plan.toValString())
        else:
            console.log("Plan is NOT valid", LogPrintLevel.PLAN)

        ts.end("Overall")
        console.log(str(ts), LogPrintLevel.TIMES)

    except:
        print("Something went wrong.")
        traceback.print_exc()


if __name__ == '__main__':
    main()
