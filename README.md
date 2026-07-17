# Classical Chinese Corpus: Sentence Segmentation and Named Entity Recognition

This repository contains the processed outputs of a Classical Chinese corpus project for the **Advanced Natural Language Processing** course.

The dataset provides two types of outputs:

* Sentence segmentation results in TSV format.
* Named Entity Recognition results in JSON format.

The segmentation and NER outputs are stored separately in the `seg/` and `ner/` directories.

## 1. Project Overview

The project focuses on two Natural Language Processing tasks for Classical Chinese historical texts.

### Sentence Segmentation

The original historical texts are divided into individual sentences. Each sentence is assigned a unique identifier.

The segmentation outputs are stored in:

```text
seg/
```

### Named Entity Recognition

Named entities are identified from each segmented sentence and exported in a unified JSON structure.

The NER outputs are stored in:

```text
ner/
```

## 2. Repository Structure

```text
NLP_corpus_project/
├── README.md
├── seg/
│   ├── HCH_009/
│   │   ├── HCH_009_001/
│   │   │   └── HCH_009_001_seg.tsv
│   │   ├── HCH_009_002/
│   │   │   └── HCH_009_002_seg.tsv
│   │   └── ...
│   ├── HCH_010/
│   ├── HCH_011/
│   ├── HCH_012/
│   ├── HCH_013/
│   ├── HCH_014/
│   ├── HCH_015/
│   └── HCH_016/
└── ner/
    ├── HCH_009/
    │   ├── HCH_009_001/
    │   │   └── HCH_009_001_ner.json
    │   ├── HCH_009_002/
    │   │   └── HCH_009_002_ner.json
    │   └── ...
    ├── HCH_010/
    ├── HCH_011/
    ├── HCH_012/
    ├── HCH_013/
    ├── HCH_014/
    ├── HCH_015/
    └── HCH_016/
```

The corresponding segmentation and NER files have the same corpus and unit identifiers but are stored in separate directory trees.

For example:

```text
seg/HCH_009/HCH_009_001/HCH_009_001_seg.tsv
ner/HCH_009/HCH_009_001/HCH_009_001_ner.json
```

The general path conventions are:

```text
seg/<corpus_id>/<unit_id>/<unit_id>_seg.tsv
ner/<corpus_id>/<unit_id>/<unit_id>_ner.json
```

## 3. Dataset Statistics

The repository contains the following corpus groups:

| Corpus ID | Number of units | Number of sentences |
| --------- | --------------: | ------------------: |
| `HCH_009` |             135 |              44,957 |
| `HCH_010` |             116 |              19,133 |
| `HCH_011` |              56 |              11,884 |
| `HCH_012` |             332 |             158,296 |
| `HCH_013` |              80 |              22,512 |
| `HCH_014` |               6 |                 399 |
| `HCH_015` |              59 |              11,910 |
| `HCH_016` |              11 |               1,723 |
| **Total** |         **795** |         **270,814** |

## 4. Sentence Segmentation Format

Sentence segmentation files use the `.tsv` format.

Each non-empty row contains two tab-separated fields:

```text
sentence_id<TAB>sentence
```

Example:

```tsv
HCH_009_001_000001	金之先，出靺鞨氏。
HCH_009_001_000002	靺鞨本號勿吉。
HCH_009_001_000003	勿吉，古肅慎地也。
```

### Sentence ID Convention

A sentence ID follows this structure:

```text
<corpus_id>_<unit_number>_<sentence_number>
```

Example:

```text
HCH_009_001_000001
```

In this example:

* `HCH_009` is the corpus identifier.
* `001` is the textual unit identifier.
* `000001` is the sentence number within the unit.

## 5. Named Entity Recognition Format

NER annotations are stored in UTF-8 JSON files.

The root element is a JSON array. Each item represents one segmented sentence:

```json
[
  {
    "sentence_id": "HCH_009_001_000001",
    "sentence": "金之先，出靺鞨氏。",
    "entities": [
      {
        "text": "金",
        "label": "ORG"
      },
      {
        "text": "靺鞨氏",
        "label": "ORG"
      }
    ]
  }
]
```

Each sentence object contains:

| Field              | Type   | Description                               |
| ------------------ | ------ | ----------------------------------------- |
| `sentence_id`      | String | Unique sentence identifier                |
| `sentence`         | String | Original segmented sentence               |
| `entities`         | Array  | Named entities identified in the sentence |
| `entities[].text`  | String | Entity text as it appears in the sentence |
| `entities[].label` | String | Entity category                           |

When no named entities are identified, the `entities` field is an empty array:

```json
{
  "sentence_id": "HCH_009_001_000010",
  "sentence": "有文字、禮樂、官府、制度。",
  "entities": []
}
```

## 6. Entity Labels

The annotation scheme uses six entity types:

| Label   | Entity type  | Description                                                                     |
| ------- | ------------ | ------------------------------------------------------------------------------- |
| `PER`   | Person       | Personal names and named historical figures                                     |
| `LOC`   | Location     | Regions, cities, mountains, rivers and geographical locations                   |
| `ORG`   | Organization | Dynasties, states, tribes, clans, institutions and administrative organizations |
| `TITLE` | Title        | Official titles, ranks, offices and honorific titles                            |
| `TME`   | Time         | Dates, reign periods, eras and temporal expressions                             |
| `NUM`   | Number       | Quantities, measurements and numerical expressions                              |

Examples:

```text
李勣     → PER
黑龍江   → LOC
契丹     → ORG
都督     → TITLE
唐初     → TME
十五萬   → NUM
```

## 7. Downloading the Dataset

Clone the repository:

```bash
git clone https://github.com/keiranoluv/NLP_corpus_project.git
cd NLP_corpus_project
```

No package installation or model execution is required to use the processed dataset.

## 8. Reading the Segmentation Data

Example using Python:

```python
import csv
from pathlib import Path

tsv_path = Path(
    "seg/HCH_009/HCH_009_001/HCH_009_001_seg.tsv"
)

with tsv_path.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:
    reader = csv.reader(file, delimiter="\t")

    for sentence_id, sentence in reader:
        print(sentence_id, sentence)
```

Run the example from the repository root:

```bash
python read_seg.py
```

Replace `read_seg.py` with the filename in which the example code is saved.

## 9. Reading the NER Data

Example using Python:

```python
import json
from pathlib import Path

json_path = Path(
    "ner/HCH_009/HCH_009_001/HCH_009_001_ner.json"
)

with json_path.open("r", encoding="utf-8-sig") as file:
    records = json.load(file)

print(f"Number of sentences: {len(records)}")

for record in records[:3]:
    print("Sentence ID:", record["sentence_id"])
    print("Sentence:", record["sentence"])
    print("Entities:", record["entities"])
    print()
```

Run the example from the repository root:

```bash
python read_ner.py
```

Replace `read_ner.py` with the filename in which the example code is saved.

## 10. Matching Segmentation and NER Files

A segmentation file and its corresponding NER file share the same unit ID.

For example:

```text
Segmentation:
seg/HCH_013/HCH_013_001/HCH_013_001_seg.tsv

NER:
ner/HCH_013/HCH_013_001/HCH_013_001_ner.json
```

For every non-empty unit, the following conditions should hold:

1. The segmentation and NER files must share the same unit ID.
2. The number of TSV sentences must equal the number of JSON sentence objects.
3. The `sentence_id` values must match between the two files.
4. The JSON `sentence` field must preserve the original segmented sentence.
5. Every entity text must occur in its corresponding sentence.
6. Every entity label must belong to the supported label set:

```text
PER, LOC, ORG, TITLE, TME, NUM
```

7. All files must use UTF-8 encoding.

## 11. Notes

* The corpus contains Classical Chinese historical texts.
* Sentence segmentation and NER results are stored separately.
* The directory structures under `seg/` and `ner/` mirror each other.
* Some source units may be empty because no textual content was available.
* Historical personal names, titles, dynasties and place names may be context-dependent and can require manual review.
* The dataset is provided as processed output; users do not need to execute the annotation models.

## 12. Course Information

This project was completed for the course:

**Advanced Natural Language Processing**

Faculty of Information Technology
University of Science
Vietnam National University, Ho Chi Minh City

## 13. License and Usage

This repository is intended primarily for academic and research purposes.

Before redistributing or publishing the dataset, users should verify the copyright and usage conditions of the original historical text sources.
