# Release Checklist

Do not create a remote repo, push, deploy, or post publicly until Joshua explicitly approves.

- [ ] Examples are synthetic only.
- [ ] No private data is present.
- [ ] No client, employer, recruiter, school, family, personal, or private data is present.
- [ ] No Unit27 material is present.
- [ ] No job-search material is present.
- [ ] No legacy project material is present.
- [ ] Review-only outputs are regenerated.
- [ ] Generated outputs contain source lines, evidence strength, risk flags, `proofwashing`, `scope_mismatch`, and boundary notes.
- [ ] Generated outputs do not contain `## Revised Humility-Aware Draft`.
- [ ] Tests pass: `python3 -m unittest discover -s tests`.
- [ ] Compile check passes: `PYTHONPYCACHEPREFIX=/private/tmp/humility_engine_pycache python3 -m py_compile humility_engine.py run.py`.
- [ ] Public copy does not claim truth verification, fraud prevention, certification, production readiness, or guaranteed detection.
- [ ] Public copy preserves the bounded posture: proof before claim, boundary before scale, review before release.
- [ ] Joshua approves before remote repo creation, push, deploy, or public post.
