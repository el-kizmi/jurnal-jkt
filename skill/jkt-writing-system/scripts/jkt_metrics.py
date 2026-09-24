#!/usr/bin/env python3
"""JKT metrics: measure a manuscript (AUDIT) or a corpus of articles (DETECT).

Standard library only. PDF input needs `pdftotext` (poppler) on PATH.

Usage:
  python jkt_metrics.py manuscript <file.docx|.pdf|.txt|.md> [--year 2026] [--format md|json]
  python jkt_metrics.py corpus <folder> [--year 2026] [--out corpus_metrics.json]

Numbers are heuristics for screening. Verify every FLAG by reading the text.
"""
import argparse, json, os, re, shutil, statistics as st, subprocess, sys, zipfile
from datetime import date

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------- reference ranges
# Guideline limits (JKT author guidelines) and corpus IQRs (Vol. 29(2), n = 14; provisional)
GUIDE = {"title_words_max": 12, "abstract_words_max": 250, "keywords_min": 3, "keywords_max": 5,
         "intro_share_min": 15, "intro_share_max": 20}
CORPUS = {"abstract_words": (200, 248), "abstract_sents": (8, 10.25), "intro_paras": (3, 5),
          "intro_share": (14.2, 19.8), "rd_share": (51.9, 60.5), "cd_intro": (0.56, 1.07),
          "cd_meth": (0.29, 0.48), "cd_rd": (0.29, 0.48), "conc_sents": (4, 9), "conc_words": (87, 186),
          "refs": (24.75, 47), "recent10": (0.68, 0.86), "recent5": (0.28, 0.66), "doi": (0.47, 0.90)}

HEAD = [
    ("ABSTRACT", r"^(abstract)\s*:?$"),
    ("ABSTRAK", r"^(abstrak)\s*:?$"),
    ("INTRO", r"^(\d+\.?\s*)?(introduction|pendahuluan)\s*$"),
    ("METH", r"^(\d+\.?\s*)?(materials?\s+(and|&)\s+methods?|methods?|methodology|materi\s+dan\s+metode|metode(\s+penelitian)?|bahan\s+dan\s+metode)\s*$"),
    ("RD", r"^(\d+\.?\s*)?(results?\s+(and|&)\s+discussions?|hasil\s+(dan|&)\s+pembahasan)\s*$"),
    ("CONC", r"^(\d+\.?\s*)?(conclus+ions?|kesimpulan(\s+dan\s+saran)?|simpulan)\s*$"),
    ("ACK", r"^(acknowledge?ments?|ucapan\s+terima\s*kasih)\s*$"),
    ("REF", r"^(references?|daftar\s+pustaka|bibliography)\s*$"),
]
NOISE = [r"^Jurnal Kelautan Tropis", r"^P-ISSN", r"^\d{1,3}$", r"et al\.\)\s*$", r"^\*\) ?Corresponding",
         r"^Diterima/Received", r"^www\.ejournal"]
YR = r"(?:19|20)\d{2}[a-z]?"
PAREN = re.compile(r"\(([^()]*?" + YR + r"[^()]*?)\)")
NARR = re.compile(r"[A-Z][A-Za-z\-']+(?: et al\.| dkk\.| (?:and|dan|&) [A-Z][A-Za-z\-']+)?,? \(" + YR + r"(?:[;,] ?" + YR + r")*\)")
ABBR = r"(et al|sp|spp|e\.g|i\.e|Fig|Figs|No|vs|cf|ca|approx|var|subsp|Tab|dkk|dll|dsb|Dr|Prof|St|ind|[A-Z])"
CAUSAL = {
    "EN": r"\b(causes?|caused by|causing|determines?|determined by|results? in|resulted in|leads? to|led to|due to|because of|affects?|affected|effect of|influenced by|driven by)\b",
    "ID": r"\b(menyebabkan|disebabkan|mengakibatkan|diakibatkan|akibat|karena|dipengaruhi|mempengaruhi|memengaruhi|berpengaruh)\b",
}
HEDGE = {
    "EN": r"\b(may|might|could|likely|possibly|probably|suggests?|suggesting|presumably|appears? to|is thought to|are thought to|associated with|related to)\b",
    "ID": r"\b(diduga|dimungkinkan|kemungkinan|diperkirakan|mungkin|dapat|cenderung|berkaitan|berhubungan|mengindikasikan)\b",
}
RESIDUE = [
    (r"\((referensi|reference|citation needed|ref)\)", "citation placeholder"),
    (r"\[(REFERENCE|SAMPLE SIZE|STUDY PERIOD|METHOD DETAIL|DATA) [A-Z ]*\]", "skill placeholder not resolved"),
    (r"\b(TODO|TBD|XXX)\b|\?\?", "to-do marker"),
    (r"\bwill be (collected|conducted|carried out|analy[sz]ed|measured|used)\b", "future tense (proposal residue)"),
    (r"\bakan (dilakukan|dianalisis|diukur|dikumpulkan|digunakan)\b", "future tense (proposal residue)"),
    (r"\bet al\s", "'et al' without period"),
]


# ---------------------------------------------------------------- reading
def read_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<w:tab/>", "\t", xml)
        txt = re.sub(r"<[^>]+>", "", xml)
        for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'")):
            txt = txt.replace(a, b)
        return txt
    if ext == ".pdf":
        if not shutil.which("pdftotext"):
            sys.exit("pdftotext not found. Install poppler-utils, or convert the PDF to .txt first.")
        return subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def lang_of(text):
    t = text.lower()
    id_hits = len(re.findall(r"\b(yang|dan|dengan|pada|untuk|dalam|ini|adalah|penelitian)\b", t))
    en_hits = len(re.findall(r"\b(the|and|with|of|for|in|this|is|study)\b", t))
    return "ID" if id_hits > en_hits else "EN"


def split_sections(text):
    lines = text.split("\n")
    ref_pat = dict(HEAD)["REF"]
    ref_idx = [i for i, l in enumerate(lines) if re.match(ref_pat, l.strip().strip("*#").strip(), re.I)]
    last_ref = ref_idx[-1] if ref_idx else -1  # a table cell "Reference" must not start the reference list
    sec, cur, order = {"FRONT": []}, "FRONT", ["FRONT"]
    for i, l in enumerate(lines):
        s = l.strip().strip("*#").strip()
        hit = None
        for key, pat in HEAD:
            if key == "REF" and i != last_ref:
                continue
            if re.match(pat, s, re.I) and key not in sec:
                hit = key
                break
        if hit:
            cur = hit
            sec[cur] = []
            order.append(cur)
            continue
        if not any(re.search(p, s) for p in NOISE):
            sec[cur].append(l.rstrip())
    return sec, order


def paragraphs(lines):
    """Prose paragraphs: join wrapped lines until a blank line or sentence-final punctuation.
    Short lines (table cells, headings, captions fragments) are skipped; blocks < 20 words are dropped."""
    out, buf = [], ""
    for l in lines:
        s = l.strip()
        if not s:
            if len(buf.split()) >= 20:
                out.append(buf)
            buf = ""
            continue
        if len(s.split()) < 8 and not buf:
            continue
        buf = (buf + " " + s).strip()
        if re.search(r"[.!?)\]]['\"”]?$", s):
            if len(buf.split()) >= 20:
                out.append(buf)
            buf = ""
    if len(buf.split()) >= 20:
        out.append(buf)
    return out


def sentences(p):
    t = re.sub(r"\b" + ABBR + r"\.", lambda m: m.group(0).replace(".", "§"), p)
    t = re.sub(r"(\d)\.(\d)", r"\1§\2", t)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(“\"])", t)
    return [s.replace("§", ".") for s in parts if len(s.split()) >= 3]


def count_citations(text):
    par = 0
    for m in PAREN.finditer(text):
        inner = m.group(1)
        if re.fullmatch(r"\s*" + YR + r"(\s*[,;]\s*" + YR + r")*\s*", inner):
            continue
        n = len(re.findall(YR, inner))
        if re.search(r"[A-Z][a-z]", inner) and n:
            par += n
    nar = len(NARR.findall(text))
    return par + nar, nar


def ref_stats(ref_lines, year):
    t = " ".join(l.strip() for l in ref_lines)
    anchors = re.findall(r"\(((?:19|20)\d{2})[a-z]?(?:, [A-Z][a-z]+[^)]{0,12})?\)\.", t)  # APA "(2020)." / "(2020, March 3)."
    if len(anchors) < 3:  # non-APA fallback: "Author. 2019." or line-start entries
        anchors = re.findall(r"(?:^|\.\s)((?:19|20)\d{2})[a-z]?\.", t)
    yrs = [int(y) for y in anchors]
    n = len(yrs)
    doi = len(re.findall(r"(?:doi:?\s*|doi\.org/)10\.\d{4,}", t, re.I))
    ages = [year - y for y in yrs]
    return {"n": n, "recent5": round(sum(a <= 5 for a in ages) / n, 2) if n else None,
            "recent10": round(sum(a <= 10 for a in ages) / n, 2) if n else None,
            "doi_ratio": round(doi / n, 2) if n else None,
            "median_year": st.median(yrs) if yrs else None}


def section_stats(lines, lang):
    P = paragraphs(lines)
    txt = " ".join(P)
    S = [s for p in P for s in sentences(p)]
    cit, nar = count_citations(txt)
    w = len(txt.split())
    return {"paras": len(P), "sents": len(S), "words": w, "citations": cit, "narrative": nar,
            "cd_s": round(cit / len(S), 2) if S else 0.0, "sent_len": round(w / len(S), 1) if S else 0.0,
            "_paras": P, "_sents": S}


# ---------------------------------------------------------------- manuscript
def analyse(path, year):
    raw = read_text(path)
    lang = lang_of(raw)
    sec, order = split_sections(raw)
    front = [l for l in sec["FRONT"] if l.strip()]
    title = front[0].strip() if front else ""
    if len(front) > 1 and len(front[1].split()) <= 3 and not re.search(r"[\d*@,]", front[1]):
        title += " " + front[1].strip()  # title wrapped onto a second short line
    # abstract: explicit heading, else FRONT text before keywords
    abs_lines = sec.get("ABSTRACT") or sec.get("ABSTRAK") or front[1:]
    abs_txt, kw = [], ""
    for l in abs_lines:
        m = re.match(r"^\s*(key\s*words?|kata\s*kunci)\s*:?\s*(.*)$", l.strip(), re.I)
        if m:
            kw = m.group(2)
            break
        abs_txt.append(l.strip())
    if not kw:
        m = re.search(r"(key\s*words?|kata\s*kunci)\s*:?\s*(.+)", raw, re.I)
        kw = m.group(2).split("\n")[0] if m else ""
    abs_lines2 = [l for l in abs_txt if l]
    # drop an English title line inside the abstract block (ID articles)
    if lang == "ID" and abs_lines2 and len(abs_lines2[0].split()) < 30 and not abs_lines2[0].endswith("."):
        abs_lines2 = abs_lines2[1:]
    abstract = " ".join(abs_lines2)
    keywords = [k.strip() for k in re.split(r"[;,]", kw.strip().rstrip(".")) if k.strip()]

    body = {k: section_stats(sec[k], lang) for k in ("INTRO", "METH", "RD", "CONC") if k in sec}
    total = sum(v["words"] for v in body.values()) or 1
    refs = ref_stats(sec.get("REF", []), year)

    # residue
    residue = []
    for pat, label in RESIDUE:
        for m in re.finditer(pat, raw, re.I if "TODO" not in pat else 0):
            ctx = raw[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")
            residue.append({"type": label, "context": ctx.strip()})

    # unhedged causal sentences in R&D and conclusion
    causal = []
    for k in ("RD", "CONC"):
        if k not in body:
            continue
        for s in body[k]["_sents"]:
            if re.search(CAUSAL[lang], s, re.I) and not re.search(HEDGE[lang], s, re.I):
                causal.append({"section": k, "sentence": s[:220]})

    # numbers in abstract / conclusion missing from the body
    def nums(t):
        return set(re.findall(r"(?<![\w.])\d+(?:[.,]\d+)?(?![\w])", t))
    body_txt = " ".join(" ".join(body[k]["_paras"]) for k in ("INTRO", "METH", "RD") if k in body)
    body_txt += " " + " ".join(sec.get("RD", []))  # include table text
    body_nums = {n.replace(",", ".") for n in nums(body_txt)}
    def missing(t):
        out = []
        for n in sorted(nums(t)):
            nn = n.replace(",", ".")
            if nn in body_nums or re.fullmatch(r"(19|20)\d{2}", n) or len(nn.replace(".", "")) < 2:
                continue
            out.append(n)
        return out
    miss_abs = missing(abstract)
    miss_conc = missing(" ".join(body["CONC"]["_paras"])) if "CONC" in body else []

    # duplicate paragraphs (near-verbatim)
    allp = [p for k in body for p in body[k]["_paras"]]
    dups = []
    for i in range(len(allp)):
        wi = set(allp[i].lower().split())
        for j in range(i + 1, len(allp)):
            wj = set(allp[j].lower().split())
            if len(wi) > 40 and len(wj) > 40 and len(wi & wj) / min(len(wi), len(wj)) > 0.8:
                dups.append([allp[i][:90], allp[j][:90]])

    cit_all = sum(v["citations"] for v in body.values())
    nar_all = sum(v["narrative"] for v in body.values())
    out = {
        "file": os.path.basename(path), "language": lang, "sections_found": [s for s in order if s != "FRONT"],
        "title": title, "title_words": len(title.replace("–", " ").split()),
        "abstract_words": len(abstract.split()), "abstract_sentences": len(sentences(abstract)) if abstract else 0,
        "abstract_has_citation": bool(PAREN.search(abstract) and re.search(r"[A-Z][a-z]+.*" + YR, abstract)),
        "keywords": keywords, "keywords_n": len(keywords),
        "sections": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in body.items()},
        "shares_pct": {k: round(100 * v["words"] / total, 1) for k, v in body.items()},
        "narrative_citation_share": round(nar_all / cit_all, 2) if cit_all else None,
        "references": refs, "residue": residue, "unhedged_causal_sentences": causal,
        "numbers_in_abstract_not_in_body": miss_abs, "numbers_in_conclusion_not_in_body": miss_conc,
        "possible_duplicate_paragraphs": dups,
    }
    out["checks"] = checks(out)
    return out


def rng(v, lo, hi):
    if v is None:
        return "N/A"
    return "PASS" if lo <= v <= hi else "FLAG"


def checks(m):
    s, sh, r = m["sections"], m["shares_pct"], m["references"]
    c = []
    add = lambda aud, crit, val, guide, corpus, res: c.append(
        {"AUD": aud, "criterion": crit, "value": val, "guideline": guide, "corpus_IQR": corpus, "result": res})
    add("AUD-01", "Title words", m["title_words"], "<= 12", "11.75-17",
        "PASS" if m["title_words"] <= GUIDE["title_words_max"] else "FLAG (guideline)")
    add("AUD-03", "Abstract words", m["abstract_words"], "<= 250", "200-248",
        "PASS" if 0 < m["abstract_words"] <= GUIDE["abstract_words_max"] else "FLAG (guideline)")
    add("AUD-06", "Abstract citations", m["abstract_has_citation"], "-", "0/14", "FLAG" if m["abstract_has_citation"] else "PASS")
    add("AUD-07", "Keywords", m["keywords_n"], "3-5", "3-6",
        "PASS" if GUIDE["keywords_min"] <= m["keywords_n"] <= GUIDE["keywords_max"] else "FLAG (guideline)")
    for key, name in (("INTRO", "Introduction"), ("METH", "Methods"), ("RD", "Results and Discussion"), ("CONC", "Conclusion")):
        add("SEC", f"Section present: {name}", key in s, "required", "14/14", "PASS" if key in s else "FLAG (guideline)")
    if "INTRO" in s:
        add("AUD-10", "Introduction paragraphs", s["INTRO"]["paras"], "-", "3-5", rng(s["INTRO"]["paras"], *CORPUS["intro_paras"]))
        add("AUD-11", "Introduction share of body (%)", sh.get("INTRO"), "15-20", "14.2-19.8",
            "PASS" if GUIDE["intro_share_min"] <= sh.get("INTRO", 0) <= GUIDE["intro_share_max"] else "FLAG (guideline)")
        add("AUD-12", "Introduction citations/sentence", s["INTRO"]["cd_s"], "-", "0.56-1.07", rng(s["INTRO"]["cd_s"], *CORPUS["cd_intro"]))
    if "METH" in s:
        add("AUD-14", "Methods citations/sentence", s["METH"]["cd_s"], "-", "0.29-0.48", rng(s["METH"]["cd_s"], *CORPUS["cd_meth"]))
    if "RD" in s:
        add("AUD-15", "R&D share of body (%)", sh.get("RD"), "-", "51.9-60.5", rng(sh.get("RD"), *CORPUS["rd_share"]))
        add("AUD-16", "R&D citations/sentence", s["RD"]["cd_s"], "-", "0.29-0.48", rng(s["RD"]["cd_s"], *CORPUS["cd_rd"]))
    if "CONC" in s:
        add("AUD-20", "Conclusion paragraphs", s["CONC"]["paras"], "-", "1", "PASS" if s["CONC"]["paras"] <= 1 else "FLAG")
        add("AUD-20", "Conclusion sentences", s["CONC"]["sents"], "-", "4-9", rng(s["CONC"]["sents"], *CORPUS["conc_sents"]))
        add("AUD-20", "Conclusion citations", s["CONC"]["citations"], "-", "0", "PASS" if s["CONC"]["citations"] == 0 else "FLAG")
    add("AUD-23", "Numbers in abstract/conclusion not found in body",
        len(m["numbers_in_abstract_not_in_body"]) + len(m["numbers_in_conclusion_not_in_body"]), "0", "0",
        "PASS" if not (m["numbers_in_abstract_not_in_body"] or m["numbers_in_conclusion_not_in_body"]) else "VERIFY")
    add("AUD-19", "Unhedged causal sentences (R&D, Conclusion)", len(m["unhedged_causal_sentences"]), "-", "-",
        "PASS" if not m["unhedged_causal_sentences"] else "VERIFY")
    add("AUD-24", "References", r["n"], "-", "24.75-47", rng(r["n"], *CORPUS["refs"]))
    add("AUD-25", "References <= 10 years", r["recent10"], "-", ">= 0.68", "N/A" if r["recent10"] is None else ("PASS" if r["recent10"] >= 0.68 else "FLAG"))
    add("AUD-26", "References <= 5 years", r["recent5"], "-", "0.28-0.66", rng(r["recent5"], *CORPUS["recent5"]))
    add("AUD-27", "DOI coverage", r["doi_ratio"], "-", ">= 0.47", "N/A" if r["doi_ratio"] is None else ("PASS" if r["doi_ratio"] >= 0.47 else "FLAG"))
    add("AUD-29", "Drafting residue", len(m["residue"]), "0", "0", "PASS" if not m["residue"] else "FLAG")
    add("AUD-30", "Possible duplicate paragraphs", len(m["possible_duplicate_paragraphs"]), "0", "0",
        "PASS" if not m["possible_duplicate_paragraphs"] else "VERIFY")
    return c


def to_md(m):
    L = [f"# JKT metrics: {m['file']}", "",
         f"- Language: **{m['language']}** · Sections found: {', '.join(m['sections_found']) or 'none detected'}",
         f"- Title ({m['title_words']} words): {m['title']}",
         f"- Abstract: {m['abstract_words']} words, {m['abstract_sentences']} sentences · Keywords ({m['keywords_n']}): {'; '.join(m['keywords'])}",
         f"- Section shares (% of body prose): {m['shares_pct']}",
         f"- Narrative-citation share: {m['narrative_citation_share']}", "",
         "| AUD | Criterion | Value | Guideline | Corpus IQR | Result |", "|---|---|---|---|---|---|"]
    for c in m["checks"]:
        L.append(f"| {c['AUD']} | {c['criterion']} | {c['value']} | {c['guideline']} | {c['corpus_IQR']} | {c['result']} |")
    L += ["", "## Section statistics", "", "| Section | Paragraphs | Sentences | Words | Citations | Cit./sentence | Mean sentence length |", "|---|---|---|---|---|---|---|"]
    for k, v in m["sections"].items():
        L.append(f"| {k} | {v['paras']} | {v['sents']} | {v['words']} | {v['citations']} | {v['cd_s']} | {v['sent_len']} |")
    if m["numbers_in_abstract_not_in_body"] or m["numbers_in_conclusion_not_in_body"]:
        L += ["", "## Numbers to verify (appear in abstract/conclusion but not in body prose or R&D text)",
              f"- Abstract: {', '.join(m['numbers_in_abstract_not_in_body']) or '-'}",
              f"- Conclusion: {', '.join(m['numbers_in_conclusion_not_in_body']) or '-'}"]
    if m["unhedged_causal_sentences"]:
        L += ["", "## Unhedged causal sentences (check design / test / cited mechanism)"]
        L += [f"- [{c['section']}] {c['sentence']}" for c in m["unhedged_causal_sentences"][:25]]
    if m["residue"]:
        L += ["", "## Drafting residue"] + [f"- {r['type']}: …{r['context']}…" for r in m["residue"][:25]]
    if m["possible_duplicate_paragraphs"]:
        L += ["", "## Possible duplicate paragraphs"] + [f"- \"{a}…\" ≈ \"{b}…\"" for a, b in m["possible_duplicate_paragraphs"]]
    L += ["", "_Heuristic screening. PASS/FLAG against JKT guidelines and a provisional corpus profile (Vol. 29(2), n = 14). Verify every FLAG/VERIFY by reading._"]
    return "\n".join(L)


# ---------------------------------------------------------------- corpus
def describe(vals):
    v = sorted(x for x in vals if x is not None)
    if not v:
        return None
    q = st.quantiles(v, n=4) if len(v) >= 4 else [v[0], st.median(v), v[-1]]
    return {"n": len(v), "median": round(st.median(v), 2), "IQR": [round(q[0], 2), round(q[2], 2)], "min": v[0], "max": v[-1]}


def corpus(folder, year, out):
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith((".pdf", ".txt", ".md", ".docx")))
    import hashlib
    seen, rows, dup = {}, [], []
    for f in files:
        p = os.path.join(folder, f)
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        if h in seen:
            dup.append([f, seen[h]])
            continue
        seen[h] = f
        try:
            m = analyse(p, year)
        except Exception as e:  # keep going on bad files
            rows.append({"file": f, "error": str(e)})
            continue
        m.pop("checks", None)
        rows.append(m)
    ok = [r for r in rows if "error" not in r]
    summary = {}
    for lang in ("ALL", "EN", "ID"):
        sub = [r for r in ok if lang == "ALL" or r["language"] == lang]
        if not sub:
            continue
        g = lambda f: describe([f(r) for r in sub])
        sec = lambda k, key: (lambda r: r["sections"].get(k, {}).get(key))
        summary[lang] = {
            "n": len(sub),
            "title_words": g(lambda r: r["title_words"]), "abstract_words": g(lambda r: r["abstract_words"]),
            "abstract_sentences": g(lambda r: r["abstract_sentences"]), "keywords": g(lambda r: r["keywords_n"]),
            "intro_paras": g(sec("INTRO", "paras")), "intro_share": g(lambda r: r["shares_pct"].get("INTRO")),
            "rd_share": g(lambda r: r["shares_pct"].get("RD")), "cd_intro": g(sec("INTRO", "cd_s")),
            "cd_meth": g(sec("METH", "cd_s")), "cd_rd": g(sec("RD", "cd_s")), "conc_sents": g(sec("CONC", "sents")),
            "refs": g(lambda r: r["references"]["n"]), "recent5": g(lambda r: r["references"]["recent5"]),
            "recent10": g(lambda r: r["references"]["recent10"]), "doi": g(lambda r: r["references"]["doi_ratio"]),
            "narrative_share": g(lambda r: r["narrative_citation_share"]),
        }
    res = {"folder": folder, "files": len(files), "duplicates_excluded": dup, "analysed": len(ok),
           "errors": [r for r in rows if "error" in r], "summary": summary, "articles": rows}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print(f"Analysed {len(ok)} of {len(files)} files ({len(dup)} duplicates excluded). Written: {out}")
    for lang, s in summary.items():
        print(f"\n[{lang}] n={s['n']}")
        for k, v in s.items():
            if isinstance(v, dict):
                print(f"  {k:18} median={v['median']} IQR={v['IQR']} range={v['min']}–{v['max']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("manuscript")
    a.add_argument("file")
    a.add_argument("--year", type=int, default=date.today().year)
    a.add_argument("--format", choices=["md", "json"], default="md")
    b = sp.add_parser("corpus")
    b.add_argument("folder")
    b.add_argument("--year", type=int, default=date.today().year)
    b.add_argument("--out", default="corpus_metrics.json")
    args = ap.parse_args()
    if args.cmd == "manuscript":
        m = analyse(args.file, args.year)
        print(to_md(m) if args.format == "md" else json.dumps(m, indent=1, ensure_ascii=False))
    else:
        corpus(args.folder, args.year, args.out)


if __name__ == "__main__":
    main()
