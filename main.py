"""
main.py – SeismoGrid Entry Point
==================================
Run from the command line:

    python main.py                           # default parameters from config.py
    python main.py --epicenter 30 70         # custom epicenter (row col)
    python main.py --I0 15 --k 0.005        # custom intensity / attenuation
    python main.py --grid-size 80            # smaller grid (faster)
    python main.py --time-steps 40           # fewer animation frames
    python main.py --seed 7                  # different random landscape
    python main.py --no-animation            # skip animation, show static only
    python main.py --save-animation out.gif  # save animation to GIF

All parameters have sensible defaults in config.py.

This module is intentionally thin – it wires together the other modules and
produces both console output and visual windows.  Application logic lives in
grid.py / simulation.py / damage.py / visualization.py.
"""

import argparse
import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ---- Internal modules -----------------------------------------------------
import config
from grid import SeismicGrid
from simulation import SeismicSimulation
from damage import DamageModel
import visualization as viz


# ===========================================================================
# CLI argument parsing
# ===========================================================================

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="SeismoGrid",
        description=(
            "SeismoGrid – Simplified Seismic Impact Simulation\n"
            "===================================================\n"
            "EDUCATIONAL / RESEARCH PROTOTYPE ONLY.\n"
            "Not for real-world disaster forecasting.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--grid-size", type=int, default=config.GRID_SIZE, metavar="N",
        help=f"Side length of the square grid in cells (default: {config.GRID_SIZE})"
    )
    parser.add_argument(
        "--epicenter", type=int, nargs=2, default=list(config.EPICENTER),
        metavar=("ROW", "COL"),
        help=f"Epicenter grid coordinates (default: {config.EPICENTER[0]} {config.EPICENTER[1]})"
    )
    parser.add_argument(
        "--I0", type=float, default=config.INITIAL_INTENSITY,
        help=f"Initial epicentral intensity (default: {config.INITIAL_INTENSITY})"
    )
    parser.add_argument(
        "--k", type=float, default=config.ATTENUATION_CONSTANT,
        help=f"Attenuation constant k (default: {config.ATTENUATION_CONSTANT})"
    )
    parser.add_argument(
        "--time-steps", type=int, default=config.TIME_STEPS,
        help=f"Animation time steps (default: {config.TIME_STEPS})"
    )
    parser.add_argument(
        "--seed", type=int, default=config.RANDOM_SEED,
        help=f"Random seed for reproducibility (default: {config.RANDOM_SEED})"
    )
    parser.add_argument(
        "--no-animation", action="store_true",
        help="Skip the animated wave propagation; show static heatmaps only."
    )
    parser.add_argument(
        "--save-animation", type=str, default=None, metavar="FILE",
        help="Save animation to file (e.g. anim.gif or anim.mp4). Requires ffmpeg/pillow."
    )
    return parser.parse_args(argv)


# ===========================================================================
# Console banner and summary
# ===========================================================================

_BANNER = r"""
 ____       _                       ____      _     _ 
/ ___|  ___(_)___ _ __ ___   ___  / ___|_ __(_) __| |
\___ \ / _ \ / __| '_ ` _ \ / _ \| |  _| '__| |/ _` |
 ___) |  __/ \__ \ | | | | | (_) | |_| | |  | | (_| |
|____/ \___|_|___/_| |_| |_|\___/ \____|_|  |_|\__,_|

  Seismic Impact Simulation – Educational / Research Prototype
  ─────────────────────────────────────────────────────────────
  ⚠  NOT a real seismic hazard or loss-estimation tool.
  Intensity decay: I = I₀ / (1 + k·d²)  [isotropic, homogeneous]
"""


def print_summary(args: argparse.Namespace,
                  grid: SeismicGrid,
                  sim: SeismicSimulation,
                  damage: DamageModel) -> None:
    """Print a structured console summary after simulation completes."""
    sep = "─" * 52

    print(_BANNER)
    print(sep)
    print("  SIMULATION PARAMETERS")
    print(sep)
    print(f"  Grid size          : {args.grid_size} × {args.grid_size} cells")
    print(f"  Epicenter          : row={args.epicenter[0]}, col={args.epicenter[1]}")
    print(f"  Initial intensity  : I₀ = {args.I0}")
    print(f"  Attenuation const  : k  = {args.k}")
    print(f"  Time steps         : {args.time_steps}")
    print(f"  Random seed        : {args.seed}")
    print()
    print(sep)
    print("  GRID STATISTICS")
    print(sep)
    for line in grid.summary().splitlines():
        print(f"  {line}")
    print()
    print(sep)
    print("  SEISMIC INTENSITY RESULTS")
    print(sep)
    print(f"  Peak intensity     : {sim.peak_intensity():.4f}")
    print(f"  Mean intensity     : {sim.mean_intensity():.4f}")
    for thr in [0.5, 1.0, 2.0, 4.0]:
        r = sim.radius_for_intensity(thr)
        print(f"  Radius @ I={thr:<4}   : {r:.1f} cells")
    print()
    print(sep)
    print("  DAMAGE & IMPACT RESULTS")
    print(sep)
    for line in damage.summary().splitlines():
        print(f"  {line}")
    print()
    print(sep)
    print("  EDUCATIONAL NOTES")
    print(sep)
    print("  • Isotropic propagation – no directional fault rupture effects.")
    print("  • Homogeneous medium – no geological heterogeneity or soil effects.")
    print("  • Linear damage model – real curves are non-linear (fragility CDFs).")
    print("  • No secondary hazards (liquefaction, fire, tsunami).")
    print("  • Population field is synthetic – no real census data.")
    print(sep)
    print()


# ===========================================================================
# Main execution
# ===========================================================================

def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Validate epicenter bounds
    epi = tuple(args.epicenter)
    if not (0 <= epi[0] < args.grid_size and 0 <= epi[1] < args.grid_size):
        print(
            f"[ERROR] Epicenter {epi} is outside the grid "
            f"(0–{args.grid_size-1}, 0–{args.grid_size-1}).",
            file=sys.stderr
        )
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 1. Build grid
    # -----------------------------------------------------------------------
    print("  [1/4] Initialising seismic grid …", end=" ", flush=True)
    grid = SeismicGrid(size=args.grid_size, seed=args.seed)
    print("done.")

    # -----------------------------------------------------------------------
    # 2. Run simulation
    # -----------------------------------------------------------------------
    print("  [2/4] Computing intensity field …", end=" ", flush=True)
    sim = SeismicSimulation(
        grid=grid,
        epicenter=epi,
        I0=args.I0,
        k=args.k,
        time_steps=args.time_steps,
    )
    print("done.")

    # -----------------------------------------------------------------------
    # 3. Compute damage
    # -----------------------------------------------------------------------
    print("  [3/4] Evaluating structural damage …", end=" ", flush=True)
    damage = DamageModel(grid, sim.intensity_full)
    print("done.")

    # -----------------------------------------------------------------------
    # 4. Console summary
    # -----------------------------------------------------------------------
    print_summary(args, grid, sim, damage)

    # -----------------------------------------------------------------------
    # 5. Static heatmaps
    # -----------------------------------------------------------------------
    print("  [4/4] Rendering visualisations …")
    fig_static  = viz.plot_static_heatmaps(grid, sim, damage)
    fig_summary = viz.plot_population_summary(grid, damage)

    # -----------------------------------------------------------------------
    # 6. Animation
    # -----------------------------------------------------------------------
    anim = None
    if not args.no_animation:
        print("        → Building wave animation …", end=" ", flush=True)
        anim = viz.build_animation(grid, sim)
        print("done.")

        if args.save_animation:
            print(f"        → Saving animation to '{args.save_animation}' …",
                  end=" ", flush=True)
            writer = (
                animation.FFMpegWriter(fps=config.ANIMATION_FPS)
                if args.save_animation.endswith(".mp4")
                else animation.PillowWriter(fps=config.ANIMATION_FPS)
            )
            anim.save(args.save_animation, writer=writer, dpi=120)
            print("done.")

    print("  All done. Close the plot windows to exit.\n")
    plt.show()


if __name__ == "__main__":
    main()
