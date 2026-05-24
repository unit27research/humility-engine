# Release Checklist

Public release posture: approved for GitHub publication and hardening. This checklist tracks the public package boundary, not private Unit27 protocol materials.

- [x] Examples are synthetic only.
- [x] No private data is present.
- [x] No client, employer, recruiter, school, family, personal, or private data is present.
- [x] No controlled Unit27 material is present.
- [x] No job-search material is present.
- [x] No legacy project material is present.
- [x] Review-only outputs are regenerated.
- [x] Generated outputs contain source lines, evidence strength, risk flags, `proofwashing`, `scope_mismatch`, and boundary notes.
- [x] Generated outputs do not contain `## Revised Humility-Aware Draft`.
- [x] Tests pass: `python3 -m unittest discover -s tests`.
- [x] Compile check passes: `PYTHONPYCACHEPREFIX=/private/tmp/humility_engine_pycache python3 -m py_compile humility_engine.py run.py`.
- [x] Public copy does not claim truth verification, fraud prevention, certification, production readiness, or guaranteed detection.
- [x] Public copy preserves the bounded posture: proof before claim, boundary before scale, review before release.
- [x] Joshua approved the public GitHub hardening and push on 2026-05-24.
