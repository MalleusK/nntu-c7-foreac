from pathlib import Path

from entropy_core import (
    analyze_russian_text,
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

    input_file = data_dir / "war_peace_ru.txt"
    if not input_file.exists():
        alt_file = data_dir / "war_peace_rus.txt"
        if alt_file.exists():
            input_file = alt_file

    probs, h, h_max, redundancy, _, n = analyze_russian_text(input_file, m=32)

    zip_file = data_dir / "war_peace_ru.zip"
    size_raw = input_file.stat().st_size
    size_zip = compress_to_zip(input_file, zip_file)
    k_comp = size_raw / size_zip if size_zip > 0 else 0.0

    # 1. Генерация графика
    ru_alphabet = [chr(c) for c in range(ord("а"), ord("я") + 1)]
    svg_output = images_dir / "task3_ru_letter_distribution.svg"
    plot_natural_distribution(
        probs=probs, output_path=svg_output, alphabet=ru_alphabet
    )

    # 2. Вывод результатов расчёта
    print(
        f"Война и мир (RU): H={h:.4f}, H_max={h_max:.4f}, R={redundancy:.2f}%, "
        f"размер={size_raw} Б, ZIP={size_zip} Б, K={k_comp:.3f}, N={n}"
    )
    print(f"График сохранён в: {svg_output.relative_to(assets_dir.parent)}")

    # 3. Экспорт в CSV и вывод таблицы частот (Приложение Б, Таблица Б.2)
    csv_headers = ["symbol", "count", "probability"]
    display_headers = ["Символ", "Частота ni", "Вероятность pi"]
    rows = []
    for ch in ru_alphabet:
        cnt = int(round(probs.get(ch, 0.0) * n))
        p = probs.get(ch, 0.0)
        rows.append([ch, cnt, f"{p:.5f}"])

    csv_output = data_dir / "task3_ru_frequencies.csv"
    export_frequencies_csv(csv_output, csv_headers, rows)
    print(f"Таблица частот сохранена в: {csv_output.relative_to(assets_dir.parent)}\n")
    print_table(display_headers, rows)


if __name__ == "__main__":
    main()
