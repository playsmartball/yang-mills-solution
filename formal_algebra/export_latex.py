from typing import List
from .proof import Proof


def export_proof_to_latex(p: Proof) -> str:
    lines = []
    lines.append(f"% Theorem: {p.theorem}")
    lines.append("\\begin{proof}")
    if p.assumptions:
        lines.append("Assumptions: " + "; ".join(p.assumptions) + ".")
    for s in p.steps:
        desc = s.description.replace('pi', '\\pi')
        lines.append(desc + "\\\n")
    lines.append("Conclusion: " + p.conclusion)
    lines.append("\\end{proof}")
    lines.append(f"% Proof hash: {p.hash()}")
    return "\n".join(lines)


def export_proofs_document(proofs: List[Proof]) -> str:
    body = []
    for p in proofs:
        body.append("\\subsection*{" + p.theorem + "}")
        body.append(export_proof_to_latex(p))
        body.append("")
    return "\n".join(body)
