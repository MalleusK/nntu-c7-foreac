from collections import Counter
import csv
import math
from pathlib import Path
import random
import string
from typing import Any
import zipfile


def generate_uniform_text(
    n: int = 100_000,
    alphabet: str = string.ascii_lowercase,
    seed: int | None = 260,
) -> str:
    if seed is not None:
        random.seed(seed)

    return "".join(random.choices(alphabet, k=n))


def compute_metrics(
    text: str, m: int = 26
) -> tuple[Counter, float, float, float, float]:
    n = len(text)
    if n == 0:
        return Counter(), 0.0, math.log2(m) if m > 0 else 0.0, 0.0, 0.0

    counts = Counter(text)

    h = -sum(
        (cnt / n) * math.log2(cnt / n) for cnt in counts.values() if cnt > 0
    )
    h_max = math.log2(m)

    redundancy = (1 - h / h_max) * 100.0 if h_max > 0 else 0.0
    total_info = n * h

    return counts, h, h_max, redundancy, total_info


def caesar_cipher(text: str, shift: int = 3) -> str:
    res = []
    for char in text:
        if "a" <= char <= "z":
            shifted = chr((ord(char) - ord("a") + shift) % 26 + ord("a"))
            res.append(shifted)
        else:
            res.append(char)

    return "".join(res)


def analyze_natural_text(
    filepath: Path | str, m: int = 26
) -> tuple[dict[str, float], float, float, float, float, int]:
    with open(filepath, "r", encoding="ascii", errors="ignore") as f:
        raw_text = f.read()

    filtered = [ch.lower() for ch in raw_text if "a" <= ch.lower() <= "z"]

    n = len(filtered)
    counts = Counter(filtered)
    probs = {ch: cnt / n for ch, cnt in counts.items()}

    h = -sum(p * math.log2(p) for p in probs.values() if p > 0)
    h_max = math.log2(m)

    redundancy = (1 - h / h_max) * 100.0 if h_max > 0 else 0.0
    total_info = n * h

    return probs, h, h_max, redundancy, total_info, n


def analyze_russian_text(
    filepath: Path | str, m: int = 32
) -> tuple[dict[str, float], float, float, float, float, int]:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()

    cleaned = raw_text.lower().replace("ё", "е")
    filtered = [ch for ch in cleaned if "а" <= ch <= "я"]

    n = len(filtered)
    counts = Counter(filtered)
    probs = {ch: cnt / n for ch, cnt in counts.items()}

    h = -sum(p * math.log2(p) for p in probs.values() if p > 0)
    h_max = math.log2(m)

    redundancy = (1 - h / h_max) * 100.0 if h_max > 0 else 0.0
    total_info = n * h

    return probs, h, h_max, redundancy, total_info, n


def compress_to_zip(
    input_file: Path,
    output_zip: Path,
    arcname: str | None = None,
    compresslevel: int = 9,
) -> int:
    if arcname is None:
        arcname = input_file.name

    with zipfile.ZipFile(
        output_zip,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=compresslevel,
    ) as zf:
        zf.write(input_file, arcname=arcname)

    return output_zip.stat().st_size


def export_frequencies_csv(
    filepath: Path,
    headers: list[str],
    rows: list[list[Any]],
) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def print_table(headers: list[str], rows: list[list[Any]]) -> None:
    widths = [
        max(len(str(val)) for val in [h] + [r[i] for r in rows])
        for i, h in enumerate(headers)
    ]
    header_str = " | ".join(f"{h:<{w}}" for h, w in zip(headers, widths))
    sep_str = "-+-".join("-" * w for w in widths)

    print(header_str)
    print(sep_str)
    for row in rows:
        print(" | ".join(f"{str(v):<{w}}" for v, w in zip(row, widths)))
