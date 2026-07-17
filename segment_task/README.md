# Classical Chinese Sentence Segmentation

This directory contains the source texts, scripts, and generated outputs for the sentence segmentation task of the HCH Classical Chinese corpus.

The pipeline applies rule-based sentence segmentation to Classical Chinese historical texts and exports the results as TSV files.

## 1. Directory Structure

```text
segment_task/
├── README.md
├── data/
│   ├── 金史_full.txt
│   ├── 遼史_full.txt
│   ├── 梁書_full.txt
│   ├── 明史_full.txt
│   ├── 明史紀事本末_full.txt
│   ├── Mục Thiên Tử Truyện - 穆天子傳_full.txt
│   ├── 南齊書_full.txt
│   └── Ngô Việt Xuân Thu - 吳越春秋_full.txt
├── scripts/
│   ├── segment_han_rule.py
│   └── segment_han_by_volume.py
└── output/
    └── by_unit/
```

The main scripts are:

| Script | Purpose |
|---|---|
| `segment_han_rule.py` | Segments one complete source text into a single TSV file |
| `segment_han_by_volume.py` | Splits a source text into volumes or sections and produces one TSV file per unit |

For the final dataset, the recommended script is:

```text
scripts/segment_han_by_volume.py
```

## 2. Supported Works

| Corpus ID | Vietnamese title | Chinese title | Input file |
|---|---|---|---|
| `HCH_009` | Kim Sử | 金史 | `金史_full.txt` |
| `HCH_010` | Liêu Sử | 遼史 | `遼史_full.txt` |
| `HCH_011` | Lương Thư | 梁書 | `梁書_full.txt` |
| `HCH_012` | Minh Sử | 明史 | `明史_full.txt` |
| `HCH_013` | Minh Sử Ký Sự Bản Mạt | 明史紀事本末 | `明史紀事本末_full.txt` |
| `HCH_014` | Mục Thiên Tử Truyện | 穆天子傳 | `Mục Thiên Tử Truyện - 穆天子傳_full.txt` |
| `HCH_015` | Nam Tề Thư | 南齊書 | `南齊書_full.txt` |
| `HCH_016` | Ngô Việt Xuân Thu | 吳越春秋 | `Ngô Việt Xuân Thu - 吳越春秋_full.txt` |

## 3. Requirements

The segmentation scripts use only the Python standard library.

Recommended Python version:

```text
Python 3.10 or later
```

No additional packages are required.

Check the installed Python version:

```bash
python --version
```

On systems where Python 3 is invoked separately:

```bash
python3 --version
```

## 4. Running the Pipeline

Run the following commands from the repository root:

```bash
cd segment_task
```

### 4.1 Process one work

For example, process `HCH_009 / 金史`:

```bash
python scripts/segment_han_by_volume.py \
  --code HCH_009 \
  --data-dir data \
  --output-root output/by_unit
```

Process `HCH_016 / 吳越春秋`:

```bash
python scripts/segment_han_by_volume.py \
  --code HCH_016 \
  --data-dir data \
  --output-root output/by_unit
```

Replace `HCH_009` with one of the supported corpus IDs:

```text
HCH_009
HCH_010
HCH_011
HCH_012
HCH_013
HCH_014
HCH_015
HCH_016
```

### 4.2 Process all works

To reproduce the complete segmentation output:

```bash
python scripts/segment_han_by_volume.py \
  --all \
  --data-dir data \
  --output-root output/by_unit
```

### 4.3 Display command-line options

```bash
python scripts/segment_han_by_volume.py --help
```

## 5. Unit Detection

For most works, the script divides the source text using level-1 volume headings such as:

```text
# 卷一
# 卷二
# 卷三
```

Arabic volume numbers are also supported:

```text
# 卷1
# 卷01
# 卷135
```

The following forms are converted to their corresponding numerical unit numbers:

```text
卷一         → 001
卷十一       → 011
卷一百三十五 → 135
```

For works without volume headings, the script falls back to level-1 section headings.

This behavior is used for `HCH_016 / 吳越春秋`, whose units include headings such as:

```text
# 吳太伯傳
# 吳王壽夢傳
# 王僚使公子光傳
```

## 6. Segmentation Rules

The script primarily treats the following characters as sentence-ending punctuation:

```text
。！？
```

The semicolon `；` is intentionally not treated as a sentence boundary because it frequently separates list items or closely related clauses in historical texts.

The pipeline also performs light preprocessing:

- Removes the UTF-8 byte-order mark when present.
- Normalizes line endings.
- Removes excessive whitespace.
- Removes inline note markers.
- Removes editorial annotations enclosed by `〈...〉`, `（...）`, or `[...]`.
- Preserves book-title brackets such as `《...》`.
- Skips Markdown headings and common metadata lines.
- Handles sentences enclosed in `「...」` and `『...』`.
- Avoids splitting at punctuation inside an unfinished quotation.
- Inserts selected hard boundaries for historical-text patterns such as `贊曰：`.
- Attempts to split a new sentence when a closing quotation is followed by a new historical time marker.

The normalization is deliberately conservative to preserve the original Classical Chinese content.

## 7. Output Structure

The generated output follows this structure:

```text
output/by_unit/
├── HCH_009/
│   ├── HCH_009_001/
│   │   └── HCH_009_001_seg.tsv
│   ├── HCH_009_002/
│   │   └── HCH_009_002_seg.tsv
│   └── ...
├── HCH_010/
├── HCH_011/
├── HCH_012/
├── HCH_013/
├── HCH_014/
├── HCH_015/
└── HCH_016/
```

The general output path is:

```text
output/by_unit/<corpus_id>/<unit_id>/<unit_id>_seg.tsv
```

Example:

```text
output/by_unit/HCH_009/HCH_009_001/HCH_009_001_seg.tsv
```

For section-based works such as `HCH_016`, the directory name may also include the section title:

```text
output/by_unit/HCH_016/HCH_016_001_吳太伯傳/HCH_016_001_seg.tsv
```

The TSV filename itself still uses the normalized unit ID:

```text
HCH_016_001_seg.tsv
```

## 8. Output Format

Each output file is a UTF-8 TSV file without a header.

Every row contains two tab-separated fields:

```text
sentence_id<TAB>sentence
```

Example:

```tsv
HCH_009_001_000001	金之先，出靺鞨氏。
HCH_009_001_000002	靺鞨本號勿吉。
HCH_009_001_000003	勿吉，古肅慎地也。
```

## 9. Sentence ID Format

Sentence IDs follow this format:

```text
<corpus_id>_<unit_number>_<sentence_number>
```

Example:

```text
HCH_009_001_000001
```

The components are:

- `HCH_009`: corpus identifier.
- `001`: unit or volume identifier.
- `000001`: sentence number within the unit.

Sentence numbering restarts at `000001` for every unit.

Example:

```text
HCH_009_001_000001
HCH_009_001_000002
HCH_009_002_000001
HCH_009_002_000002
```

## 10. Full-book Segmentation

The repository also provides `segment_han_rule.py`, which processes one complete source file without dividing it into units.

Example:

```bash
python scripts/segment_han_rule.py \
  --input "data/金史_full.txt" \
  --output "output/HCH_009/HCH_009_seg.tsv" \
  --prefix HCH_009
```

The output sentence IDs use the following format:

```text
HCH_009_000001
HCH_009_000002
HCH_009_000003
```

This mode is useful for testing or generating a single full-book file.

For the final unit-based corpus output, use `segment_han_by_volume.py`.

## 11. Expected Unit Counts

After running the pipeline with `--all`, the expected unit counts are:

| Corpus ID | Work | Expected units |
|---|---|---:|
| `HCH_009` | 金史 | 135 |
| `HCH_010` | 遼史 | 116 |
| `HCH_011` | 梁書 | 56 |
| `HCH_012` | 明史 | 332 |
| `HCH_013` | 明史紀事本末 | 80 |
| `HCH_014` | 穆天子傳 | 6 |
| `HCH_015` | 南齊書 | 59 |
| `HCH_016` | 吳越春秋 | 11 sections |

Total expected units:

```text
795
```

## 12. Output Validation

### Count generated TSV files

Linux or macOS:

```bash
find output/by_unit -name "*_seg.tsv" | wc -l
```

Expected result:

```text
795
```

Display several generated paths:

```bash
find output/by_unit -name "*_seg.tsv" | sort | head
```

### Check the number of TSV fields

Each non-empty row should contain exactly two tab-separated fields:

```bash
find output/by_unit -name "*_seg.tsv" -print0 |
while IFS= read -r -d '' file; do
  awk -F'\t' 'NF != 2 {print FILENAME, NR, $0}' "$file"
done
```

No output means that all checked rows contain exactly two fields.

### Check empty sentences

```bash
find output/by_unit -name "*_seg.tsv" -print0 |
while IFS= read -r -d '' file; do
  awk -F'\t' '$2 == "" {print FILENAME, NR, $0}' "$file"
done
```

### Check duplicate sentence IDs

```bash
find output/by_unit -name "*_seg.tsv" -exec cat {} + |
cut -f1 |
sort |
uniq -d
```

No output means that no duplicate sentence IDs were found.

### Count sentences per file

```bash
python - <<'PY'
from pathlib import Path

root = Path("output/by_unit")
total = 0

for path in sorted(root.glob("HCH_*/*/*_seg.tsv")):
    with path.open("r", encoding="utf-8-sig") as file:
        count = sum(1 for line in file if line.strip())

    total += count
    print(f"{path}: {count}")

print(f"TOTAL SENTENCES: {total}")
PY
```

### Check very long sentences

```bash
find output/by_unit -name "*_seg.tsv" -print0 |
while IFS= read -r -d '' file; do
  awk -F'\t' \
    'length($2) > 1000 {
      print FILENAME, $1, length($2), substr($2, 1, 120)
    }' "$file"
done
```

Long sentences are not necessarily errors, but they should be reviewed manually.

## 13. Reproducing the Published Output

From the root of the cloned repository:

```bash
cd NLP_corpus_project/segment_task

rm -rf output/by_unit

python scripts/segment_han_by_volume.py \
  --all \
  --data-dir data \
  --output-root output/by_unit
```

After completion, verify the number of generated files:

```bash
find output/by_unit -name "*_seg.tsv" | wc -l
```

The reproduced files will be available under:

```text
segment_task/output/by_unit/
```

## 14. Reproducibility Notes

- Run commands from the `segment_task/` directory.
- Keep the original filenames under `data/` unchanged because the script maps each corpus ID to a specific filename.
- Use the same source files and script version to reproduce the published output.
- Changes to the source text or segmentation rules may change sentence boundaries and sentence IDs.
- Some units may legitimately produce empty output when the corresponding source unit has no processable textual content.
- Rule-based segmentation may require manual review for malformed quotations, missing punctuation, editorial notes, or unusual source formatting.
