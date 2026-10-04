from collections import Counter
from pathlib import Path
import string
import matplotlib.pyplot as plt
import numpy as np


def plot_uniform_and_caesar_hist(
    counts_orig: Counter,
    counts_cipher: Counter,
    total_len: int,
    output_path: Path,
    shift: int = 3,
) -> None:
    plt.style.use("default")

    alphabet = list(string.ascii_lowercase)
    m = len(alphabet)
    p_theo = 1.0 / m

    p_orig = [counts_orig.get(c, 0) / total_len for c in alphabet]
    p_cipher = [counts_cipher.get(c, 0) / total_len for c in alphabet]

    fig, (ax1, ax2) = plt.subplots(
        nrows=2,
        ncols=1,
        figsize=(10, 6),
        sharex=True,
        sharey=True,
    )

    x = np.arange(m)
    bar_width = 0.65

    ax1.bar(x, p_orig, width=bar_width, label="Исходный текст")
    ax1.axhline(
        p_theo,
        color="crimson",
        linestyle="--",
        label=f"Теоретическая вероятность (1/{m})",
    )
    ax1.set_ylabel("Вероятность")
    ax1.set_title("Исходный массив (равномерный)")
    ax1.grid(True)
    ax1.legend()

    ax2.bar(
        x,
        p_cipher,
        width=bar_width,
        color="tab:orange",
        label=f"Шифр Цезаря (k = {shift})",
    )
    ax2.axhline(
        p_theo,
        color="crimson",
        linestyle="--",
        label=f"Теоретическая вероятность (1/{m})",
    )
    ax2.set_xlabel("Символы алфавита")
    ax2.set_ylabel("Вероятность")
    ax2.set_title(f"После шифра Цезаря (сдвиг k = {shift})")
    ax2.set_xticks(x)
    ax2.set_xticklabels(alphabet)
    ax2.grid(True)
    ax2.legend()

    ax1.set_ylim(0, max(max(p_orig), max(p_cipher)) * 1.35)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_natural_distribution(
    probs: dict[str, float],
    output_path: Path,
    alphabet: list[str] | None = None,
) -> None:
    plt.style.use("default")

    if alphabet is None:
        alphabet = list(string.ascii_lowercase)

    m = len(alphabet)
    p_theo = 1.0 / m
    values = [probs.get(c, 0.0) for c in alphabet]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = np.arange(m)
    bar_width = 0.65

    ax.bar(x, values, width=bar_width, label="Эмпирическая частота")
    ax.axhline(
        p_theo,
        color="crimson",
        linestyle="--",
        label=f"Равновероятный источник (1/{m})",
    )

    ax.set_xlabel("Символы алфавита")
    ax.set_ylabel("Вероятность")
    ax.set_xticks(x)
    ax.set_xticklabels(alphabet)
    ax.set_ylim(0, max(values) * 1.15)
    ax.grid(True)
    ax.legend()

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)
