# Synthetic Demo Scenario: Organizational Readiness Claim

## Overstated Draft Claim

The workflow is deployment-ready and validated for regulated use.

The security checklist proves the workflow is compliant for financial review.

## Structured Evidence Notes

## Evidence: deployment-ready workflow screenshot
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local workflow screen rendered with synthetic regulated-use data
- limitations: no production deployment; no regulated-use review; no uptime history; no procurement or security review
- corroboration status: none

## Evidence: security checklist
- evidence strength: artifact-backed
- evidence type: local checklist
- scope supported: internal checklist completed against a demo environment
- limitations: no third-party audit; no penetration test; no legal review; no financial compliance review
- corroboration status: none

## Command

```bash
python3 run.py examples/scenarios/org_readiness_claim.md \
  --evidence examples/scenarios/org_readiness_claim.md \
  --output examples/reviews/org_readiness_review.md \
  --review-only
```

## Expected Result Summary

> The review is expected to treat screenshots and local checklists as limited artifacts. Expected risk flags include `scope_mismatch` and `proofwashing`; the suggested wording should narrow the claim to local demo or checklist evidence rather than deployment, regulated-use, security, compliance, or financial readiness.
