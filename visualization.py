"""
visualization.py – Matplotlib Animation and Heatmaps
======================================================
Provides all visual output for SeismoGrid:

  1. Static heatmaps panel  – intensity / damage / population (3-panel figure)
  2. Animated wave expansion – FuncAnimation showing the wave front growing
     outward with an overlay of live damage on the right panel.

Design notes
------------
• All rendering uses Matplotlib only – no external GUI frameworks.
• Colormaps are configured in config.py for easy theming.
• Optional contour rings mark intensity threshold levels on the heatmap.
• Figure layout uses GridSpec for precise control.
• Each function is independent and can be called in any order.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize

import config
from grid import SeismicGrid
from simulation import SeismicSimulation
from damage import DamageModel


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _add_epicenter_marker(ax: plt.Axes, epicenter: tuple[int, int]) -> None:
    """Draw a white star at the epicenter position."""
    er, ec = epicenter
    ax.plot(ec, er, marker="*", color="white", markersize=12,
            markeredgecolor="black", markeredgewidth=0.8, zorder=10,
            label="Epicenter")


def _add_contour_rings(ax: plt.Axes, intensity: np.ndarray) -> None:
    """Overlay contour rings at configured intensity threshold levels."""
    if not config.SHOW_CONTOURS:
        return
    levels = [lv for lv in config.CONTOUR_LEVELS if lv < intensity.max()]
    if levels:
        ax.contour(intensity, levels=levels, colors="cyan",
                   linewidths=0.6, alpha=0.7)


def _styled_colorbar(fig: plt.Figure, im, ax: plt.Axes, label: str) -> None:
    """Attach a compact, labelled colorbar to an axes."""
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label(label, fontsize=8)
    cb.ax.tick_params(labelsize=7)


# ---------------------------------------------------------------------------
# 1. Static three-panel heatmap
# ---------------------------------------------------------------------------

def plot_static_heatmaps(
    grid: SeismicGrid,
    sim: SeismicSimulation,
    damage: DamageModel,
) -> plt.Figure:
    """
    Render a three-panel static figure:
      Left   – Full intensity field (post wave-propagation)
      Centre – Normalised damage field
      Right  – Population density field

    Returns the Figure object so the caller can save or show it.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor("#0d0d0d")
    for ax in axes:
        ax.set_facecolor("#0d0d0d")
        ax.tick_params(colors="white", labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333333")

    # --- Intensity ---
    ax = axes[0]
    im0 = ax.imshow(sim.intensity_full, cmap=config.CMAP_INTENSITY,
                    origin="upper", interpolation="bilinear")
    _add_contour_rings(ax, sim.intensity_full)
    _add_epicenter_marker(ax, sim.epicenter)
    ax.set_title("Seismic Intensity  I = I₀/(1+k·d²)",
                 color="white", fontsize=9, pad=6)
    ax.set_xlabel("Column (grid cells)", color="white", fontsize=7)
    ax.set_ylabel("Row (grid cells)", color="white", fontsize=7)
    _styled_colorbar(fig, im0, ax, "Intensity (a.u.)")

    # --- Damage ---
    ax = axes[1]
    im1 = ax.imshow(damage.damage, cmap=config.CMAP_DAMAGE,
                    origin="upper", interpolation="bilinear", vmin=0, vmax=1)
    _add_epicenter_marker(ax, sim.epicenter)
    ax.set_title("Normalised Structural Damage",
                 color="white", fontsize=9, pad=6)
    ax.set_xlabel("Column (grid cells)", color="white", fontsize=7)
    _styled_colorbar(fig, im1, ax, "Damage score [0–1]")

    # --- Population density ---
    ax = axes[2]
    im2 = ax.imshow(grid.population_density, cmap=config.CMAP_POPULATION,
                    origin="upper", interpolation="bilinear")
    ax.set_title("Population Density",
                 color="white", fontsize=9, pad=6)
    ax.set_xlabel("Column (grid cells)", color="white", fontsize=7)
    _styled_colorbar(fig, im2, ax, "Persons per cell")

    fig.suptitle(
        "SeismoGrid – Simplified Seismic Impact Model  "
        "[Educational / Conceptual Only]",
        color="#aaaaaa", fontsize=10, y=1.01
    )
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 2. Animated wave expansion
# ---------------------------------------------------------------------------

def build_animation(
    grid: SeismicGrid,
    sim: SeismicSimulation,
) -> animation.FuncAnimation:
    """
    Build and return a FuncAnimation that shows the seismic wave expanding
    outward from the epicenter, with a live damage panel updating in sync.

    Layout (GridSpec 1×2):
      Left  – Expanding intensity wave front
      Right – Accumulated damage field (grows as wave advances)

    The animation is returned (not shown) so the caller can .show() or .save().
    """
    fig = plt.figure(figsize=(13, 6))
    fig.patch.set_facecolor("#0d0d0d")
    gs = GridSpec(1, 2, figure=fig, wspace=0.08)

    # ---- Axes setup -------------------------------------------------------
    ax_wave   = fig.add_subplot(gs[0, 0])
    ax_damage = fig.add_subplot(gs[0, 1])

    for ax in (ax_wave, ax_damage):
        ax.set_facecolor("#0d0d0d")
        ax.tick_params(colors="white", labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333333")

    # Shared intensity normalisation (fixed to full-field max for consistency)
    int_norm = Normalize(vmin=0, vmax=sim.intensity_full.max())
    dmg_norm = Normalize(vmin=0, vmax=1)

    # Initial blank frames
    blank = np.zeros((grid.size, grid.size))

    im_wave = ax_wave.imshow(
        blank, cmap=config.CMAP_INTENSITY, norm=int_norm,
        origin="upper", interpolation="bilinear", animated=True
    )
    im_dmg = ax_damage.imshow(
        blank, cmap=config.CMAP_DAMAGE, norm=dmg_norm,
        origin="upper", interpolation="bilinear", animated=True
    )

    # Epicenter markers
    for ax in (ax_wave, ax_damage):
        _add_epicenter_marker(ax, sim.epicenter)

    # Colorbars
    _styled_colorbar(fig, im_wave, ax_wave, "Intensity (a.u.)")
    _styled_colorbar(fig, im_dmg,  ax_damage, "Damage [0–1]")

    # Labels
    ax_wave.set_title("Wave Front Expansion", color="white", fontsize=9)
    ax_damage.set_title("Structural Damage (cumulative)", color="white", fontsize=9)
    ax_wave.set_xlabel("Column", color="white", fontsize=7)
    ax_wave.set_ylabel("Row",    color="white", fontsize=7)
    ax_damage.set_xlabel("Column", color="white", fontsize=7)

    # Time-step counter text
    time_text = ax_wave.text(
        0.02, 0.96, "", transform=ax_wave.transAxes,
        color="white", fontsize=8, va="top",
        bbox=dict(boxstyle="round,pad=0.3", fc="#1a1a1a", alpha=0.7)
    )

    # Wave-front circle artist (thin ring) -----------
    wave_circle = plt.Circle(
        (sim.epicenter[1], sim.epicenter[0]),   # (x=col, y=row)
        radius=0, fill=False, edgecolor="cyan", linewidth=1.2, alpha=0.8
    )
    ax_wave.add_patch(wave_circle)

    fig.suptitle(
        "SeismoGrid – Animated Wave Propagation  [Educational Only]",
        color="#aaaaaa", fontsize=9, y=1.01
    )

    # ---- Animation function -----------------------------------------------
    def _update(frame: int):
        intensity_frame = sim.compute_frame(frame)
        damage_frame    = DamageModel.from_frame(grid, intensity_frame)

        im_wave.set_data(intensity_frame)
        im_dmg.set_data(damage_frame.damage)

        # Advance wave-front ring radius
        radius = (frame + 1) * sim.radius_step
        wave_circle.set_radius(radius)

        time_text.set_text(
            f"Step {frame + 1}/{sim.time_steps}\n"
            f"Radius: {radius:.1f} cells\n"
            f"Affected: {damage_frame.total_affected():,.0f}"
        )
        return im_wave, im_dmg, wave_circle, time_text

    anim = animation.FuncAnimation(
        fig,
        _update,
        frames=sim.time_steps,
        interval=int(1000 / config.ANIMATION_FPS),
        blit=True,
        repeat=False,
    )
    return anim


# ---------------------------------------------------------------------------
# 3. Affected population bar chart (bonus summary panel)
# ---------------------------------------------------------------------------

def plot_population_summary(
    grid: SeismicGrid,
    damage: DamageModel,
) -> plt.Figure:
    """
    Render a simple bar chart showing total population vs. estimated affected
    population, plus a damage-fraction pie chart.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor("#0d0d0d")

    for ax in (ax1, ax2):
        ax.set_facecolor("#111111")
        ax.tick_params(colors="white", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333333")

    # --- Bar: population comparison ---
    categories = ["Total Population", "Estimated Affected"]
    values = [grid.population_density.sum(), damage.total_affected()]
    colors = ["#4a90d9", "#e07070"]
    bars = ax1.bar(categories, values, color=colors, width=0.5, edgecolor="#555555")
    ax1.set_ylabel("Persons", color="white", fontsize=9)
    ax1.set_title("Population Impact Estimate", color="white", fontsize=9)
    ax1.yaxis.label.set_color("white")
    for bar, val in zip(bars, values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.01,
            f"{val:,.0f}",
            ha="center", va="bottom", color="white", fontsize=8
        )

    # --- Pie: damaged vs undamaged area ---
    damaged_frac = damage.damaged_area_fraction()
    sizes  = [damaged_frac, 1.0 - damaged_frac]
    labels = [
        f"Significantly\nDamaged\n({damaged_frac*100:.1f}%)",
        f"Below Threshold\n({(1-damaged_frac)*100:.1f}%)"
    ]
    wedge_props = {"linewidth": 0.5, "edgecolor": "#333333"}
    ax2.pie(
        sizes, labels=labels, colors=["#e07070", "#4a90d9"],
        wedgeprops=wedge_props, textprops={"color": "white", "fontsize": 8},
        startangle=90
    )
    ax2.set_title("Grid Area Damage Fraction", color="white", fontsize=9)

    fig.suptitle(
        "SeismoGrid – Impact Summary  [Educational / Conceptual Only]",
        color="#aaaaaa", fontsize=9, y=1.02
    )
    fig.tight_layout()
    return fig
