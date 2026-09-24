# Templates

## Input form (WRITE)

Ask only for what is missing. Show the list in the user's language. Indonesian version:

```
IDENTITAS PENELITIAN
- Topik / objek penelitian (spesies, ekosistem, variabel):
- Domain: (biologi laut / ekologi / perikanan / oseanografi / pencemaran / penginderaan jauh / mikrobiologi / pesisir / geologi)
- Lokasi (situs, kabupaten, provinsi; koordinat bila ada):
- Periode pengambilan data:
- Bahasa naskah: Indonesia / Inggris

LOGIKA ILMIAH
- Masalah penelitian:
- Gap (apa yang sudah diketahui, apa yang belum, di mana):
- Tujuan (O1, O2, …):

METODE
- Desain & teknik sampling (purposive/random/stratified), jumlah stasiun/sampel:
- Alat (merek/tipe), prosedur lapangan/lab, standar (SNI/CLSI/…):
- Rumus/indeks yang dihitung (dengan sumber):
- Analisis statistik (uji, α) dan perangkat lunak + versi:

HASIL
- Tabel/gambar hasil (tempel angka atau lampirkan file):
- Temuan utama per tujuan:

PUSTAKA
- Daftar referensi terverifikasi (penulis, tahun, judul, jurnal, DOI) + temuan relevan tiap referensi:
```

## Claim-evidence map (traceable draft)

| # | Section/¶ | Claim (short) | Claim type (C1–C8) | Evidence (data/table/figure/ref) | Status (supported / placeholder / needs confirmation) |
|---|---|---|---|---|---|

## Paragraph source map (traceable draft)

| ¶ | Function (paragraph type) | Moves / units | Sources used | Objective served |
|---|---|---|---|---|

## Objective contract

| Objective | Method (section/¶) | Result (table/fig/¶) | Discussion (¶) | Conclusion (sentence) | Status |
|---|---|---|---|---|---|
| O1 | | | | | complete / partial / broken |

## Audit report

```
# JKT Audit — <manuscript short title>
Date · Language · Article type · Domain · Method family · Files audited

## 1. Executive diagnosis
Status: <SUBSTANTIVE_REVISION_REQUIRED | MAJOR_REVISION_REQUIRED | TARGETED_REVISION_REQUIRED | MINOR_TECHNICAL_REVISION | AUDIT_READY>
Highest severity: … | Critical: n | Major: n | Moderate: n | Minor: n
Primary scientific weakness: …
Primary structural weakness: …
Primary JKT-conformity weakness: …
Evidence note: JKT profile is provisional (single issue, n = 14); guideline rules are authoritative.

## 2. Metrics (AUD criteria)
| AUD | Criterion | Manuscript | Guideline | Corpus IQR | Result |

## 3. Findings (sorted by severity)
| ID | Sev. | Section/¶ | Problem | Evidence | Standard | Why it matters | Recommended revision | Conf. |

## 4. Scientific logic matrix (objective contract)

## 5. JKT conformity matrix
| Section | Pattern ID | Expected | Observed | Class (match / variant / partial / deviation) |

## 6. Revision plan
Ordered by: scientific integrity → research logic → evidence → structure → discussion depth → citation → style → formatting
```

## Pattern record (DETECT)

```yaml
- pattern_id: JKT-<SECTION>-NNN
  section:
  description:
  pattern_type:        # structural | rhetorical | linguistic | citational | evidential | procedural | argumentative | statistical | referential | coherence
  source:              # guideline | corpus | domain | author_cluster | language_comparison | temporal_comparison
  frequency_percent:
  evidence_count:
  eligible_count:
  domains: []
  years: []
  author_independence:
  language_scope:      # EN | ID | both
  guideline_support:
  exceptions: []
  confidence:          # VERY_HIGH | HIGH | MODERATE | LOW | INSUFFICIENT
  frequency_class:     # CORE | COMMON | VARIABLE | RARE
  status:              # PROVISIONAL | VALIDATED | REJECTED
```
