# Mode WRITE: JKT Writing Skill (Artefak 2)

Goal: turn the user's research material into JKT-conformant text without adding anything the evidence does not support.

Read first: `generation_rules.yaml` (workflow, integrity), `style_profile.yaml` (targets), `pattern_database.yaml` → `grammar`, `paragraph_blueprints`, `writing_skill_handoff`, and `templates.md` → "Input form".

## 1. Choose the output mode

| User asks for | Output mode (`generation_rules.output_modes`) |
|---|---|
| outline, structure, "kerangka" | `planning_only` |
| one section ("tulis pendahuluan") | `section_draft` |
| whole article | `full_draft` |
| "with sources shown", thesis supervision, co-author review | `traceable_draft` (prose + paragraph source map + claim-evidence map) |
| final text to paste into the template | `clean_manuscript` (only after the quality gate passes) |

Default to `section_draft` for a single section and `traceable_draft` for a full article, unless the user asks for clean text.

## 2. Validate input

Check the input against `generation_rules.input_requirements`. Mark each group as complete, adequate, partial, or insufficient. If critical items are missing (objective, location, period, sample size, main results, sources), ask for them in one compact list (see `templates.md`). If the user wants to proceed anyway, draft with placeholders. Never fill gaps with plausible-looking values.

## 3. Build maps before writing prose

Follow this order (it matches `generation_rules.workflow`):

1. **Objective map.** Number the objectives O1…On. Each must map to a method (M), a result (R), a discussion unit (D), and a conclusion statement (C): `O_i → M_i → R_i → D_i → C_i`.
2. **Claim-evidence map.** For every major claim, record the claim type (C1–C8 in `pattern_codebook.claim_types`) and its evidence (user data, table, figure, statistic, verified reference). Claims without evidence become placeholders or are dropped.
3. **Results skeleton.** One block per variable or analysis, in Methods order. Within each block list the dominant pattern, the highest and lowest values, the key contrast, any statistical result, and any anomaly.
4. **Discussion map.** For each result choose the comparison type (agreement, partial agreement, contrast, extension, no direct comparator) and the mechanism class (directly tested, supported by data, supported by literature, plausible but untested). Stop at the depth the evidence supports.

## 4. Draft sections in this order

Methods → Results and Discussion → Introduction → Conclusion → Abstract → Title → Keywords. Apply these blueprints:

**Materials and Methods.** Where + when (+ map figure) → design and sampling (name the design: purposive, random, stratified) → collection → field or lab measurement (instrument model) → derived variables (equation, symbol legend with units, source citation) → analysis (named test, α, software + version). Past tense. Cite adopted or modified protocols.

**Results and Discussion.** For each block:
- Open with the result or a pointer: "Table 2 shows…", "Berdasarkan Tabel 2, …", then the key values. Do not repeat every table value.
- Then one of the discussion units from `pattern_database.grammar.DISCUSSION_UNIT`:
  - DU-A `R → I → L`: result, what it indicates, supporting source.
  - DU-B `R → (C|B) → E → L`: internal comparison or classification against a criterion/standard, explanation, source.
  - DU-C `R → L(agree/contrast) → E(hedged) → L`: comparison with prior sites or values.
  - DU-E `R → I → M → L`: mechanism, only when supported.
- Include a contrasting study when one exists. The corpus rarely does this (4/14 articles), and doing it strengthens the argument.
- English manuscripts: finish with a synthesis block (integrated interpretation → management/scientific implication → limitation → future research). Indonesian manuscripts: optional but recommended.
- Hedging: *may, likely, suggests* / *diduga, dimungkinkan, mengindikasikan*. Never write "significant" without a test.

**Introduction** (3–5 paragraphs, ≈15–20% of body):
- P1: importance or context of the object or ecosystem, cited (about 2–5 sources).
- P2–P3: specific context (species, site, pressure) and prior knowledge, synthesised rather than listed author by author.
- Final paragraph: what prior studies did → contrastive gap (*However/Namun … remains limited / masih terbatas*) with known + unresolved + why it matters → *Therefore/Oleh karena itu* → objective (the same wording as the objective map) → optional expected contribution.
- Never claim "no previous study" unless the user confirms a search. Prefer "limited", "not yet examined in [site]".

**Conclusion** (one paragraph, 4–9 sentences, no citations): main finding answering O1 (…On) → key numbers identical to Results → interpretation → implication or recommendation supported by the findings → optional future research or limitation. No new data, variables, or references.

**Abstract** (≤ 250 words, one paragraph, no citations): 1–3 background sentences → optional gap → objective (sentence 2–4) → method (1–4 sentences: site, period, sampling, analysis) → numeric results → conclusion or implication. Compress in this order if too long: generic background, secondary method detail, secondary results, redundant interpretation. Indonesian manuscript: write the English abstract first, then the Indonesian *Abstrak* with the same content.

**Title** (≤ 12 words, no abbreviations or formulas): [variable/process/method] + [object/taxon (scientific name if central)] + [location last]. No claim, no question. Offer 2–3 options with word counts.

**Keywords:** 3–5, including the scientific name, location, topic, and method where relevant. Do not repeat the title verbatim if possible.

## 5. Quality gate (before returning text)

Run the checks in `generation_rules.quality_gate`, plus these:
- Objective contract complete for every O_i.
- Numbers identical across abstract, results, and conclusion.
- No unhedged causal verb on observational evidence.
- Every in-text citation appears in the reference list, and vice versa. APA 7 format.
- Guideline limits met (title, abstract, keywords). Report the counts.
- No placeholder left unflagged. List all remaining placeholders at the end.

If a check fails, fix it or flag it. Do not deliver `clean_manuscript` while critical placeholders remain.

## 6. Return format

1. The requested text.
2. A short conformity note: guideline counts (title words, abstract words, keywords) and the patterns applied (IDs).
3. Open items: placeholders, missing sources, claims that need the user's confirmation.
For `traceable_draft`, add the paragraph source map and claim-evidence map (formats in `templates.md`).
