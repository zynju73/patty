import os
import random

import numpy as np
import z3


DEFAULT_SEED = 2026


def configureRandomSeed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    z3.set_param("smt.random_seed", seed)
    z3.set_param("sat.random_seed", seed)


def getPythonHashSeed():
    return os.environ.get("PYTHONHASHSEED")
