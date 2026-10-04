from pathlib import Path
import string

from entropy_core import (
    caesar_cipher,
    compute_metrics,
    compress_to_zip,
    export_frequencies_csv,
    generate_uniform_text,
    print_table,
)
from plot_charts import plot_uniform_and_caesar_hist


def main():
    script_dir = Path(__file__).resolve().parent
    assets_dir = script_dir.parent
    data_dir = assets_dir / "data"
    images_dir = assets_dir / "images"

    data_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    n_chars = 100_000
    shift = 3
    m = 26

    uniform_text = generate_uniform_text(n=n_chars, seed=260)
    counts_orig, h_orig, h_max, r_orig, _ = compute_metrics(uniform_text, m=m)

    caesar_text = caesar_cipher(uniform_text, shift=shift)
    counts_caesar, h_caesar, _, r_caesar, _ = compute_metrics(caesar_text, m=m)

    file_orig_txt = data_dir / "uniform.txt"
    file_caesar_txt = data_dir / "uniform_caesar.txt"

    file_orig_txt.write_text(uniform_text, encoding="ascii")
    file_caesar_txt.write_text(caesar_text, encoding="ascii")

    size_orig = file_orig_txt.stat().st_size
    size_caesar = file_caesar_txt.stat().st_size

    file_orig_zip = data_dir / "uniform.zip"
    file_caesar_zip = data_dir / "uniform_caesar.zip"

    zip_size_orig = compress_to_zip(file_orig_txt, file_orig_zip)
    zip_size_caesar = compress_to_zip(file_caesar_txt, file_caesar_zip)

    k_comp_orig = size_orig / zip_size_orig if zip_size_orig > 0 else 0.0
    k_comp_caesar = size_caesar / zip_size_caesar if zip_size_caesar > 0 else 0.0

    # 1. Генерация графика
    svg_output = images_dir / "task1_uniform_caesar_hist.svg"
    plot_uniform_and_caesar_hist(
        counts_orig=counts_orig,
        counts_cipher=counts_caesar,
        total_len=n_chars,
        output_path=svg_output,
        shift=shift,
    )

    # 2. Вывод результатов расчёта
    print(
        f"Исходный случайный:  H={h_orig:.4f}, H_max={h_max:.4f}, R={r_orig:.3f}%, "
        f"размер={size_orig} Б, ZIP={zip_size_orig} Б, K={k_comp_orig:.3f}"
    )
    print(
        f"Шифр Цезаря (k={shift}): H={h_caesar:.4f}, H_max={h_max:.4f}, R={r_caesar:.3f}%, "
        f"размер={size_caesar} Б, ZIP={zip_size_caesar} Б, K={k_comp_caesar:.3f}"
    )
    print(f"График сохранён в: {svg_output.relative_to(assets_dir.parent)}")

    # 3. Экспорт в CSV и вывод таблицы частот (Приложение Б, Таблица Б.3)
    alphabet = list(string.ascii_lowercase)
    csv_headers = [
        "symbol",
        "orig_count",
        "orig_probability",
        "cipher_count",
        "cipher_probability",
    ]
    display_headers = [
        "Символ",
        "Исходн. ni",
        "Исходн. pi",
        "Шифр ni",
        "Шифр pi",
    ]
    rows = []
    for ch in alphabet:
        c_orig = counts_orig.get(ch, 0)
        p_orig = c_orig / n_chars
        c_ciph = counts_caesar.get(ch, 0)
        p_ciph = c_ciph / n_chars
        rows.append([ch, c_orig, f"{p_orig:.5f}", c_ciph, f"{p_ciph:.5f}"])

    csv_output = data_dir / "task1_uniform_frequencies.csv"
    export_frequencies_csv(csv_output, csv_headers, rows)
    print(f"Таблица частот сохранена в: {csv_output.relative_to(assets_dir.parent)}\n")
    print_table(display_headers, rows)


if __name__ == "__main__":
    main()
