from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns


def configure_theme() -> None:
    """Configure a consistent dark theme for all plots."""
    plt.style.use("dark_background")
    sns.set_theme(style="dark")
    sns.set_palette("Spectral")
    # Reduce default DPI to lighten payload on mobile
    plt.rcParams["figure.dpi"] = 96


def style_ax_dark(ax, title: str, xlabel: str | None = None, ylabel: str | None = None) -> None:
    ax.set_facecolor("#0E1117")
    ax.set_title(title, fontsize=16, weight="bold", color="white")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12, color="white")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12, color="white")

    ax.tick_params(axis="x", rotation=45, colors="white")
    ax.tick_params(axis="y", colors="white")
    ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.4, color="gray")
    for spine in ax.spines.values():
        spine.set_visible(False)


def new_fig(size: tuple[int, int] = (8, 5)):
    return plt.subplots(figsize=size, facecolor="#0E1117")


