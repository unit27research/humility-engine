# Humility Engine

[![CI](https://github.com/unit27research/humility-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/unit27research/humility-engine/actions/workflows/ci.yml)

AI-polished writing can make weak evidence sound stronger than it is. Humility Engine is a small local instrument for evidence-boundary review: it helps a human inspect where a claim may outrun the evidence beneath it.

The category is evidence-boundary review.

## Release Status

`SOURCE_STATUS: PUBLIC_PACKAGE`
`ACCESS_STATUS: CLEARED_FOR_EXTERNAL_USE`
`UNIT27_POSITION: ADJACENT_CLAIM_REVIEW_UTILITY`

This repository is a released Unit27 public utility: visible, inspectable, and intended for orientation, testing, and practical use. Controlled protocol materials remain outside this source package.

It answers one narrow question:

> Where might a draft's public claim sound stronger than the evidence beneath it?

## Two Failure Modes

**Uncertainty laundering** is when uncertain, inferred, incomplete, or weakly supported information becomes confident language.

**Proofwashing** is when thin evidence, such as a screenshot, demo, checklist, one run, or self-attested note, is presented as if it proves a much broader claim.

## What Humility Engine Does

Humility Engine reads a Markdown or text draft, compares extracted claims against optional evidence notes, and produces a review surface.

It is designed to help surface:

- claims with no matching support
- self-attested or artifact-backed evidence
- evidence that supports a narrower scope than the claim
- likely `proofwashing`
- likely `scope_mismatch`
- suggested narrower wording for manual editing
- next verification steps

The recommended workflow is review-only:

1. Run the tool.
2. Inspect the claim table.
3. Manually revise the source document.
4. Do not auto-replace source docs with generated rewrites.

## What It Does Not Do

Humility Engine is not a verifier, fact-checker, fraud detector, certification system, compliance system, medical safety tool, legal reviewer, or truth oracle.

It does not browse the web, inspect external sources, validate screenshots, certify artifacts, audit code, or prove that a claim is true or false.

It is a heuristic review aid. The output is a prompt for human judgment, not a final authority.

## Where It Fits

Humility Engine is not part of the Unit27 Field Kit Suite operating sequence. It sits beside that chain as an adjacent claim-review utility for drafts, public copy, and other human-authored release material.

It is also distinct from Boundary Engine. Boundary Engine checks public repository language against recorded proof artifacts. Humility Engine helps review a draft before publication by surfacing likely uncertainty laundering, proofwashing, and scope mismatch in the language itself.

## Who It Is For

- builders writing portfolio or project claims
- researchers and operators preserving evidence boundaries in public claims
- teams reviewing AI-polished drafts before publication
- anyone trying to avoid turning a demo, artifact, or hunch into a claim that sounds proven

## Quick Demo

Run the synthetic medical-safety scenario:

```bash
python3 run.py examples/scenarios/medical_safety_claim.md \
  --evidence examples/scenarios/medical_safety_claim.md \
  --output examples/reviews/medical_safety_review.md \
  --review-only
```

The output is a claim-review table with source lines, evidence strength, risk flags, suggested narrower wording, and next verification steps.

## Before / After Example

Overstated claim:

> The model is safe for hospitals.

Evidence available:

> Local checklist review on sample prompts. No clinical review. No patient data. No hospital pilot. No external validation.

Humility Engine review result:

> A local checklist review on sample prompts is supported by artifact-backed evidence. This does not establish medical or clinical safety.

## Synthetic Demo Scenarios

The repo includes three synthetic scenarios:

- `examples/scenarios/builder_portfolio_claim.md`
- `examples/scenarios/org_readiness_claim.md`
- `examples/scenarios/medical_safety_claim.md`

Generated review-only outputs live in:

- `examples/reviews/builder_portfolio_review.md`
- `examples/reviews/org_readiness_review.md`
- `examples/reviews/medical_safety_review.md`

## Run Your Own Draft

Requirements: Python 3. No package install is required.

```bash
python3 run.py path/to/draft.md --evidence path/to/evidence.md --output path/to/review.md --review-only
```

Then read the table and manually edit the source document. Do not auto-replace source files with generated rewrites.

The older full-output mode remains available for short plain-text drafts:

```bash
python3 run.py path/to/draft.md --evidence path/to/evidence.md --output path/to/output.md
```

Treat that revised-draft section as experimental helper text, not a source-replacement artifact. Review before release.

## Claim Schema

The output table contains:

| field | meaning |
| --- | --- |
| source line | Source line where the extracted claim starts. |
| claim | Extracted claim text from the draft. |
| claim type | Rough claim category, such as proof claim or capability claim. |
| evidence provided | Best matching evidence note, or a missing-evidence note. |
| evidence strength | One of the MVP evidence-strength labels. |
| risk flag | Likely uncertainty laundering, proofwashing, related risk, or `none`. |
| humility rewrite | Safer rewrite suggestion with evidence limits visible. |
| next verification step | Suggested next action to strengthen or bound the claim. |

## Structured Evidence Notes

Evidence notes can be plain bullets, but the clearer path is a small structured Markdown format:

```markdown
## Evidence: local demo screenshot
- evidence label: local demo screenshot
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local toy CLI demo on sample input
- limitations: synthetic sample only; no customer data
- corroboration status: none
```

Supported evidence-strength values:

- `unsupported`
- `self-attested`
- `artifact-backed`
- `externally corroborated`
- `live-demonstrable`

The scope fields matter. For example, an artifact-backed local toy demo can support “a local demo ran on sample input,” but it does not establish “validated for regulated enterprise customers.”

## Current Limits

- Claim extraction is sentence-based and may miss claims spread across sections.
- Review-only mode is the recommended path for Markdown documents with headings, tables, code blocks, or examples.
- The extractor skips common Markdown structures, but it is still a heuristic parser.
- Evidence matching is keyword-based and can choose the wrong note.
- Evidence strength is inferred from wording in the evidence notes.
- The tool does not inspect files, URLs, screenshots, logs, demos, or external sources.
- Rewrites are conservative suggestions for manual editing, not safe source replacements.

## Tests

```bash
python3 -m unittest discover -s tests
```

## License

MIT
