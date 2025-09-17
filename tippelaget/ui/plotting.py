from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path


def configure_theme() -> None:
    """Configure a consistent dark theme for all plots."""
    plt.style.use("dark_background")
    sns.set_theme(style="dark")
    sns.set_palette("Spectral")
    # Reduce default DPI further to lighten payload on mobile and desktop
    plt.rcParams["figure.dpi"] = 84


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


def new_fig(size: tuple[int, int] = (7, 4.2)):
    return plt.subplots(figsize=size, facecolor="#0E1117")



def show_fig(fig) -> None:
    """Display figure centered in a narrower column to avoid full-width stretching on desktop.

    On mobile, columns stack so the figure remains readable while keeping image payload reasonable.
    """
    left, center, right = st.columns([1, 4, 1])
    with center:
        st.pyplot(fig, use_container_width=True)


@st.cache_resource
def load_player_head_image(player_name: str):
    """Load a player's head image by name, trying repo root and CWD. Returns None if not found."""
    filename = f"{str(player_name).lower()}.png"
    candidate_dirs = [Path(__file__).resolve().parents[2], Path.cwd()]
    for base in candidate_dirs:
        path = base / filename
        if path.exists():
            try:
                return plt.imread(str(path))
            except Exception:
                return None
    return None


def add_image_markers(ax, x_values, y_values, image, zoom: float = 0.12) -> None:
    """Overlay image markers at data points.

    If image is None, this is a no-op.
    """
    if image is None:
        return
    for x, y in zip(x_values, y_values):
        try:
            im = OffsetImage(image, zoom=zoom)
            ab = AnnotationBbox(im, (x, y), frameon=False, box_alignment=(0.5, 0.5), zorder=5)
            ax.add_artist(ab)
        except Exception:
            # Fail silently to avoid breaking plots if image rendering fails
            pass

