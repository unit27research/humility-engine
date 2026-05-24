# Synthetic Demo Scenario: Medical Safety Claim

## Overstated Draft Claim

The model is safe for hospitals.

The checklist proves this workflow is approved for patient-facing clinical use.

## Structured Evidence Notes

## Evidence: hospital safety checklist
- evidence strength: artifact-backed
- evidence type: local checklist
- scope supported: local checklist review on sample prompts
- limitations: no clinical review; no patient data; no hospital pilot; no external validation
- corroboration status: none

## Evidence: patient-facing approval note
- evidence strength: unsupported
- evidence type: none
- scope supported: no approval evidence
- limitations: no certification body; no medical reviewer; no legal approval; no clinical deployment
- corroboration status: none

## Command

```bash
python3 run.py examples/scenarios/medical_safety_claim.md \
  --evidence examples/scenarios/medical_safety_claim.md \
  --output examples/reviews/medical_safety_review.md \
  --review-only
```

## Expected Result Summary

> The review is expected to flag the hospital safety claim as `scope_mismatch` and `proofwashing` because a local checklist on sample prompts does not establish medical or clinical safety. The approval claim should remain unsupported unless real approval evidence exists.
