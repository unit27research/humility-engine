# Synthetic Demo Scenario: Builder Portfolio Claim

## Overstated Draft Claim

I built a production-ready AI evaluation platform that proves teams can eliminate hallucinations.

The demo validates public-use reliability for regulated-use claims.

## Structured Evidence Notes

## Evidence: local AI evaluation prototype demo
- evidence strength: artifact-backed
- evidence type: local demo output
- scope supported: local prototype run on three synthetic prompts
- limitations: no production deployment; no external users; no independent evaluation; no longitudinal reliability data
- corroboration status: none

## Evidence: hallucination reduction note
- evidence strength: self-attested
- evidence type: manual observation note
- scope supported: one local review pass on sample outputs
- limitations: not a benchmark; no external reviewer; no repeated test set
- corroboration status: none

## Command

```bash
python3 run.py examples/scenarios/builder_portfolio_claim.md \
  --evidence examples/scenarios/builder_portfolio_claim.md \
  --output examples/reviews/builder_portfolio_review.md \
  --review-only
```

## Expected Result Summary

> The review is expected to flag broad production, enterprise, and proof language as outrunning local prototype evidence. Expected risk flags include `proofwashing` and `scope_mismatch` where artifact-backed local output is used to support production or enterprise readiness.
