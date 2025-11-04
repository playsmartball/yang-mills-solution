from dataclasses import dataclass
from typing import Callable, List, Tuple
import sympy as sp

Expr = sp.Expr


@dataclass(frozen=True)
class Rule:
    name: str
    apply: Callable[[Expr], Tuple[Expr, bool]]  # returns (new_expr, changed)


def _rule_pow_to_exp(e: Expr) -> Tuple[Expr, bool]:
    # a**b -> exp(b*log(a)) for positive a
    if isinstance(e, sp.Pow):
        base, exp = e.as_base_exp()
        if base.is_positive or (hasattr(base, 'is_positive') and base.is_positive is True):
            return (sp.exp(exp * sp.log(base)), True)
    return (e, False)


def _rule_simplify(e: Expr) -> Tuple[Expr, bool]:
    s = sp.simplify(e)
    return (s, s != e)


DEFAULT_RULES: List[Rule] = [
    Rule("pow_to_exp", _rule_pow_to_exp),
    Rule("simplify", _rule_simplify),
]


def apply_rules_deterministic(expr: Expr, rules: List[Rule] = None, max_passes: int = 5) -> Tuple[Expr, List[str]]:
    if rules is None:
        rules = DEFAULT_RULES
    steps: List[str] = []
    current = expr
    for _ in range(max_passes):
        changed_any = False
        for r in rules:
            new_expr, changed = r.apply(current)
            if changed:
                steps.append(f"{r.name}: {sp.sstr(current)} -> {sp.sstr(new_expr)}")
                current = new_expr
                changed_any = True
        if not changed_any:
            break
    return current, steps
