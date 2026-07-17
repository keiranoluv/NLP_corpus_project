# HCH Corpus Processing

Rule-based sentence segmentation pipeline for Classical Chinese historical texts in the HCH corpus.

## Project Structure

```text
hch_project/
├── data/
│   ├── 金史_full.txt
│   ├── 遼史_full.txt
│   ├── 梁書_full.txt
│   ├── 明史_full.txt
│   ├── 明史紀事本末_full.txt
│   ├── Mục Thiên Tử Truyện - 穆天子傳_full.txt
│   ├── 南齊書_full.txt
│   └── Ngô Việt Xuân Thu - 吳越春秋_full.txt
│
├── scripts/
│   ├── segment_han_rule.py
│   └── segment_han_by_volume.py
│
└── output/
```

## Environment Setup

Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install pandas openpyxl tqdm regex
```

Optional:

```bash
pip freeze > requirements.txt
```

## Input Files

| Code    | Work                  | Chinese Title | Input File                                |
| ------- | --------------------- | ------------- | ----------------------------------------- |
| HCH_009 | Kim Sử                | 金史            | 金史_full.txt                               |
| HCH_010 | Liêu Sử               | 遼史            | 遼史_full.txt                               |
| HCH_011 | Lương Thư             | 梁書            | 梁書_full.txt                               |
| HCH_012 | Minh Sử               | 明史            | 明史_full.txt                               |
| HCH_013 | Minh Sử Ký Sự Bản Mạt | 明史紀事本末        | 明史紀事本末_full.txt                           |
| HCH_014 | Mục Thiên Tử Truyện   | 穆天子傳          | Mục Thiên Tử Truyện - 穆天子傳_full.txt |
| HCH_015 | Nam Tề Thư            | 南齊書           | 南齊書_full.txt                              |
| HCH_016 | Ngô Việt Xuân Thu     | 吳越春秋          | Ngô Việt Xuân Thu - 吳越春秋_full.txt     |

## 1. Full-book Sentence Segmentation

This mode segments one full text file into a single TSV file.

Example for `金史`:

```bash
python scripts/segment_han_rule.py \
  --input "data/金史_full.txt" \
  --output "output/HCH_009/HCH_009_seg.tsv" \
  --prefix HCH_009
```

Output format:

```text
sentence_id<TAB>sentence
```

Example:

```text
HCH_009_000001	金之先，出靺鞨氏。
HCH_009_000002	靺鞨本號勿吉。
```

## 2. Unit-aware Segmentation

This mode segments each work by internal units.

For most works, the unit is `# 卷...`.

For `HCH_016 / 吳越春秋`, the source does not use `# 卷...`, so the script falls back to level-1 headings such as:

```text
# 吳太伯傳
# 吳王壽夢傳
# 王僚使公子光傳
```

### Run One Work

Example for `金史`:

```bash
python scripts/segment_han_by_volume.py \
  --code HCH_009 \
  --data-dir data \
  --output-root output/by_unit
```

Example for `吳越春秋`:

```bash
python scripts/segment_han_by_volume.py \
  --code HCH_016 \
  --data-dir data \
  --output-root output/by_unit
```

### Run All Works

```bash
python scripts/segment_han_by_volume.py \
  --all \
  --data-dir data \
  --output-root output/by_unit
```

## Output Structure

For volume-based works:

```text
output/by_unit/HCH_009/HCH_009_001/HCH_009_001_seg.tsv
output/by_unit/HCH_009/HCH_009_002/HCH_009_002_seg.tsv
...
```

For `吳越春秋`:

```text
output/by_unit/HCH_016/HCH_016_001_吳太伯傳/HCH_016_001_seg.tsv
output/by_unit/HCH_016/HCH_016_002_吳王壽夢傳/HCH_016_002_seg.tsv
output/by_unit/HCH_016/HCH_016_003_王僚使公子光傳/HCH_016_003_seg.tsv
...
```

## Sentence ID Format

Full-book mode:

```text
HCH_009_000001
HCH_009_000002
```

Unit-aware mode:

```text
HCH_009_001_000001
HCH_009_001_000002
HCH_009_002_000001
```

For `HCH_016`, each section uses the same unit-aware format:

```text
HCH_016_001_000001
HCH_016_001_000002
HCH_016_002_000001
```

## Quality Check Commands

Check generated files:

```bash
find output/by_unit -name "*_seg.tsv" | sort | head
find output/by_unit -name "*_seg.tsv" | wc -l
```

Check TSV format:

```bash
for f in output/by_unit/HCH_*/*/*_seg.tsv; do
  awk -F'\t' 'NF != 2 {print FILENAME, NR, $0}' "$f"
done | head
```

Check long sentences:

```bash
for f in output/by_unit/HCH_*/*/*_seg.tsv; do
  awk -F'\t' 'length($2) > 1000 {print FILENAME, $1, length($2), substr($2,1,120)}' "$f"
done | head
```

Check sentences starting with unmatched closing quotes:

```bash
for f in output/by_unit/HCH_*/*/*_seg.tsv; do
  awk -F'\t' '$2 ~ /^」|^』/ {print FILENAME, $1, substr($2,1,120)}' "$f"
done | head
```

Count sentences per generated file:

```bash
python - << 'PY'
from pathlib import Path

total = 0

for path in sorted(Path("output/by_unit").glob("HCH_*/*/*_seg.tsv")):
    n = sum(1 for _ in path.open(encoding="utf-8"))
    total += n
    print(path, n)

print("TOTAL:", total)
PY
```

## Expected Unit Counts

Expected unit counts after running `segment_han_by_volume.py --all`:

```text
HCH_009 金史: 135 volumes
HCH_010 遼史: 116 volumes
HCH_011 梁書: 56 volumes
HCH_012 明史: 332 volumes
HCH_013 明史紀事本末: 80 volumes
HCH_014 穆天子傳: 6 volumes
HCH_015 南齊書: 59 volumes
HCH_016 吳越春秋: sections/傳 instead of volumes
```

