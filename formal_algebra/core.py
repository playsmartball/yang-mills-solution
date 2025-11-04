from dataclasses import dataclass
from typing import List, Any
import sympy as sp


@dataclass(frozen=True)
class SymbolicVar:
    name: str
    positive: bool = False
    real: bool = True

    def to_symbol(self) -> sp.Symbol:
        return sp.Symbol(self.name, positive=self.positive, real=self.real)


Expr = Any  # sympy expression alias


def expr_str(e: Expr) -> str:
    try:
        return str(sp.simplify(e))
    except Exception:
        return str(e)
