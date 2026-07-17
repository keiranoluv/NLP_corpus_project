# Classical Chinese Corpus: Sentence Segmentation and Named Entity Recognition

This repository contains the processed outputs of a Classical Chinese corpus project for the **Advanced Natural Language Processing** course.

The corpus is organized by historical work and textual unit. Each unit contains:

* A sentence-segmentation file in TSV format.
* A named entity recognition file in JSON format.

## 1. Project Overview

The project focuses on two main Natural Language Processing tasks for Classical Chinese historical texts:

1. **Sentence Segmentation**

   * Dividing the original historical texts into individual sentences.
   * Assigning a unique identifier to every sentence.

2. **Named Entity Recognition**

   * Identifying named entities appearing in each segmented sentence.
   * Exporting the annotations in a unified JSON format.

The repository currently contains the processed outputs for the following corpus groups:

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

> The statistics above are generated from `check_ner_report.log`.

## 2. Repository Structure

```text
NLP_corpus_project/
├── HCH_009/
│   ├── HCH_009_001/
│   │   ├── HCH_009_001_seg.tsv
│   │   └── HCH_009_001_ner.json
│   ├── HCH_009_002/
│   │   ├── HCH_009_002_seg.tsv
│   │   └── HCH_009_002_ner.json
│   └── ...
├── HCH_010/
├── HCH_011/
├── HCH_012/
├── HCH_013/
├── HCH_014/
├── HCH_015/
├── HCH_016/
├── script.py
├── check_ner_report.log
└── README.md
```

The directory naming convention is:

```text
<corpus_id>/<unit_id>/
```

For example:

```text
HCH_009/HCH_009_001/
```

Each unit normally contains two corresponding files:

```text
<unit_id>_seg.tsv
<unit_id>_ner.json
```

## 3. Sentence Segmentation Format

Sentence-segmentation files use the `.tsv` format.

Each non-empty row contains:

```text
sentence_id<TAB>sentence
```

Example:

```tsv
HCH_009_001_000001	金之先，出靺鞨氏。
HCH_009_001_000002	靺鞨本號勿吉。
HCH_009_001_000003	勿吉，古肅慎地也。
```

### Sentence ID convention

A sentence ID follows this structure:

```text
<corpus_id>_<unit_number>_<sentence_number>
```

Example:

```text
HCH_009_001_000001
```

Where:

* `HCH_009` identifies the historical work.
* `001` identifies the textual unit.
* `000001` identifies the sentence within that unit.

## 4. Named Entity Recognition Format

NER annotations are stored as UTF-8 JSON files.

The root element of each file is a JSON array. Each element represents one sentence:

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

| Field              | Type   | Description                                       |
| ------------------ | ------ | ------------------------------------------------- |
| `sentence_id`      | String | Unique sentence identifier                        |
| `sentence`         | String | Original segmented sentence                       |
| `entities`         | Array  | Named entities found in the sentence              |
| `entities[].text`  | String | Entity text exactly as it appears in the sentence |
| `entities[].label` | String | Entity category                                   |

When no named entity is identified, `entities` is an empty array:

```json
{
  "sentence_id": "HCH_009_001_000010",
  "sentence": "有文字、禮樂、官府、制度。",
  "entities": []
}
```

## 5. Entity Labels

The annotation scheme uses the following six entity types:

| Label   | Entity type  | Description                                                                     |
| ------- | ------------ | ------------------------------------------------------------------------------- |
| `PER`   | Person       | Personal names and named historical figures                                     |
| `LOC`   | Location     | Countries, regions, cities, mountains, rivers and other geographical locations  |
| `ORG`   | Organization | Dynasties, states, tribes, clans, institutions and administrative organizations |
| `TITLE` | Title        | Official titles, ranks, offices and honorific titles                            |
| `TME`   | Time         | Dates, reign periods, eras, seasons and other temporal expressions              |
| `NUM`   | Number       | Quantities, measurements and numerical expressions                              |

Examples:

```text
李勣        → PER
黑龍江      → LOC
契丹        → ORG
都督        → TITLE
唐初        → TME
十五萬      → NUM
```

## 6. Data Validation

The repository includes `script.py`, which scans all segmentation files and checks their corresponding NER outputs.

The validation script performs the following checks:

* Finds every `*_seg.tsv` file recursively.
* Determines the expected matching `*_ner.json` path.
* Counts the sentences in each TSV file.
* Counts the sentence objects in each JSON file.
* Detects missing JSON files.
* Detects TSV–JSON sentence-count mismatches.
* Reports JSON parsing and file-reading errors.
* Produces per-unit and per-corpus statistics.
* Saves the complete report to a log file.

### Requirements

The validation script only uses the Python standard library.

Recommended environment:

```text
Python 3.9 or later
```

No additional package installation is required.

### Run the validation script

From the repository root:

```bash
python script.py .
```

On systems where Python 3 uses a separate command:

```bash
python3 script.py .
```

To specify a custom output log:

```bash
python script.py . --log validation_report.log
```

General syntax:

```bash
python script.py <dataset_root> --log <output_log>
```

### Example output

```text
[OK] HCH_009/HCH_009_001 | sentences=410
[OK] HCH_009/HCH_009_002 | sentences=307

STATISTICS BY WORK
====================================================================================================

HCH_009 | units=135 | matched=133 | mismatched=0 | missing_json=2

GLOBAL SUMMARY
====================================================================================================

Total works             : 8
Total TSV units         : 795
Matched units           : 789
Mismatched units        : 0
Missing JSON units      : 6
Read errors             : 0
Total TSV sentences     : 270814
Total JSON sentences    : 270814
```

## 7. Current Validation Status

According to the included validation report:

* Total corpus groups: **8**
* Total TSV units: **795**
* TSV–JSON pairs with matching sentence counts: **789**
* Mismatched sentence counts: **0**
* File-reading errors: **0**
* Total non-empty TSV sentences: **270,814**
* Total JSON sentence objects: **270,814**

Six units are reported as missing NER JSON files:

```text
HCH_009_061
HCH_009_062
HCH_012_101
HCH_012_102
HCH_012_110
HCH_012_112
```

The corresponding TSV files contain zero sentences. Therefore, they do not affect the total number of annotated sentences, but they remain listed by the validation script because no corresponding `*_ner.json` file exists.

## 8. Data Consistency Requirements

For every non-empty unit, the following conditions should hold:

1. The TSV and JSON filenames must share the same unit ID.

```text
HCH_013_001_seg.tsv
HCH_013_001_ner.json
```

2. The number of TSV sentences must equal the number of JSON sentence objects.

3. The `sentence_id` values must remain consistent between both files.

4. The `sentence` field in JSON must preserve the original segmented text.

5. Entity text must occur exactly within the corresponding sentence.

6. Entity labels must belong to the supported label set:

```text
PER, LOC, ORG, TITLE, TME, NUM
```

7. Files must be encoded in UTF-8.

## 9. Using the Dataset

A basic Python example for reading one NER file:

```python
import json
from pathlib import Path

json_path = Path(
    "HCH_009/HCH_009_001/HCH_009_001_ner.json"
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

A basic example for reading one segmentation file:

```python
import csv
from pathlib import Path

tsv_path = Path(
    "HCH_009/HCH_009_001/HCH_009_001_seg.tsv"
)

with tsv_path.open(
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:
    reader = csv.reader(file, delimiter="\t")

    for sentence_id, sentence in reader:
        print(sentence_id, sentence)
```

## 10. Notes

* The corpus contains Classical Chinese historical texts.
* Annotation boundaries follow the text spans appearing in each sentence.
* Some source units are empty because no textual content was available for segmentation.
* Automatic and assisted annotation may still require manual review for ambiguous historical names, titles, dynasties and geographical entities.
* `check_ner_report.log` is a generated validation artifact and can be regenerated by running `script.py`.

## 11. Course Information

This project was completed for the course:

**Advanced Natural Language Processing**

Faculty of Information Technology
University of Science
Vietnam National University, Ho Chi Minh City

## 12. License and Usage

This repository is intended primarily for academic and research purposes.

Before redistributing or publishing the dataset, users should verify the copyright and usage conditions of the original historical text sources.
