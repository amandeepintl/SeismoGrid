"""
damage.py – Structural Damage Computation
==========================================
Translates seismic intensity into damage and affected-population estimates.

Damage model (conceptual)
--------------------------
    damage(cell) = intensity(cell) × (1 - resistance(cell))

Interpretation:
  - A cell with resistance=1.0 sustains zero damage regardless of intensity.
  - A cell with resistance=0.0 sustains damage equal to the raw intensity.
  - Damage is clipped to [0, 1] after normalisation (see below).

SIMPLIFICATIONS AND LIMITATIONS
---------------------------------
1. We use a LINEAR relationship between intensity and damage.  Real fragility
   curves (HAZUS, OpenQuake) are typically non-linear (lognormal CDF) and
   depend on structural typology and spectral acceleration – not implemented.
2. A single 'resistance' scalar collapses all building types in a cell.
3. Soil amplification is not accounted for.
4. Damage state categories (None / Slight / Moderate / Extensive / Complete)
   from standard loss models are reduced here to a single continuous score.
5. Secondary hazards (liquefaction, landslide, fire-following-earthquake) are
   not modelled.

Affected population model
--------------------------
    affected(cell) = population_density(cell) × normalised_damage(cell)

'affected' is an approximation of the fraction of the cell's inhabitants
who experience significant shaking-related impact.  It is NOT a casualty
estimate and should NOT be used as one.
"""

import numpy as np
import config
from grid import SeismicGrid


class DamageModel:
    """
    Computes and stores damage metrics for a given intensity field.

    Parameters
    ----------
    grid      : SeismicGrid – provides population and resistance fields
    intensity : ndarray (size × size) – intensity field from the simulation
    """

    def __init__(self, grid: SeismicGrid, intensity: np.ndarray):
        self.grid = grid
        self.intensity = intensity

        # Raw damage (un-normalised): element-wise product of intensity and
        # vulnerability (i.e., 1 – resistance).
        raw_damage = intensity * (1.0 - grid.resistance)

        # Normalise damage to [0, 1] relative to the theoretical maximum
        # (I0 × max_vulnerability = I0 × (1 - RESISTANCE_MIN)).
        max_possible = config.INITIAL_INTENSITY * (1.0 - config.RESISTANCE_MIN)
        if max_possible > 0:
            self.damage: np.ndarray = np.clip(raw_damage / max_possible, 0.0, 1.0)
        else:
            self.damage = np.zeros_like(raw_damage)

        # Affected population: population × normalised damage
        self.affected_population: np.ndarray = (
            grid.population_density * self.damage
        )

    # ------------------------------------------------------------------
    # Aggregate statistics
    # ------------------------------------------------------------------
    def total_affected(self) -> float:
        """Total number of affected persons across the entire grid."""
        return float(self.affected_population.sum())

    def damaged_cells(self) -> int:
        """Number of cells where normalised damage exceeds DAMAGE_THRESHOLD."""
        return int(np.sum(self.damage > config.DAMAGE_THRESHOLD))

    def damaged_area_fraction(self) -> float:
        """Fraction of grid area classified as significantly damaged."""
        total_cells = self.grid.size ** 2
        return self.damaged_cells() / total_cells

    def peak_damage(self) -> float:
        """Maximum normalised damage score across all cells."""
        return float(self.damage.max())

    def mean_damage(self) -> float:
        """Mean normalised damage score across all cells."""
        return float(self.damage.mean())

    # ------------------------------------------------------------------
    # Convenience – damage for a partial wave-front field
    # ------------------------------------------------------------------
    @classmethod
    def from_frame(cls, grid: SeismicGrid, intensity_frame: np.ndarray) -> "DamageModel":
        """
        Factory method to create a DamageModel for an animation frame's
        partial intensity field (masked to the current wave-front radius).
        """
        return cls(grid, intensity_frame)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    def summary(self) -> str:
        return (
            f"Peak damage score  : {self.peak_damage():.4f}\n"
            f"Mean damage score  : {self.mean_damage():.4f}\n"
            f"Damaged cells      : {self.damaged_cells()} "
            f"({self.damaged_area_fraction() * 100:.1f}% of grid)\n"
            f"Total affected pop : {self.total_affected():,.0f} persons"
        )
