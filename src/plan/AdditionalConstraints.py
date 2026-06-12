from typing import Dict, List, Set, Tuple

from src.pddl.Atom import Atom
from src.pddl.BinaryPredicate import BinaryPredicate
from src.pddl.Constant import Constant
from src.pddl.Domain import GroundedDomain
from src.pddl.Literal import Literal
from src.pddl.Predicate import Predicate
from src.pddl.Problem import Problem
from src.plan.Pattern import Pattern
from src.smt.SMTExpression import SMTExpression


class PatternEffectIndex:
    """Reverse effect indexes for the concrete action occurrences in a pattern."""

    def __init__(self, pattern: Pattern, modes: Set[str]):
        self.adds: Dict[Atom, List[int]] = {}
        self.deletes: Dict[Atom, List[int]] = {}
        self.increases: Dict[Atom, List[Tuple[int, Predicate]]] = {}
        self.decreases: Dict[Atom, List[Tuple[int, Predicate]]] = {}
        self.assignments: Dict[Atom, List[int]] = {}
        self.influencedBy: Dict[Atom, List[int]] = {}

        if not modes:
            return

        for i, action in enumerate(pattern):
            if action.isFake:
                continue

            if "support" in modes:
                for atom in action.getAddList():
                    self.adds.setdefault(atom, []).append(i)
                for atom in action.getDelList():
                    self.deletes.setdefault(atom, []).append(i)

            if "resource" in modes:
                for atom, amount in action.getIncreases().items():
                    self.increases.setdefault(atom, []).append((i, amount))
                for atom, amount in action.getDecreases().items():
                    self.decreases.setdefault(atom, []).append((i, amount))
                for atom in action.getAssList():
                    self.assignments.setdefault(atom, []).append(i)
                for atom in action.getInfluencedAtoms():
                    self.influencedBy.setdefault(atom, []).append(i)


class AdditionalConstraintGenerator:
    """Generate conservative necessary constraints from a grounded pattern."""

    def __init__(self, domain: GroundedDomain, problem: Problem, pattern: Pattern,
                 prevVars, stepVars, mode: str = None, actionVariablesByIndex=False,
                 patternIndex: PatternEffectIndex = None, supportRuleGrouping="action"):
        self.domain = domain
        self.problem = problem
        self.pattern = pattern
        self.prevVars = prevVars
        self.stepVars = stepVars
        self.actionVariablesByIndex = actionVariablesByIndex
        self.supportRuleGrouping = supportRuleGrouping
        self.modes = self.getModes(mode)
        self.stats = {"support": 0, "resource": 0}
        self.patternIndex = patternIndex or PatternEffectIndex(pattern, self.modes)

    @staticmethod
    def getModes(mode: str) -> Set[str]:
        if not mode:
            return set()
        if mode == "all":
            return {"support", "resource"}
        return {mode}

    def __getActionVariable(self, index: int):
        key = index if self.actionVariablesByIndex else self.pattern[index]
        return self.stepVars.actionVariables[key]

    def generate(self) -> List[SMTExpression]:
        rules = []
        if "support" in self.modes:
            supportRules = self.__getSupportRules()
            self.stats["support"] = len(supportRules)
            rules.extend(supportRules)
        if "resource" in self.modes:
            resourceRules = self.__getResourceRules()
            self.stats["resource"] = len(resourceRules)
            rules.extend(resourceRules)
        return rules

    def __getSupportRules(self) -> List[SMTExpression]:
        rules = []

        for i, action in enumerate(self.pattern):
            if action.isFake:
                continue

            actionCount = self.__getActionVariable(i)
            actionSupports = []
            for precondition in action.preconditions:
                if not isinstance(precondition, Literal):
                    continue

                atom = precondition.getAtom()
                if atom not in self.prevVars.valueVariables:
                    continue
                entrySupport = self.prevVars.valueVariables[atom]
                if precondition.sign == "-":
                    entrySupport = entrySupport.NOT()
                supporters = [entrySupport]
                supporterIndexes = self.patternIndex.adds.get(atom, []) if precondition.sign == "+" \
                    else self.patternIndex.deletes.get(atom, [])
                for j in supporterIndexes:
                    if j >= i:
                        break
                    supporters.append(self.__getActionVariable(j) > 0)

                support = SMTExpression.orOfExpressionsList(supporters)
                if self.supportRuleGrouping == "precondition":
                    rules.append((actionCount > 0).implies(support))
                else:
                    actionSupports.append(support)

            if self.supportRuleGrouping == "action" and actionSupports:
                allSupports = SMTExpression.andOfExpressionsList(actionSupports)
                rules.append((actionCount > 0).implies(allSupports))

        return rules

    @staticmethod
    def __isInteger(value: float) -> bool:
        return float(value).is_integer()

    def __hasIntegerLattice(self, atom: Atom) -> bool:
        if atom not in self.problem.init.numericAssignments \
                or not self.__isInteger(self.problem.init.numericAssignments[atom]):
            return False

        if self.domain.assList.get(atom):
            return False

        modifiers = self.domain.influencedBy.get(atom, set())
        decreases = self.domain.decreaseList.get(atom, set())
        increases = self.domain.increaseList.get(atom, set())
        if modifiers - decreases - increases:
            return False

        for actions, getModifications in (
                (decreases, lambda action: action.getDecreases()),
                (increases, lambda action: action.getIncreases())):
            for action in actions:
                modifications = getModifications(action)
                amount = modifications[atom]
                if not isinstance(amount, Constant) or not self.__isInteger(amount.value):
                    return False
        return True

    def __hasSufficientConsumptionPrecondition(self, action, atom: Atom, amount: float,
                                               integerLattice: bool) -> bool:
        for precondition in action.preconditions:
            if not isinstance(precondition, BinaryPredicate):
                continue

            operator = precondition.operator
            if isinstance(precondition.lhs, Literal) and precondition.lhs.getAtom() == atom \
                    and isinstance(precondition.rhs, Constant):
                threshold = float(precondition.rhs.value)
            elif isinstance(precondition.lhs, Constant) and isinstance(precondition.rhs, Literal) \
                    and precondition.rhs.getAtom() == atom:
                threshold = float(precondition.lhs.value)
                operator = {">=": "<=", ">": "<", "<=": ">=", "<": ">"}.get(operator, operator)
            else:
                continue

            if operator in {">=", "="} and threshold >= amount:
                return True
            if operator == ">" and threshold >= amount:
                return True
            if operator == ">" and integerLattice and self.__isInteger(threshold) \
                    and self.__isInteger(amount) and threshold >= amount - 1:
                return True

        return False

    def __getResourceRules(self) -> List[SMTExpression]:
        rules = []

        for atom, indexedConsumers in self.patternIndex.decreases.items():
            consumers = []
            producers = []
            integerLattice = self.__hasIntegerLattice(atom)

            recognizedIndexes = {
                i for i, _ in self.patternIndex.decreases.get(atom, [])
            } | {
                i for i, _ in self.patternIndex.increases.get(atom, [])
            }
            if self.patternIndex.assignments.get(atom) \
                    or any(i not in recognizedIndexes for i in self.patternIndex.influencedBy.get(atom, [])):
                continue

            safe = True
            for i, amount in indexedConsumers:
                if not isinstance(amount, Constant) or amount.value <= 0:
                    safe = False
                    break
                integerLattice = integerLattice and self.__isInteger(amount.value)
                consumers.append((i, float(amount.value)))
            if not safe:
                continue

            for i, amount in self.patternIndex.increases.get(atom, []):
                if not isinstance(amount, Constant) or amount.value <= 0:
                    safe = False
                    break
                integerLattice = integerLattice and self.__isInteger(amount.value)
                producers.append((i, float(amount.value)))
            if not safe:
                continue

            if any(not self.__hasSufficientConsumptionPrecondition(
                    self.pattern[i], atom, amount, integerLattice) for i, amount in consumers):
                continue

            totalConsumption = sum(self.__getActionVariable(i) * amount for i, amount in consumers)
            totalProduction = sum(self.__getActionVariable(i) * amount for i, amount in producers)
            rules.append(totalConsumption <= self.prevVars.valueVariables[atom] + totalProduction)

        return rules
