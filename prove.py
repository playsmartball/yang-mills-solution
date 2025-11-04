import os
import json
from formal_algebra.engine import Prover
from formal_algebra.export_latex import export_proofs_document


def main():
    os.makedirs("artifacts", exist_ok=True)
    prover = Prover()

    proofs = [
        prover.prove_T1_domain_positivity(),
        prover.prove_T2_monotone_decreasing(),
        prover.prove_T3_mass_gap_positivity(),
    ]

    # Save JSON certificates
    json_path = os.path.join("artifacts", "proofs_phi_scheme.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() | {"hash": p.hash()} for p in proofs], f, indent=2, ensure_ascii=False, sort_keys=True)

    # Save LaTeX transcript
    tex_path = os.path.join("artifacts", "proofs_phi_scheme.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(export_proofs_document(proofs))

    print("Generated:")
    print(" -", json_path)
    print(" -", tex_path)
    print("\nProof hashes:")
    for p in proofs:
        print(f"  {p.theorem}: {p.hash()}")


if __name__ == "__main__":
    main()
