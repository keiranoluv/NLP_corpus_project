from pathlib import Path
import argparse
import csv
import re


# Do not include ； here.
# In historical texts, ； is often used to separate list items, not full sentences.
END_PUNCT = "。！？"


WORKS = {
    "HCH_009": {
        "title_vi": "Kim Sử",
        "title_zh": "金史",
        "input": "金史_full.txt",
    },
    "HCH_010": {
        "title_vi": "Liêu Sử",
        "title_zh": "遼史",
        "input": "遼史_full.txt",
    },
    "HCH_011": {
        "title_vi": "Lương Thư",
        "title_zh": "梁書",
        "input": "梁書_full.txt",
    },
    "HCH_012": {
        "title_vi": "Minh Sử",
        "title_zh": "明史",
        "input": "明史_full.txt",
    },
    "HCH_013": {
        "title_vi": "Minh Sử Ký Sự Bản Mạt",
        "title_zh": "明史紀事本末",
        "input": "明史紀事本末_full.txt",
    },
    "HCH_014": {
        "title_vi": "Mục Thiên Tử Truyện",
        "title_zh": "穆天子傳",
        "input": "Mục Thiên Tử Truyện - 穆天子傳_full.txt",
    },
    "HCH_015": {
        "title_vi": "Nam Tề Thư",
        "title_zh": "南齊書",
        "input": "南齊書_full.txt",
    },
    "HCH_016": {
        "title_vi": "Ngô Việt Xuân Thu",
        "title_zh": "吳越春秋",
        "input": "Ngô Việt Xuân Thu - 吳越春秋_full.txt",
    },
}


def normalize_text(text: str) -> str:
    """
    Normalize input text lightly without changing the original Classical Chinese content.
    """
    text = text.replace("\ufeff", "")
    text = text.replace("\u3000", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chinese_number_to_int(text: str) -> int | None:
    """
    Convert simple Chinese numerals to int.
    Supports common volume numbers like 一, 二, 十, 十一, 二十, 一百二十.
    """
    text = text.strip()

    if not text:
        return None

    if text.isdigit():
        return int(text)

    digits = {
        "零": 0,
        "〇": 0,
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
    }

    units = {
        "十": 10,
        "百": 100,
        "千": 1000,
    }

    total = 0
    current = 0

    for char in text:
        if char in digits:
            current = digits[char]
        elif char in units:
            unit = units[char]
            if current == 0:
                current = 1
            total += current * unit
            current = 0
        else:
            return None

    total += current

    return total if total > 0 else None


def volume_number_to_int(volume_raw: str) -> int | None:
    """
    Normalize volume marker number to int.
    Examples:
    - 1 -> 1
    - 001 -> 1
    - 一 -> 1
    - 十一 -> 11
    """
    volume_raw = volume_raw.strip()

    if volume_raw.isdigit():
        return int(volume_raw)

    return chinese_number_to_int(volume_raw)


def safe_dir_name(text: str) -> str:
    """
    Make a short safe directory name from a Chinese heading.
    """
    text = text.strip()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[\\/:\*\?\"<>\|]", "_", text)
    return text[:40] if text else "section"


def split_units(text: str) -> list[tuple[int, str, str, str]]:
    """
    Split source text into logical units.

    Priority:
    1. If the file has volume headings like '# 卷1', '# 卷01', '# 卷一',
       split by volume.
    2. If there is no volume heading, split by level-1 headings '# ...'.
       This is needed for 吳越春秋, which is divided by 傳 rather than 卷.

    Returns:
        [(unit_no, unit_kind, unit_title, unit_text), ...]

    unit_kind:
        - 'volume'
        - 'section'
    """
    text = normalize_text(text)

    # Only level-1 markdown heading, not '##'.
    volume_pattern = re.compile(
        r"(?m)^#(?!#)\s*卷\s*([0-9一二三四五六七八九十百千〇零]+)\s*$"
    )

    volume_matches = list(volume_pattern.finditer(text))

    if volume_matches:
        # For volume-based books, discard front matter before first volume.
        text = text[volume_matches[0].start():]
        volume_matches = list(volume_pattern.finditer(text))

        units = []

        for idx, match in enumerate(volume_matches):
            volume_raw = match.group(1)
            volume_no = volume_number_to_int(volume_raw)

            if volume_no is None:
                volume_no = idx + 1

            start = match.end()
            end = volume_matches[idx + 1].start() if idx + 1 < len(volume_matches) else len(text)

            unit_title = match.group(0).strip().lstrip("#").strip()
            unit_text = text[start:end].strip()

            if unit_text:
                units.append((volume_no, "volume", unit_title, unit_text))

        return units

    # Fallback for non-volume books, e.g. 吳越春秋.
    # Use only level-1 heading '# ...', not '## ...', to avoid duplicate headings.
    section_pattern = re.compile(r"(?m)^#(?!#)\s*(.+?)\s*$")

    skip_section_titles = {
        "序",
        "序一",
        "序二",
        "附錄",
        "附录",
        "牒",
        "百衲本跋",
    }

    first_valid_start = None
    for match in section_pattern.finditer(text):
        title = match.group(1).strip()
        if title not in skip_section_titles:
            first_valid_start = match.start()
            break

    if first_valid_start is not None:
        text = text[first_valid_start:]

    section_matches = []
    for match in section_pattern.finditer(text):
        title = match.group(1).strip()
        if title in skip_section_titles:
            continue
        section_matches.append(match)

    if not section_matches:
        return [(1, "section", "section1", text)]

    units = []

    for idx, match in enumerate(section_matches):
        unit_no = idx + 1
        unit_title = match.group(1).strip()

        start = match.end()
        end = section_matches[idx + 1].start() if idx + 1 < len(section_matches) else len(text)

        unit_text = text[start:end].strip()

        if unit_text:
            units.append((unit_no, "section", unit_title, unit_text))

    return units


def clean_line(line: str) -> str:
    """
    Clean one line lightly.
    """
    line = line.strip()

    # Remove leading bullet-like symbols.
    line = re.sub(r"^[○●◎◇◆]+", "", line)

    # Remove inline wiki-style note markers like [ 1 ], [註 1].
    line = re.sub(r"\[\s*註?\s*\d+\s*\]", "", line)
    line = re.sub(r"\[\s*\d+\s*\]", "", line)

    # Remove excessive whitespace inside line.
    line = re.sub(r"\s+", "", line)

    return line


def remove_annotations(text: str) -> str:
    """
    Remove inline editorial annotations before sentence segmentation.

    Common source forms:
    - 〈 ... 〉
    - （ ... ）
    - [ ... ]

    Book-title brackets 《...》 are intentionally kept.
    """
    text = re.sub(r"〈.*?〉", "", text, flags=re.DOTALL)
    text = re.sub(r"（.*?）", "", text, flags=re.DOTALL)
    text = re.sub(r"\[.*?\]", "", text, flags=re.DOTALL)
    return text


def fix_common_quote_errors(text: str) -> str:
    """
    Fix common quote typos in source text.

    Some source texts contain patterns like 曰：」 instead of 曰：「.
    This is only a conservative normalization for common speech-introducing words.
    """
    text = re.sub(r"([曰云謂言對詔問奏稱報])：」", r"\1：「", text)
    text = re.sub(r"([曰云謂言對詔問奏稱報])：『", r"\1：「", text)
    return text


def should_skip_line(line: str) -> bool:
    """
    Skip metadata, markdown headings, table of contents lines, and non-content lines.
    """
    raw = line.strip()
    compact = re.sub(r"\s+", "", raw)

    if not compact:
        return True

    # Skip footnote / collation lines.
    if compact.startswith("↑"):
        return True

    # Markdown headings from source files.
    # Unit splitting is already handled before segmentation.
    if raw.startswith("#"):
        return True

    skip_keywords = [
        "姊妹计划",
        "姊妹計劃",
        "数据项",
        "數據項",
        "Publicdomain",
        "本作品在全世界都属于",
        "本作品在全世界都屬於",
        "本北宋作品",
        "本清朝作品",
        "全文以中華書局",
        "校勘记",
        "校勘記",
    ]

    if any(keyword in compact for keyword in skip_keywords):
        return True

    # Skip standalone annotation headers only, not every line containing 注/註.
    if compact in {"注", "註"}:
        return True

    if compact.startswith("注") and len(compact) <= 20:
        return True

    if compact.startswith("註") and len(compact) <= 20:
        return True

    # Skip likely collation notes, but do not remove all lines containing 按/據.
    if compact.startswith("按") and ("原作" in compact or "據" in compact or "卷" in compact):
        return True

    standalone_titles = {
        "金史",
        "遼史",
        "辽史",
        "梁書",
        "梁书",
        "明史",
        "明史紀事本末",
        "穆天子傳",
        "穆天子传",
        "南齊書",
        "南齐书",
        "吳越春秋",
        "吴越春秋",
        "附錄",
        "附录",
        "序",
        "自序",
        "牒",
        "百衲本跋",
    }

    if compact in standalone_titles:
        return True

    has_end_punct = any(punct in compact for punct in END_PUNCT)

    # Skip section/catalogue-like lines without sentence-ending punctuation.
    if not has_end_punct:
        heading_keywords = [
            "列傳第",
            "列传第",
            "本紀第",
            "本纪第",
            "志第",
            "表第",
        ]

        if any(keyword in compact for keyword in heading_keywords):
            return True

        title_patterns = [
            r"^卷[一二三四五六七八九十百千\d]+$",
            r"^卷[一二三四五六七八九十百千\d]+.*$",
            r"^本紀.*$",
            r"^本纪.*$",
            r"^列傳.*$",
            r"^列传.*$",
            r"^志第.*$",
            r"^表第.*$",
            r"^.*傳$",
            r"^.*传$",
            r"^.*上$",
            r"^.*下$",
        ]

        for pattern in title_patterns:
            if re.match(pattern, compact) and len(compact) <= 40:
                return True

    official_list_headers = {
        "修史官員",
        "修史官员",
        "領三史事",
        "领三史事",
        "都總裁",
        "都总裁",
        "總裁官",
        "总裁官",
        "纂修官",
        "提調官",
        "提调官",
        "金史公文",
        "三史凡例",
        "進遼史表",
        "进辽史表",
        "進《金史》表",
        "进《金史》表",
    }

    if compact in official_list_headers:
        return True

    # Skip short heading-like non-sentence lines.
    # Since these source files are mostly punctuated, short lines without punctuation
    # are more likely headings/catalogue items than real sentence fragments.
    if len(compact) <= 30 and not any(punct in compact for punct in "。！？；，："):
        return True

    return False


def looks_like_content_line(line: str) -> bool:
    """
    Decide whether a cleaned line should be kept as content.
    """
    if not line:
        return False

    if any(punct in line for punct in END_PUNCT):
        return True

    if len(line) >= 30:
        return True

    if any(punct in line for punct in "，：；") and len(line) >= 15:
        return True

    return False


def is_appendix_official_list_line(line: str) -> bool:
    """
    Filter common official-list lines from appendices.
    These lines often contain many titles and names but are not main historical content.
    """
    compact = re.sub(r"\s+", "", line)

    official_terms = [
        "開府儀同三司",
        "开府仪同三司",
        "中書右丞相",
        "中书右丞相",
        "中書左丞相",
        "中书左丞相",
        "監修國史",
        "监修国史",
        "翰林學士",
        "翰林学士",
        "御史大夫",
        "參知政事",
        "参知政事",
        "左右司",
        "臣",
    ]

    hit_count = sum(1 for term in official_terms if term in compact)

    return hit_count >= 3 and "。" not in compact


def starts_with_time_marker(text: str) -> bool:
    """
    Detect common historical time markers.

    This is used after a closing quote. For example:
    「...。」丙寅，尚書左丞相...
    should be split into:
    「...。」
    丙寅，尚書左丞相...
    """
    text = text.strip()
    if not text:
        return False

    heavenly_stems = "甲乙丙丁戊己庚辛壬癸"
    earthly_branches = "子丑寅卯辰巳午未申酉戌亥"

    # Sexagenary day marker, e.g. 甲寅，丙寅，辛未.
    if len(text) >= 3 and text[0] in heavenly_stems and text[1] in earthly_branches:
        if text[2] in "，。；、":
            return True

    # Month / leap month marker, e.g. 正月，二月，閏月.
    month_markers = [
        "正月",
        "二月",
        "三月",
        "四月",
        "五月",
        "六月",
        "七月",
        "八月",
        "九月",
        "十月",
        "十一月",
        "十二月",
        "閏月",
        "闰月",
    ]

    if any(text.startswith(marker) for marker in month_markers):
        return True

    # Year marker, e.g. 二年，三年，明昌三年.
    if re.match(r"^[一二三四五六七八九十元][一二三四五六七八九十]*年[，。；、]", text):
        return True

    return False


def split_after_quote_before_time_marker(text: str) -> str:
    """
    Insert a sentence boundary after a closing quote if a new time marker follows.

    Example:
    ...毋拒而不從。」丙寅，尚書左丞相...
    =>
    ...毋拒而不從。」
    丙寅，尚書左丞相...
    """
    result = []
    i = 0

    while i < len(text):
        result.append(text[i])

        if text[i] in "」』":
            rest = text[i + 1 :]
            if starts_with_time_marker(rest):
                result.append("\n")

        i += 1

    return "".join(result)


def insert_hard_boundaries(text: str) -> str:
    """
    Insert hard sentence boundaries for common historical-text section markers.
    """
    # 贊曰 usually starts a new comment/summary section.
    text = re.sub(r"(?=贊曰[：:])", "\n", text)

    # Keep the previous rule: quote followed by a new time marker should split.
    text = split_after_quote_before_time_marker(text)

    return text


def smart_split_sentences(text: str, max_buffer_len: int = 500) -> list[str]:
    """
    Split sentences by 。！？ with safer quote handling.

    Rules:
    - Split at 。！？ outside quotes.
    - If punctuation appears inside 「...」 or 『...』, wait until the closing quote.
    - If quotes are broken and the buffer becomes too long, force split.
    - Split before hard section markers such as 贊曰：.
    """
    text = remove_annotations(text)
    text = fix_common_quote_errors(text)
    text = insert_hard_boundaries(text)

    sentences = []
    buffer = []
    quote_stack = []

    quote_pairs = {
        "「": "」",
        "『": "』",
    }
    closing_quotes = set(quote_pairs.values())

    last_char_was_end_punct = False

    for char in text:
        # Hard boundary inserted before markers like 贊曰.
        if char == "\n":
            sentence = "".join(buffer).strip()
            sentence = sentence.lstrip("」』")
            if sentence:
                sentences.append(sentence)
            buffer = []
            quote_stack = []
            last_char_was_end_punct = False
            continue

        buffer.append(char)

        if char in quote_pairs:
            quote_stack.append(quote_pairs[char])
            last_char_was_end_punct = False
            continue

        if char in closing_quotes:
            if quote_stack and char == quote_stack[-1]:
                quote_stack.pop()

            # Case: 「...。」 should split after 」.
            if last_char_was_end_punct and not quote_stack:
                sentence = "".join(buffer).strip()
                sentence = sentence.lstrip("」』")
                if sentence:
                    sentences.append(sentence)
                buffer = []
                last_char_was_end_punct = False

            continue

        if char in END_PUNCT:
            last_char_was_end_punct = True

            # Normal case: punctuation outside quotes.
            if not quote_stack:
                sentence = "".join(buffer).strip()
                sentence = sentence.lstrip("」』")
                if sentence:
                    sentences.append(sentence)
                buffer = []
                last_char_was_end_punct = False

            # Safety case: broken quote causes a very long buffer.
            elif len(buffer) >= max_buffer_len:
                sentence = "".join(buffer).strip()
                sentence = sentence.lstrip("」』")
                if sentence:
                    sentences.append(sentence)
                buffer = []
                quote_stack = []
                last_char_was_end_punct = False

            continue

        # Extra safety: if buffer grows too long even without hitting punctuation,
        # force split at a comma-like boundary.
        if quote_stack and len(buffer) >= max_buffer_len and char in "，；：、":
            sentence = "".join(buffer).strip()
            sentence = sentence.lstrip("」』")
            if sentence:
                sentences.append(sentence)
            buffer = []
            quote_stack = []
            last_char_was_end_punct = False
            continue

        last_char_was_end_punct = False

    tail = "".join(buffer).strip()
    tail = tail.lstrip("」』")
    if tail:
        sentences.append(tail)

    return sentences


def further_split_long_sentence(sentence: str, max_len: int) -> list[str]:
    """
    If a sentence is too long, split softly by comma-like punctuation.
    Disabled by default.
    """
    if max_len <= 0 or len(sentence) <= max_len:
        return [sentence]

    soft_punct = "，、：；"
    parts = re.split(rf"(?<=[{re.escape(soft_punct)}])", sentence)

    result = []
    buffer = ""

    for part in parts:
        if not part:
            continue

        if len(buffer) + len(part) <= max_len:
            buffer += part
        else:
            if buffer:
                result.append(buffer)
            buffer = part

    if buffer:
        result.append(buffer)

    return result


def segment_unit_text(text: str, min_len: int = 2, max_len: int = 0) -> list[str]:
    """
    Segment one logical unit only.
    Important: this does not re-split by volume/section.
    """
    text = normalize_text(text)

    cleaned_lines = []

    for line in text.splitlines():
        if should_skip_line(line):
            continue

        line = clean_line(line)

        if not looks_like_content_line(line):
            continue

        if is_appendix_official_list_line(line):
            continue

        cleaned_lines.append(line)

    merged_text = "\n".join(cleaned_lines)
    merged_text = merged_text.replace("\n", "")

    raw_sentences = smart_split_sentences(merged_text)

    final_sentences = []
    for sentence in raw_sentences:
        sentence = sentence.strip()

        if len(sentence) < min_len:
            continue

        sub_sentences = further_split_long_sentence(sentence, max_len=max_len)

        for sub_sentence in sub_sentences:
            sub_sentence = sub_sentence.strip()
            if len(sub_sentence) >= min_len:
                final_sentences.append(sub_sentence)

    return final_sentences


def write_tsv(sentences: list[str], output_path: Path, prefix: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t", lineterminator="\n")
        for idx, sentence in enumerate(sentences, start=1):
            sentence_id = f"{prefix}_{idx:06d}"
            writer.writerow([sentence_id, sentence])


def process_one_work(
    code: str,
    data_dir: Path,
    output_root: Path,
    min_len: int = 2,
    max_len: int = 0,
) -> None:
    if code not in WORKS:
        valid_codes = ", ".join(sorted(WORKS))
        raise ValueError(f"Unknown code: {code}. Valid codes: {valid_codes}")

    work = WORKS[code]
    input_path = data_dir / work["input"]
    output_dir = output_root / code

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    units = split_units(text)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"Code: {code}")
    print(f"Title VI: {work['title_vi']}")
    print(f"Title ZH: {work['title_zh']}")
    print(f"Input: {input_path}")
    print(f"Output dir: {output_dir}")
    print(f"Total units: {len(units)}")

    total_sentences = 0

    for unit_no, unit_kind, unit_title, unit_text in units:
        unit_prefix = f"{code}_{unit_no:03d}"

        if unit_kind == "volume":
            unit_dir_name = unit_prefix
        else:
            unit_dir_name = f"{unit_prefix}_{safe_dir_name(unit_title)}"

        unit_dir = output_dir / unit_dir_name
        output_path = unit_dir / f"{unit_prefix}_seg.tsv"

        sentences = segment_unit_text(
            unit_text,
            min_len=min_len,
            max_len=max_len,
        )

        write_tsv(sentences, output_path, unit_prefix)

        total_sentences += len(sentences)

        print(
            f"{unit_prefix}: {unit_kind} | {unit_title} -> "
            f"{len(sentences)} sentences -> {output_path}"
        )

    print(f"Total sentences: {total_sentences}")


def main():
    parser = argparse.ArgumentParser(
        description="Mapped unit-aware sentence segmentation for HCH corpus."
    )

    parser.add_argument(
        "--code",
        "-c",
        choices=sorted(WORKS.keys()),
        help="Work code, e.g. HCH_009. Required unless --all is used.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all mapped works.",
    )

    parser.add_argument(
        "--data-dir",
        default="data",
        help="Input data directory. Default: data",
    )

    parser.add_argument(
        "--output-root",
        default="output/by_unit",
        help="Output root directory. Default: output/by_unit",
    )

    parser.add_argument(
        "--min-len",
        type=int,
        default=2,
        help="Minimum sentence length to keep. Default: 2",
    )

    parser.add_argument(
        "--max-len",
        type=int,
        default=0,
        help=(
            "If > 0, further split sentences longer than this length by ，、：；. "
            "Default: 0 means disabled."
        ),
    )

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_root = Path(args.output_root)

    if args.all:
        codes = sorted(WORKS.keys())
    else:
        if not args.code:
            parser.error("--code is required unless --all is used")
        codes = [args.code]

    for code in codes:
        process_one_work(
            code=code,
            data_dir=data_dir,
            output_root=output_root,
            min_len=args.min_len,
            max_len=args.max_len,
        )


if __name__ == "__main__":
    main()
