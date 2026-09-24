# Mode DETECT: JKT Pattern-Detection (Artefak 1)

Goal: derive or update empirical JKT writing patterns from published articles. Learn structure, function, sequence, and evidence, never surface wording. The output updates `style_profile.yaml` and `pattern_database.yaml`.

Read first: `annotation_codebook.yaml` (coding manual and priority rules), `pattern_codebook.yaml` (codes, frequency classes, confidence), and the header of `pattern_database.yaml` (current evidence ceiling).

## Principles

- Distinguish EDITORIAL CONSTRAINT ≠ CORPUS PATTERN ≠ DOMAIN PATTERN ≠ AUTHOR-CLUSTER ≠ LANGUAGE PATTERN.
- A feature seen in one article, one author group, one domain, or one issue is not a journal pattern.
- "No stable pattern detected" is a valid result.
- Never fabricate frequencies. Use NOT_DETERMINED where extraction is unreliable.
- Do not quote distinctive sentences from the corpus. Store codes and abstractions.

## Pipeline

1. **Intake report (always the first response).** Articles received, eligible, excluded (duplicates by hash, reviews, editorials), years, issues, languages, domains, author clusters (shared authors or institutions), missing information, sampling bias, current confidence.
2. **Metrics.** Run
   ```bash
   python scripts/jkt_metrics.py corpus <folder-of-pdfs-or-txt> --out corpus_metrics.json
   ```
   It gives per-article section word counts, paragraph and sentence counts, citation density, narrative-citation share, reference count, recency, DOI coverage, title and abstract counts, and corpus medians and IQRs split by language.
3. **Manual coding** with `annotation_codebook.yaml`:
   - Abstract: move string per sentence (AB-*).
   - Introduction: paragraph map, scope 5→1, gap visibility and type, objective position and connective.
   - Methods: component sequence M1–M16.
   - R&D: one chain per paragraph using R F C L LX B E M I U S G K A T D X. Here `B` is benchmark classification, `LX` is contrasting literature, `D` is definition, and `X` is method restatement. Q is folded into R. Store chains as `id|chain;chain;…`, one line per article (format and baseline coding of the 14-article corpus: `references/baseline_rd_chains.txt`).
   - Conclusion: C1–C9 sequence, objective alignment, new information.
   - Anomalies: numeric contradictions between sections, residue, duplicates.
4. **Aggregate.** Frequency = articles with the pattern ÷ eligible articles. Tier: CORE ≥ 80, COMMON 60–79, VARIABLE 30–59, RARE < 30. For R&D, also compute paragraph opening and closing distributions, transitions P(next | current), and the deepest unit per paragraph (L1 R/F/D/X/S/T, L2 C/B/L/LX, L3 E/I/U, L4 M, L5 G/K/A).
5. **Effect tests.** Split by language (EN/ID), method family, author cluster, and year or issue. Label a pattern DOMAIN, LANGUAGE, or AUTHOR-CLUSTER when it concentrates in one group.
6. **Confidence.** MODERATE or higher only if the tier is ≥ COMMON, the pattern holds in both languages and in most independent author units, and appears in ≥ 2 issues. JKT-CORE status requires ≥ 30 articles, ≥ 2 years, and holdout validation (hold out 10–20% before building rules, then test predictions of objective position, abstract order, R&D chains, and conclusion shape).
7. **Update outputs.**
   - `style_profile.yaml`: replace values and update `profile_status`, `corpus_period`, `corpus_size`, `saturation_status`.
   - `pattern_database.yaml`: pattern records (`pattern_codebook.pattern_record_template`), anti-patterns, grammar, `writing_skill_handoff`, `auditor_handoff` ranges.
   - Keep the previous version, and record what changed and why in a changelog comment at the top of each file.
8. **Report** to the user: corpus composition, the patterns that changed tier or confidence, new or rejected patterns, and remaining limits.

## Current baseline (v1.1)

14 articles from Vol. 29(2), June 2026: 7 EN, 7 ID; 5-article Universitas Diponegoro author cluster; 187 R&D paragraphs coded; saturation not reached; no holdout. Highest-value next step: add issues from 2024–2026 (target n ≥ 50) and reserve a holdout set.
