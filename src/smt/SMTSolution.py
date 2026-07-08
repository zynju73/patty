from typing import Dict

from pysmt.fnode import FNode
from pysmt.typing import INT
from z3 import IntNumRef, RatNumRef

from src.smt.SMTBoolVariable import SMTBoolVariable
from src.smt.SMTNumericVariable import SMTNumericVariable
from src.smt.SMTVariable import SMTVariable


class SMTSolution:

    def __init__(self):
        self.__variables: Dict[SMTVariable, float] = dict()

    def addVariable(self, var: SMTVariable, value: float):
        self.__variables[var] = value

    def getVariable(self, var: SMTVariable, dec: int = 3) -> float:
        node = self.__variables[var]
        if isinstance(var, SMTNumericVariable):
            if isinstance(node, IntNumRef):
                return node.as_long()
            if isinstance(node, RatNumRef):
                return float(node.as_fraction())
            if isinstance(node, FNode) and node.is_constant():
                value = node.constant_value()
                return int(value) if var.type == INT else float(value)
            return node
        if isinstance(var, SMTBoolVariable):
            raise NotImplemented("TODO")

    def __str__(self):
        return str(self.__variables)

    def prettyString(self):
        strings = [f"{v}: {val}" for (v, val) in self.__variables.items()]
        strings.sort()
        return '\n'.join(list(strings))
