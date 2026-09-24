---
name: jkt-writing-system
description: Write, audit, or corpus-analyse marine-science manuscripts for Jurnal Kelautan Tropis (JKT, Universitas Diponegoro), in English or Indonesian. Use when the user wants to draft or plan a JKT article or section (judul, abstrak, pendahuluan, metode, hasil dan pembahasan, kesimpulan), check or review a manuscript against JKT author guidelines and journal style, or extract writing patterns from a set of JKT articles. Do not use for other journals unless the user asks for a JKT-style comparison.
---

# JKT Writing System

An evidence-based system for Jurnal Kelautan Tropis manuscripts. It has three modes that share one ontology:

| Mode | Use when the user… | Main output | Instructions |
|---|---|---|---|
| **WRITE** | gives research data or notes and wants a plan, a section, or a full draft | JKT-conformant text + claim-evidence map | `references/mode_write.md` |
| **AUDIT** | gives a manuscript (text, .docx, .pdf) and wants it checked or revised | Audit report with severity-ranked findings | `references/mode_audit.md` |
| **DETECT** | gives a set of published JKT articles and wants patterns updated | Corpus profile + updated pattern database | `references/mode_detect.md` |

Pick the mode from the request. If it is unclear, ask one question: *"Do you want me to write, audit, or analyse a corpus?"* ("Mau saya tulis, audit, atau analisis korpus?"). Then read the mode file before doing anything else.

## Reference files (load only what the mode needs)

| File | Content | Loaded by |
|---|---|---|
| `references/style_profile.yaml` | Empirical JKT profile per section (ranges, move sequences, %) | WRITE, AUDIT |
| `references/pattern_database.yaml` | Pattern IDs with evidence, anti-patterns, grammar, blueprints, auditor criteria AUD-01…30 | WRITE, AUDIT, DETECT |
| `references/generation_rules.yaml` | Writing workflow, integrity rules, placeholders, output modes | WRITE |
| `references/audit_rules.yaml` | Severity scale, audit layers, finding record, diagnostic classes | AUDIT |
| `references/pattern_codebook.yaml` | Shared codes: moves, gap types, R&D units, citation functions | all |
| `references/annotation_codebook.yaml` | Operational annotation manual with boundary cases | DETECT (and AUDIT when tagging) |
| `references/templates.md` | Input form, output skeletons, audit report layout | WRITE, AUDIT |
| `references/baseline_rd_chains.txt` | Coded R&D discourse chains of the 14 baseline articles | DETECT |
| `scripts/jkt_metrics.py` | Measures a manuscript or a corpus (word counts, citation density, reference recency, residue, cross-checks) | AUDIT, DETECT |

The script needs Python 3 (standard library only; `pdftotext` for PDF input). Where code cannot run (for example some chat surfaces), compute the same measures manually and say so.

## Non-negotiable rules (all modes)

1. **Priority order:** scientific validity → evidence traceability → research logic → JKT author guidelines → JKT patterns → language polish. A style pattern never overrides a scientific or ethical requirement.
2. **Never fabricate.** No invented numbers, statistics, sample sizes, instruments, coordinates, species identities, DOIs, references, or literature findings. Use placeholders: `[REFERENCE REQUIRED]`, `[SAMPLE SIZE REQUIRED]`, `[STUDY PERIOD NOT PROVIDED]`, `[METHOD DETAIL REQUIRED]`, `[DATA REQUIRED]`.
3. **Every citation must be real and traceable** to a source the user supplied or one you verified. Each JKT discussion explanation is followed by a source (P(citation | explanation) = 0.71 in the corpus), so ask for sources rather than inventing them.
4. **Causality control.** Observational or correlational designs get associational or hedged verbs (*was associated with, may reflect, diduga berkaitan dengan*). Causal verbs (*causes, determines, menyebabkan, berpengaruh terhadap*) need an experimental design, a statistical test, or a cited mechanism. Unhedged causal claims appear in at least 7 of the 14 corpus articles, so treat this as a known weakness to avoid.
5. **One source for every number.** Abstract, objective, results, and conclusion must use identical values for the same quantity. In the corpus, 4 of 14 published articles break this.
6. **Keep the evidence layers apart.** Label rules as GUIDELINE (author guidelines), CORPUS (observed pattern), DOMAIN (method family), or LANGUAGE (EN vs ID). Never present a corpus pattern as a journal requirement.
7. **Provisional status.** The profile comes from one issue (Vol. 29(2), 2026; n = 14). Apply CORE-tier corpus patterns as SHOULD, not MUST. Only guideline rules are MUST. Tell the user this once when it matters.
8. **Original prose.** Learn function and sequence, never copy sentences from published articles.
9. **Language.** Reply in the user's language. Write the manuscript in the language the user chooses. An Indonesian manuscript still needs an English title and abstract (guideline).

## JKT at a glance (what "JKT style" means)

**Guideline rules (MUST):** title ≤ 12 words, no abbreviations or formulas · abstract ≤ 250 words, one paragraph · 3–5 keywords · sections Introduction, Materials and Methods, Results and Discussion (combined), Conclusion, References · Introduction ≈ 15–20% of length, containing background, literature, gap, and objective · APA 7 author–year, *et al.* for 3+ authors · ≤ 10 pages · Indonesian articles carry an English title and abstract.

**Corpus patterns (SHOULD, provisional):**
- **Title:** nominal, no result claim. Order is [variable/method] → [object/taxon/ecosystem] → [location], with the location last.
- **Abstract:** BG(1–3 sentences) → (gap) → objective (sentence 2–4) → method → numeric results → conclusion/implication. No citations.
- **Introduction:** 3–5 paragraphs, funnel from importance/context to the specific site. The final paragraph runs prior studies → contrastive gap (*However / Namun*) → *Therefore / Oleh karena itu* → objective (+ expected contribution). About 0.7 citations per sentence.
- **Methods:** location + time (+ map) → sampling → collection → measurement → derived variables (equation + symbol legend) → analysis (software + version).
- **Results and Discussion:** one block per variable, in the order of the Methods. Paragraphs open with a result or a Table/Figure pointer. Core unit: `R → I → L` or `R → (benchmark) → E → L`. Classify values against criteria or standards where relevant. English manuscripts usually close with a synthesis, implication, and limitation block.
- **Conclusion:** one paragraph, no citations. Main finding → key numbers → interpretation → implication or recommendation. Answers every objective, adds nothing new.
- **References:** about 25–47 entries, ≥ 68% from the last 10 years, DOIs where they exist.

Full grammar, blueprints, and ranges: `references/pattern_database.yaml` (sections `grammar`, `paragraph_blueprints`, `auditor_handoff`).

## Quick routing examples

- "Buatkan pendahuluan dari data ini…" → WRITE, section draft.
- "Tolong cek naskah saya sebelum submit ke JKT" + file → AUDIT, full audit.
- "Perbaiki bagian pembahasan sesuai gaya JKT" → AUDIT (diagnose) → WRITE (revise the smallest unit).
- "Ini 20 artikel JKT 2024, perbarui profil pola" → DETECT.
