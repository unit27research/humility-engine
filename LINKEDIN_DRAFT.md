# LinkedIn Draft

Field note from a small local instrument I have been testing: AI-polished writing can make weak evidence sound stronger than it is.

Two useful labels:

**Uncertainty laundering**: uncertain, inferred, incomplete, or weakly supported information gets converted into confident language.

**Proofwashing**: thin evidence, like a screenshot, checklist, demo, or one run, gets dressed up as proof of a broader claim.

The tool is called Humility Engine. It is intentionally modest: a local CLI that reads a Markdown/text draft plus optional evidence notes, extracts likely claims, labels rough evidence strength, flags possible `proofwashing` / `scope_mismatch`, and outputs a review table for human judgment.

It does not verify truth. It does not prevent fraud. It does not certify safety, compliance, medical readiness, legal reliability, or factual accuracy. It is a heuristic review aid: proof before claim, boundary before scale, review before release.

Example:

Claim: “The model is safe for hospitals.”

Evidence: local checklist review on sample prompts; no clinical review, no patient data, no hospital pilot, no external validation.

Review result: artifact-backed evidence, but `scope_mismatch` / `proofwashing`; a local checklist does not establish medical or clinical safety.

I am not claiming originality over the phrase “uncertainty laundering.” I am using it as a useful category label for a practical review workflow.

Repo, once approved: [repo link]

Curious where people see this pattern most often: AI evals, portfolio claims, research summaries, public documentation, compliance/security language, or internal reports moving toward release?
