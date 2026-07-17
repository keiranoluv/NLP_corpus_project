#!/usr/bin/env python3

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import TextIO


def count_tsv_sentences(tsv_path: Path) -> int:
    """Count sentence rows in a *_seg.tsv file."""
    with tsv_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = [
            row
            for row in csv.reader(file, delimiter="\t")
            if row and any(cell.strip() for cell in row)
        ]

    if not rows:
        return 0

    first_row = [cell.strip().lower() for cell in rows[0]]

    id_headers = {"sentence_id", "sentenceid", "sent_id", "id"}
    text_headers = {"sentence", "text", "content"}

    has_header = (
        any(cell in id_headers for cell in first_row)
        and any(cell in text_headers for cell in first_row)
    )

    return len(rows) - 1 if has_header else len(rows)


def count_json_sentences(json_path: Path) -> int:
    """Count sentence objects in a *_ner.json file."""
    with json_path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"JSON root must be a list, found {type(data).__name__}"
        )

    return len(data)


def expected_json_path(tsv_path: Path) -> Path:
    """
    HCH_013_001_seg.tsv -> HCH_013_001_ner.json
    """
    filename = tsv_path.name

    if filename.endswith("_seg.tsv"):
        json_name = filename[:-len("_seg.tsv")] + "_ner.json"
    else:
        json_name = tsv_path.stem + "_ner.json"

    return tsv_path.with_name(json_name)


def get_work_id(relative_tsv: Path) -> str:
    """
    Extract work ID such as HCH_013 from:
    HCH_013/HCH_013_001/HCH_013_001_seg.tsv
    """
    if len(relative_tsv.parts) >= 2:
        return relative_tsv.parts[0]

    unit_name = relative_tsv.parent.name
    parts = unit_name.split("_")

    if len(parts) >= 2:
        return "_".join(parts[:2])

    return "UNKNOWN"


class Logger:
    """Write the same ASCII output to terminal and log file."""

    def __init__(self, stream: TextIO):
        self.stream = stream

    def write(self, message: str = "") -> None:
        print(message)
        print(message, file=self.stream)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan all *_seg.tsv files, compare them with matching "
            "*_ner.json files, print per-unit statistics, and save a log."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        type=Path,
        help="Root directory to scan. Default: current directory",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("check_ner_report.log"),
        help="Output log path. Default: check_ner_report.log",
    )

    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    log_path = args.log.expanduser()

    if not log_path.is_absolute():
        log_path = (Path.cwd() / log_path).resolve()

    if not root.exists():
        print(f"[ERROR] Path does not exist: {root}", file=sys.stderr)
        return 2

    if not root.is_dir():
        print(f"[ERROR] Path is not a directory: {root}", file=sys.stderr)
        return 2

    tsv_files = sorted(root.rglob("*_seg.tsv"))

    if not tsv_files:
        print(f"[WARNING] No *_seg.tsv files found under: {root}")
        return 1

    log_path.parent.mkdir(parents=True, exist_ok=True)

    total_units = 0
    matched_units = 0
    mismatched_units = 0
    missing_json_units = 0
    read_errors = 0

    total_tsv_sentences = 0
    total_json_sentences = 0

    complete_units: list[dict[str, object]] = []
    missing_units: list[dict[str, object]] = []
    mismatch_units: list[dict[str, object]] = []
    error_units: list[dict[str, str]] = []

    work_stats = defaultdict(
        lambda: {
            "total_units": 0,
            "matched_units": 0,
            "mismatched_units": 0,
            "missing_json_units": 0,
            "read_errors": 0,
            "tsv_sentences": 0,
            "json_sentences": 0,
        }
    )

    with log_path.open("w", encoding="utf-8", newline="\n") as log_file:
        logger = Logger(log_file)

        logger.write("NER OUTPUT VALIDATION REPORT")
        logger.write(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
        logger.write(f"Scan root   : {root}")
        logger.write(f"Log file    : {log_path}")
        logger.write(f"TSV files   : {len(tsv_files)}")
        logger.write("=" * 100)

        for tsv_path in tsv_files:
            total_units += 1

            relative_tsv = tsv_path.relative_to(root)
            json_path = expected_json_path(tsv_path)
            relative_json = json_path.relative_to(root)
            unit_dir = relative_tsv.parent
            unit_name = tsv_path.name[:-len("_seg.tsv")]
            work_id = get_work_id(relative_tsv)

            stats = work_stats[work_id]
            stats["total_units"] += 1

            try:
                tsv_count = count_tsv_sentences(tsv_path)
                total_tsv_sentences += tsv_count
                stats["tsv_sentences"] += tsv_count
            except Exception as error:
                read_errors += 1
                stats["read_errors"] += 1

                error_units.append(
                    {
                        "unit": str(unit_dir),
                        "type": "TSV ERROR",
                        "file": str(relative_tsv),
                        "error": str(error),
                    }
                )
                continue

            if not json_path.is_file():
                missing_json_units += 1
                stats["missing_json_units"] += 1

                missing_units.append(
                    {
                        "work": work_id,
                        "unit": unit_name,
                        "directory": str(unit_dir),
                        "tsv_sentences": tsv_count,
                        "tsv": str(relative_tsv),
                        "expected_json": str(relative_json),
                    }
                )
                continue

            try:
                json_count = count_json_sentences(json_path)
                total_json_sentences += json_count
                stats["json_sentences"] += json_count
            except json.JSONDecodeError as error:
                read_errors += 1
                stats["read_errors"] += 1

                error_units.append(
                    {
                        "unit": str(unit_dir),
                        "type": "JSON ERROR",
                        "file": str(relative_json),
                        "error": (
                            f"Invalid JSON at line {error.lineno}, "
                            f"column {error.colno}: {error.msg}"
                        ),
                    }
                )
                continue
            except Exception as error:
                read_errors += 1
                stats["read_errors"] += 1

                error_units.append(
                    {
                        "unit": str(unit_dir),
                        "type": "JSON ERROR",
                        "file": str(relative_json),
                        "error": str(error),
                    }
                )
                continue

            if tsv_count == json_count:
                matched_units += 1
                stats["matched_units"] += 1

                complete_units.append(
                    {
                        "work": work_id,
                        "unit": unit_name,
                        "directory": str(unit_dir),
                        "sentences": tsv_count,
                    }
                )
            else:
                mismatched_units += 1
                stats["mismatched_units"] += 1

                mismatch_units.append(
                    {
                        "work": work_id,
                        "unit": unit_name,
                        "directory": str(unit_dir),
                        "tsv_sentences": tsv_count,
                        "json_sentences": json_count,
                        "difference": json_count - tsv_count,
                        "tsv": str(relative_tsv),
                        "json": str(relative_json),
                    }
                )

        logger.write("")
        logger.write("COMPLETE UNITS")
        logger.write("=" * 100)

        if complete_units:
            for item in complete_units:
                logger.write(
                    f"[OK] {item['directory']} | "
                    f"sentences={item['sentences']}"
                )
        else:
            logger.write("No complete units found.")

        logger.write("")
        logger.write("STATISTICS BY WORK")
        logger.write("=" * 100)

        for work_id in sorted(work_stats):
            stats = work_stats[work_id]

            logger.write(
                f"{work_id} | "
                f"units={stats['total_units']} | "
                f"matched={stats['matched_units']} | "
                f"mismatched={stats['mismatched_units']} | "
                f"missing_json={stats['missing_json_units']} | "
                f"read_errors={stats['read_errors']} | "
                f"tsv_sentences={stats['tsv_sentences']} | "
                f"json_sentences={stats['json_sentences']}"
            )

        logger.write("")
        logger.write("MISSING JSON")
        logger.write("=" * 100)

        if missing_units:
            for item in missing_units:
                logger.write(f"[MISSING] {item['directory']}")
                logger.write(f"  Unit          : {item['unit']}")
                logger.write(f"  TSV sentences : {item['tsv_sentences']}")
                logger.write(f"  TSV file      : {item['tsv']}")
                logger.write(f"  Expected JSON : {item['expected_json']}")
                logger.write("-" * 100)
        else:
            logger.write("No missing JSON files.")

        logger.write("")
        logger.write("MISMATCHED SENTENCE COUNTS")
        logger.write("=" * 100)

        if mismatch_units:
            for item in mismatch_units:
                logger.write(f"[MISMATCH] {item['directory']}")
                logger.write(f"  Unit           : {item['unit']}")
                logger.write(f"  TSV sentences  : {item['tsv_sentences']}")
                logger.write(f"  JSON sentences : {item['json_sentences']}")
                logger.write(f"  Difference     : {item['difference']:+d}")
                logger.write(f"  TSV file       : {item['tsv']}")
                logger.write(f"  JSON file      : {item['json']}")
                logger.write("-" * 100)
        else:
            logger.write("No mismatched sentence counts.")

        logger.write("")
        logger.write("READ ERRORS")
        logger.write("=" * 100)

        if error_units:
            for item in error_units:
                logger.write(f"[{item['type']}] {item['unit']}")
                logger.write(f"  File : {item['file']}")
                logger.write(f"  Error: {item['error']}")
                logger.write("-" * 100)
        else:
            logger.write("No read errors.")

        logger.write("")
        logger.write("GLOBAL SUMMARY")
        logger.write("=" * 100)
        logger.write(f"Total works          : {len(work_stats)}")
        logger.write(f"Total TSV units      : {total_units}")
        logger.write(f"Matched units        : {matched_units}")
        logger.write(f"Mismatched units     : {mismatched_units}")
        logger.write(f"Missing JSON units   : {missing_json_units}")
        logger.write(f"Read errors          : {read_errors}")
        logger.write(f"Total TSV sentences  : {total_tsv_sentences}")
        logger.write(f"Total JSON sentences : {total_json_sentences}")

        problem_count = (
            mismatched_units
            + missing_json_units
            + read_errors
        )

        if problem_count == 0:
            logger.write("Status: ALL UNITS ARE COMPLETE.")
        else:
            logger.write(f"Status: {problem_count} PROBLEM UNIT(S) FOUND.")

    print("")
    print(f"Report saved to: {log_path}")

    return 0 if (
        mismatched_units == 0
        and missing_json_units == 0
        and read_errors == 0
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
