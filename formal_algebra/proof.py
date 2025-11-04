from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Optional, Any, Dict
import json
import hashlib


@dataclass
class ProofStep:
    description: str
    rule: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None


@dataclass
class Proof:
    theorem: str
    assumptions: List[str]
    steps: List[ProofStep]
    conclusion: str
    qed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theorem": self.theorem,
            "assumptions": list(self.assumptions),
            "steps": [asdict(s) for s in self.steps],
            "conclusion": self.conclusion,
            "qed": self.qed,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False, indent=2)

    def hash(self) -> str:
        h = hashlib.sha256()
        h.update(self.to_json().encode("utf-8"))
        return h.hexdigest()
