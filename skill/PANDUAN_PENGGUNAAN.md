# Panduan Penggunaan Skill `jkt-writing-system`

Skill untuk **menulis**, **mengaudit**, dan **menganalisis pola** naskah Jurnal Kelautan Tropis (JKT). Satu paket bisa dipakai di Claude (claude.ai), Claude Code, ChatGPT, dan Codex.

---

## 1. Apa isi skill ini

Skill ini menggabungkan rancangan di folder `pattern/` (codebook, aturan penulisan, aturan audit) dengan hasil analisis korpus 14 artikel JKT Vol. 29(2) 2026. Profil gaya `JKT_STYLE_PROFILE` yang sebelumnya masih kosong (`TO_BE_POPULATED`) kini sudah terisi data empiris.

| Mode | Kapan dipakai | Hasil |
|---|---|---|
| **WRITE** (Artefak 2) | Anda punya data, catatan, atau hasil penelitian dan ingin kerangka, satu bagian, atau naskah lengkap | Teks sesuai gaya JKT + peta klaim–bukti + daftar hal yang masih kurang |
| **AUDIT** (Artefak 3) | Anda punya naskah (.docx/.pdf/.txt) dan ingin diperiksa sebelum submit | Laporan audit: status naskah, temuan per tingkat keparahan, rencana revisi |
| **DETECT** (Artefak 1) | Anda punya kumpulan artikel JKT terbitan dan ingin memperbarui pola gaya | Profil korpus + basis data pola yang diperbarui |

Skill memilih mode dari permintaan Anda. Kalau permintaannya ambigu, skill akan bertanya dulu.

### Struktur folder

```
skill/
├─ PANDUAN_PENGGUNAAN.md          ← dokumen ini
├─ build_and_install.py           ← validasi, buat ZIP, pasang ke Claude Code & Codex
├─ dist/jkt-writing-system.zip    ← file untuk diunggah ke claude.ai dan ChatGPT
└─ jkt-writing-system/            ← isi skill (sumber utama; edit di sini)
   ├─ SKILL.md                    ← instruksi inti + pemilihan mode
   ├─ agents/openai.yaml          ← metadata tampilan untuk Codex/ChatGPT
   ├─ references/
   │  ├─ mode_write.md · mode_audit.md · mode_detect.md
   │  ├─ style_profile.yaml       ← profil gaya JKT (terisi, status PROVISIONAL)
   │  ├─ pattern_database.yaml    ← pola, anti-pola, grammar, kriteria audit AUD-01…30
   │  ├─ generation_rules.yaml · audit_rules.yaml          (dari folder pattern/)
   │  ├─ pattern_codebook.yaml · annotation_codebook.yaml  (dari folder pattern/)
   │  ├─ templates.md             ← formulir input & format laporan
   │  └─ baseline_rd_chains.txt   ← kode wacana 187 paragraf Hasil & Pembahasan
   └─ scripts/jkt_metrics.py      ← pengukur otomatis naskah/korpus
```

---

## 2. Status instalasi dan cara memasang

| Platform | Status | Lokasi / cara |
|---|---|---|
| **Claude Code** | ✅ Sudah terpasang dan terverifikasi | `C:\Users\Romie Jhonnerie\.claude\skills\jkt-writing-system` |
| **Codex** (CLI/IDE/desktop) | ✅ Sudah terpasang dan terverifikasi | `C:\Users\Romie Jhonnerie\.agents\skills\jkt-writing-system` |
| **Claude (claude.ai / desktop / mobile)** | Perlu diunggah sekali | Unggah `skill\dist\jkt-writing-system.zip` |
| **ChatGPT** | Perlu diunggah sekali | Unggah `skill\dist\jkt-writing-system.zip` |

### Claude (claude.ai)
1. Buka **Settings → Capabilities**. Pastikan *Code execution and file creation* aktif, karena skill memerlukannya.
2. Di bagian **Skills**, pilih **Upload skill** dan pilih `dist\jkt-writing-system.zip`. Di versi yang lebih baru menu ini bisa bernama **Customize → Skills**.
3. Aktifkan toggle skill tersebut. Skill akan dipakai otomatis saat Anda meminta sesuatu tentang naskah JKT.
4. Untuk organisasi (Team/Enterprise), admin bisa mengunggahnya agar tersedia bagi seluruh anggota.

### ChatGPT
1. Buka **Skills → Create → Upload from your computer**, lalu pilih `dist\jkt-writing-system.zip`.
2. Panggil skill dengan mengetik `@` lalu memilih **jkt-writing-system**, atau cukup tulis permintaan. Skill dipilih otomatis bila cocok dengan deskripsinya.
3. Ketersediaan fitur Skills bergantung pada paket ChatGPT Anda.

### Claude Code
- Otomatis aktif di semua proyek. Panggil langsung dengan `/jkt-writing-system`, atau cukup tulis permintaan seperti "audit naskah saya untuk JKT".
- Agar skill ikut ter-commit ke repositori proyek, jalankan `python skill\build_and_install.py --project C:\xampp\htdocs\jurnal\JKT`. Perintah ini membuat `.claude\skills\` dan `.agents\skills\` di proyek.

### Codex
- Panggil dengan `$jkt-writing-system`, atau lihat daftar skill dengan `/skills`. Skill juga dipilih otomatis bila permintaan cocok.

### Memperbarui skill
1. Edit file di `skill\jkt-writing-system\` (misalnya setelah profil pola diperbarui lewat mode DETECT).
2. Jalankan:
   ```bash
   python skill/build_and_install.py
   ```
   Perintah ini memvalidasi `SKILL.md`, membuat ulang ZIP, dan memperbarui salinan Claude Code dan Codex.
3. Unggah ulang ZIP baru ke claude.ai dan ChatGPT (hapus versi lama terlebih dahulu).

---

## 3. Cara memakai setiap mode

### 3.1 WRITE: menulis naskah

**Siapkan** sebanyak mungkin dari daftar ini (skill akan menanyakan yang kurang):
- Topik, objek, lokasi (situs, kabupaten, provinsi), periode sampling, bahasa naskah
- Masalah, gap (apa yang sudah diketahui dan apa yang belum), tujuan O1, O2, …
- Desain dan teknik sampling, jumlah stasiun/sampel, alat (tipe), rumus/indeks, uji statistik, perangkat lunak + versi
- Tabel atau angka hasil
- **Daftar pustaka terverifikasi** (penulis, tahun, judul, jurnal, DOI) beserta temuan relevannya. Skill tidak akan mengarang sitasi.

**Contoh permintaan**
```
Pakai skill JKT. Buatkan kerangka (planning only) artikel dari data terlampir:
struktur komunitas lamun di Pulau X, Mei–Juli 2025, 6 stasiun, bahasa Indonesia.
```
```
Tulis bagian Hasil dan Pembahasan dari Tabel 1–3 berikut, gaya JKT, bahasa Inggris.
Referensi yang boleh dipakai: [tempel daftar]
```
```
Buat draf lengkap (traceable draft) dari catatan penelitian saya. Tampilkan peta klaim–bukti.
```

**Mode keluaran:** `planning_only` (kerangka) · `section_draft` (satu bagian) · `full_draft` · `traceable_draft` (teks + peta sumber + peta klaim–bukti) · `clean_manuscript` (siap tempel ke template, hanya setelah lolos quality gate).

**Yang Anda terima:**
1. Teks sesuai pola JKT, misalnya:
   - Pendahuluan: corong dari konteks ke lokasi → gap kontrastif → "Oleh karena itu" → tujuan.
   - Hasil dan Pembahasan: per variabel, pola hasil → interpretasi → pustaka.
   - Kesimpulan: satu paragraf tanpa sitasi.
2. Catatan kepatuhan: jumlah kata judul (≤ 12), abstrak (≤ 250), jumlah kata kunci (3–5).
3. Daftar placeholder yang harus Anda lengkapi, misalnya `[REFERENCE REQUIRED]` dan `[SAMPLE SIZE REQUIRED]`.

### 3.2 AUDIT: memeriksa naskah

**Contoh permintaan**
```
Audit naskah terlampir untuk submit ke Jurnal Kelautan Tropis. Laporan dalam bahasa Indonesia.
```
```
Periksa khusus bagian Pembahasan dan Kesimpulan: kedalaman diskusi, klaim kausal, kesesuaian dengan tujuan.
```
```
Perbaiki temuan CRITICAL dan MAJOR saja, lalu audit ulang.
```

**Yang dilakukan skill:**
1. Mengukur naskah dengan `jkt_metrics.py`: jumlah kata, proporsi bagian, kepadatan sitasi, umur referensi, DOI, sisa draf, kalimat kausal tanpa *hedging*, dan angka di abstrak/kesimpulan yang tidak ada di isi.
2. Mengaudit tiga lapis: **integritas ilmiah** → **kualitas retoris** → **kesesuaian JKT**.
3. Memberi status naskah: `SUBSTANTIVE / MAJOR / TARGETED REVISION REQUIRED`, `MINOR TECHNICAL REVISION`, atau `AUDIT_READY`. Status tidak bisa `AUDIT_READY` bila masih ada temuan CRITICAL.
4. Menyajikan temuan per tingkat (CRITICAL, MAJOR, MODERATE, MINOR), lengkap dengan lokasi, bukti, standar acuan (ID pedoman, pola, atau AUD), dan saran revisi.

Skill tidak memberi skor tunggal dan tidak memprediksi peluang diterima.

**Menjalankan pengukuran sendiri** (tanpa AI):
```bash
python "C:/Users/Romie Jhonnerie/.claude/skills/jkt-writing-system/scripts/jkt_metrics.py" manuscript naskah.docx --year 2026
```
Hasilnya berupa tabel PASS/FLAG/VERIFY. **FLAG** berarti melanggar pedoman atau berada di luar rentang korpus. **VERIFY** berarti perlu dibaca manual, misalnya kalimat kausal atau angka yang tidak cocok.

> Tips: gunakan judul bagian standar (PENDAHULUAN / MATERI DAN METODE / HASIL DAN PEMBAHASAN / KESIMPULAN / DAFTAR PUSTAKA, atau padanan Inggrisnya) agar skrip bisa memisahkan bagian dengan benar.

### 3.3 DETECT: memperbarui pola dari korpus

Pakai mode ini untuk menambah artikel JKT (misalnya terbitan 2024–2025) agar pola lebih kuat.

**Langkah**
1. Kumpulkan PDF artikel dalam satu folder, misalnya `korpus_2024\`.
2. Minta:
   ```
   Pakai skill JKT mode DETECT pada folder korpus_2024. Gabungkan dengan baseline Vol. 29(2)
   dan perbarui style_profile.yaml serta pattern_database.yaml. Sisihkan 15% artikel sebagai holdout.
   ```
3. Skill akan memberi *Corpus Intake Report*, menjalankan
   `python scripts/jkt_metrics.py corpus korpus_2024 --out corpus_metrics.json`, mengodekan retorika secara manual sesuai `annotation_codebook.yaml`, menguji efek bahasa, bidang, klaster penulis, dan tahun, lalu memperbarui file profil.
4. Setelah file diperbarui, jalankan `python skill/build_and_install.py` dan unggah ulang ZIP.

**Target:** ≥ 30 artikel dari ≥ 2 tahun (idealnya 50–100) dengan validasi holdout. Setelah itu pola bisa naik dari *PROVISIONAL* ke *VALIDATED*.

---

## 4. Aturan penting yang dipegang skill

1. **Urutan prioritas:** validitas ilmiah → keterlacakan bukti → logika penelitian → pedoman JKT → pola JKT → bahasa.
2. **Tidak pernah mengarang** angka, statistik, jumlah sampel, alat, koordinat, spesies, DOI, atau referensi. Data yang kurang ditandai dengan placeholder.
3. **Kontrol kausalitas:** data observasional ditulis dengan bahasa asosiatif atau *hedged* ("diduga berkaitan dengan", "may reflect"). Setengah artikel korpus masih melanggar ini, jadi ini titik periksa utama.
4. **Satu sumber untuk setiap angka:** abstrak, tujuan, hasil, dan kesimpulan harus memakai angka yang identik. Empat dari 14 artikel terbit melanggar ini.
5. **Pedoman ≠ pola korpus:** aturan pedoman (judul ≤ 12 kata, abstrak ≤ 250 kata, 3–5 kata kunci, ≤ 10 halaman, APA 7) bersifat **WAJIB**. Pola korpus bersifat **DIANJURKAN**.

## 5. Keterbatasan (baca sebelum mengandalkan)

- Profil gaya berasal dari **satu terbitan** (Vol. 29(2) 2026, 14 artikel, 5 di antaranya dari satu klaster penulis Undip). Semua pola berstatus **PROVISIONAL**.
- Pedoman penulis diambil dari laman JKT per 23-09-2026. **Periksa ulang** sebelum submit, karena pedoman bisa berubah.
- `jkt_metrics.py` bersifat penyaring heuristik. Hasil pembacaan PDF dua kolom bisa menggeser hitungan referensi ±1–2, jadi setiap FLAG/VERIFY perlu dicek manual.
- Di ChatGPT atau claude.ai tanpa eksekusi kode, skill akan mengukur secara manual dan menyatakannya.

## 6. Pemecahan masalah

| Masalah | Solusi |
|---|---|
| Skill tidak terpanggil otomatis | Sebut eksplisit: "pakai skill jkt-writing-system", `/jkt-writing-system` (Claude Code), `$jkt-writing-system` (Codex), `@jkt-writing-system` (ChatGPT) |
| Unggahan ZIP ditolak | Pastikan yang diunggah adalah `dist\jkt-writing-system.zip` hasil `build_and_install.py`, bukan folder `skill\` |
| `pdftotext not found` | Pasang poppler, atau simpan naskah sebagai .docx/.txt |
| Bagian naskah tidak terdeteksi | Gunakan judul bagian standar di baris tersendiri |
| Perubahan skill tidak muncul | Jalankan ulang `build_and_install.py`, buka sesi baru, dan unggah ulang ZIP di claude.ai/ChatGPT |
