import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


EVIDENCE_STRENGTHS = [
    "unsupported",
    "self-attested",
    "artifact-backed",
    "externally corroborated",
    "live-demonstrable",
]

_CONFIDENT_TERMS = {
    "approved",
    "certified",
    "prove",
    "proves",
    "proved",
    "validated",
    "guarantees",
    "guaranteed",
    "will",
    "always",
    "never",
    "ready",
    "complete",
    "definitive",
    "confirmed",
    "safe",
}

_PROOF_TERMS = {
    "prove",
    "proves",
    "proved",
    "proof",
    "validated",
    "validation",
    "verified",
    "confirmed",
    "evidence shows",
}

_WEAK_QUALIFIERS = {
    "believe",
    "think",
    "may",
    "might",
    "could",
    "appears",
    "suggests",
    "likely",
    "early",
    "initial",
}

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "the",
    "this",
    "to",
    "we",
    "with",
}


@dataclass
class EvidenceNote:
    text: str
    tokens: set
    strength: str
    label: str = ""
    evidence_type: str = ""
    scope_supported: str = ""
    limitations: str = ""
    corroboration_status: str = ""

    def summary(self) -> str:
        if not any((self.label, self.evidence_type, self.scope_supported, self.limitations, self.corroboration_status)):
            return self.text
        parts = []
        if self.label:
            parts.append(self.label)
        if self.evidence_type:
            parts.append(f"type: {self.evidence_type}")
        if self.scope_supported:
            parts.append(f"scope: {self.scope_supported}")
        if self.limitations:
            parts.append(f"limitations: {self.limitations}")
        if self.corroboration_status:
            parts.append(f"corroboration: {self.corroboration_status}")
        return "; ".join(parts)


@dataclass
class ClaimOccurrence:
    text: str
    start: int
    end: int
    line: int


def analyze_document(draft_text: str, evidence_text: str = "") -> Dict[str, object]:
    """Analyze a draft and return claim records plus a revised draft."""
    claim_occurrences = extract_claim_occurrences(draft_text)
    evidence_notes = parse_evidence_notes(evidence_text)
    claim_records = []

    for occurrence in claim_occurrences:
        claim = occurrence.text
        evidence = match_evidence(claim, evidence_notes)
        strength = evidence.strength if evidence else "unsupported"
        risk_flag = classify_risk(claim, evidence)
        claim_type = classify_claim_type(claim)
        rewrite = make_humility_rewrite(claim, strength, risk_flag, evidence)
        claim_records.append(
            {
                "claim": claim,
                "start": occurrence.start,
                "end": occurrence.end,
                "source_line": occurrence.line,
                "claim_type": claim_type,
                "evidence_provided": evidence.summary() if evidence else "No matching evidence note found.",
                "evidence_strength": strength,
                "risk_flag": risk_flag,
                "humility_rewrite": rewrite,
                "next_verification_step": next_verification_step(strength, claim_type),
            }
        )

    return {
        "source": draft_text,
        "evidence": evidence_text,
        "claims": claim_records,
        "revised_draft": render_revised_draft(draft_text, claim_records),
    }


def extract_claims(text: str) -> List[str]:
    return [occurrence.text for occurrence in extract_claim_occurrences(text)]


def extract_claim_occurrences(text: str) -> List[ClaimOccurrence]:
    claims: List[ClaimOccurrence] = []
    in_fence = False
    offset = 0
    for line_number, raw_line in enumerate(text.splitlines(keepends=True), start=1):
        line = raw_line.rstrip("\r\n")
        stripped = line.strip()
        if _is_fence_marker(stripped):
            in_fence = not in_fence
            offset += len(raw_line)
            continue
        if in_fence or _skip_markdown_line(stripped):
            offset += len(raw_line)
            continue

        leading_len = len(line) - len(line.lstrip())
        content = line.lstrip()
        bullet_match = re.match(r"^[-*]\s+", content)
        if bullet_match:
            leading_len += len(bullet_match.group(0))
            content = content[bullet_match.end() :]

        content_leading = len(content) - len(content.lstrip())
        leading_len += content_leading
        normalized = content.lstrip()
        sentence_offset = 0
        for sentence in _split_sentences(normalized):
            if _looks_like_claim(sentence):
                local_index = normalized.find(sentence, sentence_offset)
                if local_index == -1:
                    continue
                start = offset + leading_len + local_index
                end = start + len(sentence)
                claims.append(ClaimOccurrence(sentence, start, end, line_number))
                sentence_offset = local_index + len(sentence)
        offset += len(raw_line)
    return claims


def parse_evidence_notes(text: str) -> List[EvidenceNote]:
    notes: List[EvidenceNote] = []
    current: Optional[Dict[str, str]] = None
    unstructured_lines: List[str] = []
    saw_structured_note = False

    def flush_current() -> None:
        nonlocal current, saw_structured_note
        if not current:
            return
        notes.append(_structured_note(current))
        saw_structured_note = True
        current = None

    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            if cleaned.lower().startswith("## evidence:"):
                flush_current()
                current = {"label": cleaned.split(":", 1)[1].strip()}
            continue
        if current is not None:
            field_line = re.sub(r"^[-*]\s+", "", cleaned)
            if ":" in field_line:
                key, value = field_line.split(":", 1)
                current[_normalize_field_name(key)] = value.strip()
            else:
                current["text"] = " ".join(part for part in (current.get("text", ""), field_line) if part)
            continue
        cleaned = re.sub(r"^[-*]\s+", "", cleaned)
        unstructured_lines.append(cleaned)

    flush_current()
    if not saw_structured_note:
        for line in unstructured_lines:
            notes.append(_unstructured_note(line))
    return notes


def match_evidence(claim: str, notes: Iterable[EvidenceNote]) -> Optional[EvidenceNote]:
    claim_tokens = _tokens(claim)
    best_note = None
    best_score = 0.0
    for note in notes:
        score = _evidence_match_score(claim_tokens, note)
        if score > best_score:
            best_note = note
            best_score = score
    return best_note if best_score >= 0.25 else None


def infer_evidence_strength(note: str) -> str:
    lower = note.lower()
    if re.search(r"\b(no|not|without|missing|none)\b", lower):
        return "unsupported"
    if "live-demonstrable" in lower or "live demo" in lower or "demo command" in lower:
        return "live-demonstrable"
    if "externally corroborated" in lower or "third-party" in lower or "independent review" in lower:
        return "externally corroborated"
    if "artifact" in lower or "screenshot" in lower or "log" in lower or "commit" in lower or "file" in lower:
        return "artifact-backed"
    if "self-attested" in lower or "internal" in lower or "manual timing" in lower or "we observed" in lower:
        return "self-attested"
    return "self-attested"


def classify_claim_type(claim: str) -> str:
    lower = claim.lower()
    if _contains_term(lower, _PROOF_TERMS):
        return "proof claim"
    if re.search(r"\b\d+(\.\d+)?%?\b", lower) or any(term in lower for term in ("reduced", "increased", "faster", "slower")):
        return "qualified performance claim"
    if any(term in lower for term in ("live", "demo", "cli", "dashboard", "supports", "can ")):
        return "capability claim"
    if any(term in lower for term in _WEAK_QUALIFIERS):
        return "inferred claim"
    return "general claim"


def classify_risk(claim: str, evidence: Optional[EvidenceNote]) -> str:
    lower = claim.lower()
    strength = evidence.strength if evidence else "unsupported"
    evidence_lower = evidence.text.lower() if evidence else ""
    weak_strength = strength in {"unsupported", "self-attested"}
    risks: List[str] = []

    if weak_strength and _contains_term(lower, _CONFIDENT_TERMS):
        risks.append("uncertainty_laundering")
    if weak_strength and _contains_term(lower, _PROOF_TERMS):
        risks.append("proofwashing")
    if strength == "self-attested" and re.search(r"\b\d+(\.\d+)?%?\b", lower):
        risks.append("single-source_metric")
    if "no " in evidence_lower and _contains_term(lower, _CONFIDENT_TERMS):
        if "proofwashing" not in risks:
            risks.append("proofwashing")
    if evidence and has_scope_mismatch(claim, evidence):
        risks.append("scope_mismatch")
        if "proofwashing" not in risks:
            risks.append("proofwashing")

    return ", ".join(risks) if risks else "none"


def has_scope_mismatch(claim: str, evidence: EvidenceNote) -> bool:
    if evidence.strength != "artifact-backed":
        return False
    if not _claim_uses_broad_language(claim):
        return False
    if _evidence_is_limited(evidence):
        return True
    return False


def make_humility_rewrite(claim: str, strength: str, risk_flag: str, evidence: Optional[EvidenceNote]) -> str:
    plain_claim = claim.rstrip(".")
    sentence_claim = _lower_initial(plain_claim)
    if strength == "unsupported":
        return f"Current notes do not prove this claim: {plain_claim}. Treat it as unverified until supporting evidence is collected."
    if strength == "self-attested":
        scope = _scope_hint(evidence.text if evidence else "")
        return f"We have a self-attested indication that {sentence_claim}{scope}. This should be presented as preliminary, not proven."
    if strength == "artifact-backed":
        scope = evidence.scope_supported if evidence and evidence.scope_supported else "the narrower artifact shown"
        limitation = _unsupported_broad_scope(claim)
        if "scope_mismatch" in risk_flag:
            return f"{_sentence_from_scope(scope)} is supported by artifact-backed evidence. This does not establish {limitation}."
        return f"{_sentence_from_scope(scope)} is supported by artifact-backed evidence. External corroboration is still not established."
    if strength == "externally corroborated":
        return f"External evidence appears to support this claim: {plain_claim}. Keep the source and date visible."
    if strength == "live-demonstrable":
        return f"This appears live-demonstrable: {plain_claim}. The claim should stay tied to the demo command or observable run."
    return plain_claim


def next_verification_step(strength: str, claim_type: str) -> str:
    if strength == "unsupported":
        return "Collect a concrete artifact, reproducible run, or external source before using confident language."
    if strength == "self-attested":
        return "Repeat the check, save the artifact, and ask an independent reviewer or external source to corroborate it."
    if strength == "artifact-backed":
        return "Link the artifact and verify whether an independent source can corroborate the claim."
    if strength == "externally corroborated":
        return "Record the source, date, and scope limits so the claim does not drift beyond the evidence."
    if strength == "live-demonstrable":
        return "Keep the command or demo path reproducible and note the environment where it was observed."
    return "Review manually."


def render_markdown(review: Dict[str, object], review_only: bool = False) -> str:
    rows = [
        "# Humility Engine Claim Review",
        "",
        "## Claim Schema",
        "",
        "| source line | claim | claim type | evidence provided | evidence strength | risk flag | humility rewrite | next verification step |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for claim in review["claims"]:
        rows.append(
            "| "
            + " | ".join(
                _escape_table(str(claim[key]))
                for key in (
                    "source_line",
                    "claim",
                    "claim_type",
                    "evidence_provided",
                    "evidence_strength",
                    "risk_flag",
                    "humility_rewrite",
                    "next_verification_step",
                )
            )
            + " |"
        )

    if not review_only:
        rows.extend(
            [
                "",
                "## Revised Humility-Aware Draft",
                "",
                str(review["revised_draft"]).strip(),
            ]
        )

    rows.extend(
        [
            "",
            "## Boundary Note",
            "",
            "This review uses local heuristics. It can surface likely laundering or proofwashing, but it does not prove that a claim is true or false. Use the table as a manual review aid; do not auto-replace source documents with generated rewrites.",
            "",
        ]
    )
    return "\n".join(rows)


def render_revised_draft(draft_text: str, claim_records: List[Dict[str, str]]) -> str:
    pieces: List[str] = []
    cursor = 0
    for record in sorted(claim_records, key=lambda item: int(item["start"])):
        start = int(record["start"])
        end = int(record["end"])
        pieces.append(draft_text[cursor:start])
        pieces.append(record["humility_rewrite"])
        cursor = end
    pieces.append(draft_text[cursor:])
    return "".join(pieces)


def _split_sentences(text: str) -> List[str]:
    pieces = re.split(r"(?<=[.!?])\s+", text)
    return [piece.strip() for piece in pieces if piece.strip()]


def _is_fence_marker(stripped: str) -> bool:
    return stripped.startswith("```") or stripped.startswith("~~~")


def _skip_markdown_line(stripped: str) -> bool:
    if not stripped:
        return True
    if re.match(r"^#{1,6}\s+", stripped):
        return True
    if stripped.startswith(">"):
        return True
    if stripped.startswith("|"):
        return True
    if re.match(r"^:?-{3,}:?(\s*\|\s*:?-{3,}:?)*$", stripped):
        return True
    if _is_section_label(stripped):
        return True
    field_line = re.sub(r"^[-*]\s+", "", stripped).lower()
    structured_prefixes = (
        "evidence label:",
        "evidence strength:",
        "evidence type:",
        "scope supported:",
        "limitations:",
        "corroboration status:",
    )
    return field_line.startswith(structured_prefixes)


def _is_section_label(stripped: str) -> bool:
    if not stripped.endswith(":"):
        return False
    without_marker = re.sub(r"^[-*]\s+", "", stripped).rstrip(":").strip()
    return 0 < len(without_marker.split()) <= 8


def _looks_like_claim(sentence: str) -> bool:
    if len(sentence.split()) < 4:
        return False
    return bool(re.search(r"[A-Za-z]", sentence))


def _tokens(text: str) -> set:
    return {
        _token_root(token)
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in _STOPWORDS
    }


def _scope_hint(evidence: str) -> str:
    lower = evidence.lower()
    if "one internal run" in lower or "one manual" in lower:
        return " in one internal run"
    if "internal" in lower:
        return " in internal notes"
    return ""


def _escape_table(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def _contains_term(text: str, terms: Iterable[str]) -> bool:
    for term in terms:
        if " " in term:
            if term in text:
                return True
        elif re.search(rf"\b{re.escape(term)}\b", text):
            return True
    return False


def _lower_initial(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def _structured_note(fields: Dict[str, str]) -> EvidenceNote:
    label = fields.get("evidence_label", fields.get("label", "")).strip()
    strength = fields.get("evidence_strength", fields.get("strength", "")).strip() or "self-attested"
    evidence_type = fields.get("evidence_type", fields.get("type", "")).strip()
    scope_supported = fields.get("scope_supported", fields.get("scope", "")).strip()
    limitations = fields.get("limitations", "").strip()
    corroboration_status = fields.get("corroboration_status", fields.get("corroboration", "")).strip()
    text = " ".join(
        part
        for part in (
            label,
            f"evidence strength: {strength}" if strength else "",
            f"evidence type: {evidence_type}" if evidence_type else "",
            f"scope supported: {scope_supported}" if scope_supported else "",
            f"limitations: {limitations}" if limitations else "",
            f"corroboration status: {corroboration_status}" if corroboration_status else "",
            fields.get("text", ""),
        )
        if part
    )
    return EvidenceNote(
        text=text,
        tokens=_tokens(text),
        strength=_normalize_strength(strength, text),
        label=label,
        evidence_type=evidence_type,
        scope_supported=scope_supported,
        limitations=limitations,
        corroboration_status=corroboration_status,
    )


def _unstructured_note(line: str) -> EvidenceNote:
    return EvidenceNote(line, _tokens(line), infer_evidence_strength(line))


def _normalize_field_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _normalize_strength(strength: str, fallback_text: str) -> str:
    normalized = strength.lower().strip()
    return normalized if normalized in EVIDENCE_STRENGTHS else infer_evidence_strength(fallback_text)


def _claim_uses_broad_language(claim: str) -> bool:
    broad_terms = {
        "approved",
        "certified",
        "clinical",
        "compliant",
        "compliance",
        "customer",
        "customers",
        "enterprise",
        "enterprise-ready",
        "financial",
        "hospital",
        "hospitals",
        "legal",
        "medical",
        "organization",
        "organization-wide",
        "patient",
        "patients",
        "production",
        "production-ready",
        "proven",
        "regulated",
        "safe",
        "safety",
        "secure",
        "teams",
        "validated",
        "ready",
    }
    lower = claim.lower()
    return _contains_term(lower, broad_terms) or "will " in lower


def _evidence_is_limited(evidence: EvidenceNote) -> bool:
    combined = " ".join(
        part
        for part in (
            evidence.evidence_type,
            evidence.scope_supported,
            evidence.limitations,
            evidence.corroboration_status,
            evidence.text,
        )
        if part
    ).lower()
    limited_terms = {
        "local",
        "toy",
        "demo",
        "sample",
        "synthetic",
        "screenshot",
        "one run",
        "single run",
        "checklist",
        "none",
        "no external",
        "no customer",
        "no clinical",
        "no patient",
        "no hospital",
        "no production",
    }
    no_corroboration = evidence.corroboration_status.lower() in {"none", "no", "not corroborated", "uncorroborated"}
    return no_corroboration or any(term in combined for term in limited_terms)


def _unsupported_broad_scope(claim: str) -> str:
    lower = claim.lower()
    if any(term in lower for term in ("medical", "clinical", "hospital", "hospitals", "patient", "patients", "safe", "safety")):
        return "medical or clinical safety"
    if "legal" in lower or "financial" in lower:
        return "legal or financial reliability"
    if "certified" in lower or "approved" in lower:
        return "certification or approval"
    if "regulated" in lower and ("enterprise" in lower or "customers" in lower or "customer" in lower):
        return "regulated enterprise customer readiness"
    if "secure" in lower or "compliant" in lower or "compliance" in lower:
        return "security or compliance readiness"
    if "production" in lower:
        return "production readiness"
    if "enterprise" in lower:
        return "enterprise readiness"
    if "teams" in lower or "organization" in lower:
        return "organization-wide adoption or behavior change"
    return "the broader claim"


def _sentence_from_scope(scope: str) -> str:
    stripped = scope.strip().rstrip(".")
    if not stripped:
        return "The narrower artifact"
    first_word = stripped.split()[0].lower()
    if first_word in {"one", "the", "this", "that", "these", "those"}:
        return stripped[0].upper() + stripped[1:]
    article = "An" if stripped[:1].lower() in {"a", "e", "i", "o", "u"} else "A"
    return f"{article} {stripped}"


def _token_root(token: str) -> str:
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token


def _evidence_match_score(claim_tokens: set, note: EvidenceNote) -> float:
    label_score = 3.0 * len(claim_tokens & _tokens(note.label))
    scope_score = 2.0 * len(claim_tokens & _tokens(note.scope_supported))
    type_score = 1.0 * len(claim_tokens & _tokens(note.evidence_type))
    limitation_score = 0.25 * len(claim_tokens & _tokens(note.limitations))
    fallback_score = 0.5 * len(claim_tokens & note.tokens)
    structured_score = label_score + scope_score + type_score + limitation_score
    return structured_score if structured_score else fallback_score
