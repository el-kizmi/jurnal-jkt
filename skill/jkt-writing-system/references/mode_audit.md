# Mode AUDIT: JKT Style Auditor (Artefak 3)

Goal: diagnose a manuscript's scientific integrity, research logic, guideline compliance, and conformity with JKT patterns, then recommend the smallest revisions that fix it.

Read first: `audit_rules.yaml` (severity, layers, finding record, diagnostic classes), `pattern_database.yaml` → `auditor_handoff` (AUD-01…30 with corpus ranges) and `anti_patterns`, `style_profile.yaml`, and `templates.md` → "Audit report".

## 1. Intake

- Accept .docx, .pdf, .txt, .md, or pasted text. Identify the language (EN/ID), article type (research or review), domain (`pattern_codebook.domains`), and method family (field-index, lab, acoustic, sedimentology, modelling, other).
- Ask for the data tables or supplementary files only if needed to check numbers. Otherwise audit the text as given and state that limitation.

## 2. Measure (automated where possible)

Run:

```bash
python scripts/jkt_metrics.py manuscript <file> --year <publication-or-current-year> --format md
```

It reports title words, abstract words and sentences, keywords, section shares, citations per sentence by section, narrative-citation share, reference count, recency, DOI coverage, drafting residue, causal-verb sentences, numbers in the abstract or conclusion that do not appear in the body, and PASS/FLAG against guideline limits and corpus IQRs.

If Python is unavailable, measure manually: count words and citations and list abstract/conclusion numbers. Say that you measured manually.

## 3. Audit layers (in priority order)

**A. Scientific integrity** (`audit_rules.audit_layers.scientific_integrity`):
- Numeric consistency: abstract vs results vs conclusion vs tables (JKT-ANTI-001). Treat every script "numbers not found in body" item as a candidate to verify by reading.
- Causality: every causal verb must be backed by design, test, or cited mechanism (JKT-ANTI-002, AUD-19).
- Statistical language: "significant" only with a named test and p-value. Effect-size labels must match a stated scale (JKT-ANTI-007).
- Objective contract `O_i → M_i → R_i → D_i → C_i`: mark each as complete, partial, or broken.
- Method reproducibility: score location, period, sample size, sampling, instrument, analytical method, equation, software, and test on the 0–3 scale.
- Citations: in-text vs reference list (phantom types A–D in `audit_rules.citation_audit`), and whether each citation supports the specific proposition. Do not claim a reference is fake without verifying. Mark it `not_verifiable` instead.

**B. Rhetorical quality:**
- Tag abstract moves (AB-*), introduction moves (I1–I7), R&D units (R/Q/F/C/L/E/M/I/U/S/A/G/K/T), and conclusion moves (C1–C9), using `annotation_codebook.yaml` priority rules.
- Check the gap: explicit, placed in the last two paragraphs, known/unknown contrast, no unsupported "no previous study" claim.
- Check discussion depth: the share of R&D paragraphs reaching L3 or deeper should be at least 70% (corpus 81%). Flag result-only repetition blocks (JKT-ANTI-006).
- Conclusion: one paragraph, answers every objective, no new data or references, not result-only (JKT-ANTI-003).

**C. JKT conformity:**
- Guideline rules (AUD-01, 03, 07, 11, 28 and the section list): ENFORCE.
- Corpus patterns: classify as match, acceptable_variant, partial_match, or deviation. Weight provisional CORE-tier patterns at MODERATE at most, because the profile comes from one issue.
- Drafting residue (AUD-29): placeholders, "(referensi)", future tense in Methods, captions in the wrong language, "TODO".
- Duplicated paragraphs (AUD-30).

## 4. Severity

Use `audit_rules.finding_severity`:
- **CRITICAL:** compromises validity (contradictory key numbers, conclusion unsupported, central causal overclaim, fabricated or untraceable major reference, objective never analysed).
- **MAJOR:** weak or unsupported gap, non-reproducible core method, discussion that only repeats results, missing key literature comparison, guideline violations likely to trigger desk rejection (e.g. abstract far above 250 words, missing required section).
- **MODERATE:** paragraph architecture, citation placement, redundancy, overloaded title, pattern deviations.
- **MINOR:** language and formatting.

A corpus-pattern deviation alone is never above MODERATE.

## 5. Report

Follow `templates.md` → "Audit report":
1. Executive diagnosis: status class (`audit_rules.overall_diagnostic_classes`), highest severity, counts, and the primary structural, scientific, and conformity weakness.
2. Metrics table (script output with PASS/FLAG).
3. Findings table sorted by severity. Each finding has: finding_id, section, location (paragraph/sentence), severity, layer, problem, evidence (short quote ≤ 15 words or measurement), expected standard (guideline ID, pattern ID, or AUD ID), why it matters, recommended revision, confidence, status = open.
4. Scientific logic matrix (objective contract) and JKT conformity matrix (section × pattern → match/variant/deviation).
5. Revision plan in `audit_rules.revision_priority` order, revising the smallest unit.

No single overall score and no prediction of acceptance (`no_single_score_rule`, `publication_probability_prediction: false`). The status cannot be AUDIT_READY while any CRITICAL finding is open.

## 6. Revision and re-audit

If the user asks for fixes, switch to WRITE for the affected units only. After revising, re-audit with `audit_rules.re_audit`: mark each finding resolved, partially resolved, unresolved, or new issue introduced. Check for regressions: changed numbers, new unsupported claims, citation mismatches, lost method detail.
