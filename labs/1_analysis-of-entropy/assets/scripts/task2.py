from pathlib import Path
import string

from entropy_core import (
    analyze_natural_text,
    compress_to_zip,
    export_frequencies_csv,
    print_table,
)
from plot_charts import plot_natural_distribution


def main():
    script_dir = Path(__file__).resolve().parent
    assets_dir = script_dir.parent
    data_dir = assets_dir / "data"
    images_dir = assets_dir / "images"

    data_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    input_file = data_dir / "war_peace_en.txt"
    if not input_file.exists():
        alt_file = data_dir / "war_peace.txt"
        if alt_file.exists():
            input_file = alt_file

    probs, h, h_max, redundancy, _, n = analyze_natural_text(input_file, m=26)

    zip_file = data_dir / "war_peace_en.zip"
    size_raw = input_file.stat().st_size
    size_zip = compress_to_zip(input_file, zip_file)
    k_comp = size_raw / size_zip if size_zip > 0 else 0.0

    # 1. Генерация графика
    svg_output = images_dir / "task2_en_letter_distribution.svg"
    plot_natural_distribution(probs=probs, output_path=svg_output)

    # 2. Вывод результатов расчёта
    print(
        f"Война и мир (EN): H={h:.4f}, H_max={h_max:.4f}, R={redundancy:.2f}%, "
        f"размер={size_raw} Б, ZIP={size_zip} Б, K={k_comp:.3f}, N={n}"
    )
    print(f"График сохранён в: {svg_output.relative_to(assets_dir.parent)}")

    # 3. Экспорт в CSV и вывод таблицы частот (Приложение Б, Таблица Б.1)
    alphabet = list(string.ascii_lowercase)
    csv_headers = ["symbol", "count", "probability"]
    display_headers = ["Символ", "Частота ni", "Вероятность pi"]
    rows = []
    for ch in alphabet:
        cnt = int(round(probs.get(ch, 0.0) * n))
        p = probs.get(ch, 0.0)
        rows.append([ch, cnt, f"{p:.5f}"])

    csv_output = data_dir / "task2_en_frequencies.csv"
    export_frequencies_csv(csv_output, csv_headers, rows)
    print(f"Таблица частот сохранена в: {csv_output.relative_to(assets_dir.parent)}\n")
    print_table(display_headers, rows)


if __name__ == "__main__":
    main()
