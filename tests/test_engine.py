import unittest
from pathlib import Path

from humility_engine import analyze_document, parse_evidence_notes, render_markdown


SAMPLE_INPUT = """# Sample

Our evaluation proves the product is ready for enterprise deployment.

We believe the prototype reduced review time by 40% in one internal run.

The dashboard is live-demonstrable through the local CLI.
"""


SAMPLE_EVIDENCE = """# Evidence

- enterprise deployment: no customer pilot, no independent security review.
- internal run: self-attested note from one manual timing pass.
- dashboard local CLI: live demo command available in this repository.
"""


class HumilityEngineTests(unittest.TestCase):
    def test_analyze_document_labels_claims_and_risks(self):
        review = analyze_document(SAMPLE_INPUT, SAMPLE_EVIDENCE)

        self.assertEqual(len(review["claims"]), 3)

        proof_claim = review["claims"][0]
        self.assertEqual(proof_claim["claim_type"], "proof claim")
        self.assertEqual(proof_claim["evidence_strength"], "unsupported")
        self.assertIn("uncertainty_laundering", proof_claim["risk_flag"])
        self.assertIn("proofwashing", proof_claim["risk_flag"])
        self.assertIn("Current notes do not prove", proof_claim["humility_rewrite"])

        internal_claim = review["claims"][1]
        self.assertEqual(internal_claim["evidence_strength"], "self-attested")
        self.assertIn("qualified performance claim", internal_claim["claim_type"])
        self.assertIn("one internal run", internal_claim["humility_rewrite"])

        demo_claim = review["claims"][2]
        self.assertEqual(demo_claim["evidence_strength"], "live-demonstrable")
        self.assertEqual(demo_claim["risk_flag"], "none")

    def test_render_markdown_includes_schema_and_revised_draft(self):
        review = analyze_document(SAMPLE_INPUT, SAMPLE_EVIDENCE)
        markdown = render_markdown(review)

        self.assertIn("| source line | claim | claim type | evidence provided | evidence strength | risk flag | humility rewrite | next verification step |", markdown)
        self.assertIn("## Revised Humility-Aware Draft", markdown)
        self.assertIn("unsupported", markdown)
        self.assertIn("proofwashing", markdown)
        self.assertIn("live-demonstrable", markdown)

    def test_review_only_output_suppresses_revised_draft(self):
        review = analyze_document(SAMPLE_INPUT, SAMPLE_EVIDENCE)
        markdown = render_markdown(review, review_only=True)

        self.assertIn("## Claim Schema", markdown)
        self.assertIn("| source line | claim | claim type |", markdown)
        self.assertNotIn("## Revised Humility-Aware Draft", markdown)
        self.assertNotIn("# Sample", markdown)
        self.assertIn("## Boundary Note", markdown)

    def test_markdown_code_fences_tables_headings_and_blockquotes_are_skipped(self):
        draft = """# This heading should not become a claim.

The real product proves enterprise readiness.

```markdown
The fenced example proves hospital safety.
```

| claim | evidence |
| --- | --- |
| The table proves production readiness. | Screenshot only. |

> The blockquote demo proves customer readiness.

## Evidence: structured example heading
- evidence strength: artifact-backed
- scope supported: local sample only
"""
        review = analyze_document(draft, "")
        extracted = [claim["claim"] for claim in review["claims"]]

        self.assertEqual(extracted, ["The real product proves enterprise readiness."])

    def test_claim_rows_include_source_line_number(self):
        draft = """# Heading

First real claim proves enterprise readiness.

Second real claim is safe for hospitals.
"""
        review = analyze_document(draft, "")

        self.assertEqual(review["claims"][0]["source_line"], 3)
        self.assertEqual(review["claims"][1]["source_line"], 5)
        markdown = render_markdown(review, review_only=True)
        self.assertIn("| 3 | First real claim proves enterprise readiness.", markdown)
        self.assertIn("| 5 | Second real claim is safe for hospitals.", markdown)

    def test_structured_evidence_note_parsing(self):
        evidence = """# Evidence

## Evidence: local demo screenshot
- evidence label: local demo screenshot
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local toy CLI demo on sample input
- limitations: synthetic sample only; no customer data
- corroboration status: none
"""
        notes = parse_evidence_notes(evidence)

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].label, "local demo screenshot")
        self.assertEqual(notes[0].strength, "artifact-backed")
        self.assertEqual(notes[0].evidence_type, "screenshot")
        self.assertEqual(notes[0].scope_supported, "local toy CLI demo on sample input")
        self.assertIn("synthetic sample only", notes[0].limitations)
        self.assertEqual(notes[0].corroboration_status, "none")

    def test_artifact_backed_local_demo_does_not_clear_enterprise_claim(self):
        draft = "The system is validated for regulated enterprise customers."
        evidence = """# Evidence

## Evidence: local demo screenshot
- evidence strength: artifact-backed
- evidence type: screenshot
- scope supported: local toy CLI demo on sample input
- limitations: synthetic sample only; no regulated customer pilot
- corroboration status: none
"""
        review = analyze_document(draft, evidence)
        claim = review["claims"][0]

        self.assertEqual(claim["evidence_strength"], "artifact-backed")
        self.assertIn("scope_mismatch", claim["risk_flag"])
        self.assertIn("proofwashing", claim["risk_flag"])
        self.assertIn("local toy CLI demo on sample input", claim["humility_rewrite"])
        self.assertIn("does not establish regulated enterprise customer readiness", claim["humility_rewrite"])

    def test_artifact_backed_local_checklist_does_not_clear_hospital_safety_claim(self):
        draft = "The model is safe for hospitals."
        evidence = """# Evidence

## Evidence: local hospital safety checklist
- evidence strength: artifact-backed
- evidence type: local checklist
- scope supported: local checklist review on sample prompts
- limitations: no clinical review; no patient data; no hospital pilot; no external validation
- corroboration status: none
"""
        review = analyze_document(draft, evidence)
        claim = review["claims"][0]

        self.assertEqual(claim["evidence_strength"], "artifact-backed")
        self.assertIn("scope_mismatch", claim["risk_flag"])
        self.assertIn("proofwashing", claim["risk_flag"])
        self.assertIn("local checklist review on sample prompts", claim["humility_rewrite"])
        self.assertIn("does not establish medical or clinical safety", claim["humility_rewrite"])

    def test_scope_rewrite_uses_plain_article_for_one_and_the_phrases(self):
        draft = "The workflow is proven for enterprise teams."
        evidence = """# Evidence

## Evidence: one sample workflow rewrite
- evidence strength: artifact-backed
- evidence type: local output
- scope supported: one sample workflow claim rewrite
- limitations: local sample only
- corroboration status: none
"""
        review = analyze_document(draft, evidence)

        self.assertIn("One sample workflow claim rewrite is supported", review["claims"][0]["humility_rewrite"])
        self.assertNotIn("An one sample workflow claim rewrite", review["claims"][0]["humility_rewrite"])

    def test_duplicate_repeated_claims_are_rewritten_without_corruption(self):
        draft = """The CLI proves enterprise readiness.

The CLI proves enterprise readiness.
"""
        evidence = """# Evidence

## Evidence: CLI sample output
- evidence strength: artifact-backed
- evidence type: local output
- scope supported: local CLI run on sample input
- limitations: no production deployment or customer validation
- corroboration status: none
"""
        review = analyze_document(draft, evidence)

        self.assertEqual(len(review["claims"]), 2)
        self.assertEqual(review["revised_draft"].count("local CLI run on sample input"), 2)
        self.assertNotIn("readiness. Treat it as unverified", review["revised_draft"])
        self.assertNotIn("Current notes do not prove this claim: Current notes", review["revised_draft"])

    def test_repository_example_still_generates_required_review_fields(self):
        root = Path(__file__).resolve().parents[1]
        draft = (root / "examples/input.md").read_text(encoding="utf-8")
        evidence = (root / "examples/evidence.md").read_text(encoding="utf-8")

        review = analyze_document(draft, evidence)
        markdown = render_markdown(review)

        self.assertGreaterEqual(len(review["claims"]), 1)
        self.assertIn("## Claim Schema", markdown)
        self.assertIn("## Revised Humility-Aware Draft", markdown)
        self.assertIn("evidence strength", markdown)

    def test_structured_evidence_matching_prefers_label_and_scope_over_limitations(self):
        draft = "Our pilot reduced claim review time by 40% across the organization."
        evidence = """# Evidence

## Evidence: enterprise governance toy artifact
- evidence strength: artifact-backed
- evidence type: local Markdown output
- scope supported: local claim-review table generated from sample input
- limitations: no customer pilot, no independent compliance review
- corroboration status: none

## Evidence: pilot review time
- evidence strength: self-attested
- evidence type: timing note
- scope supported: one internal run using a short sample document
- limitations: not repeated
- corroboration status: none
"""
        review = analyze_document(draft, evidence)

        self.assertIn("pilot review time", review["claims"][0]["evidence_provided"])
        self.assertEqual(review["claims"][0]["evidence_strength"], "self-attested")


if __name__ == "__main__":
    unittest.main()
