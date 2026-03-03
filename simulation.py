"""
simulation.py – Seismic Propagation Engine
===========================================
Computes the seismic intensity field and manages wave-front expansion.

Physical model (educational / conceptual only)
-----------------------------------------------
We use a simplified scalar intensity decay:

    I(d) = I0 / (1 + k * d²)

where
  I0  = initial intensity at the epicenter (epicentral intensity)
  k   = dimensionless attenuation constant
  d   = Euclidean distance from epicenter in grid-cell units

Rationale for the formula
--------------------------
In classical body-wave theory, peak ground motion amplitude decays roughly as
1/r (geometric spreading in 3-D) and energy as 1/r².  The denominator
(1 + k*d²) approximates this quadratic decay while keeping intensity finite
at d=0 (avoiding a singularity).  The constant k lumps together geometric
spreading and intrinsic attenuation.

WHY THIS IS NOT A REAL SEISMIC SOLVER
---------------------------------------
1. Real shaking depends on focal depth, fault mechanism, radiation pattern,
   and crustal velocity structure – all absent here.
2. We assume perfect isotropy (equal energy in every direction).
3. Site amplification (soil type, topography) is ignored.
4. Frequency-dependent attenuation and dispersion are not modelled.
5. The model is 2-D; seismic waves propagate in 3-D.
6. No body-wave vs. surface-wave distinction.

Wave propagation animation model
----------------------------------
For the animation we expand a circular "wave front" outward at one grid-cell
per time step.  At each step we compute intensity ONLY within the currently
reached radius.  This is a didactic device – it does not represent actual
wave speed (which varies with crustal structure) but clearly shows how energy
spreads outward and decays.
"""

import numpy as np
import config
from grid import SeismicGrid


class SeismicSimulation:
    """
    Manages the seismic intensity computation and wave-front expansion.

    Parameters
    ----------
    grid      : SeismicGrid instance
    epicenter : (row, col) epicenter coordinates
    I0        : Initial intensity at the epicenter
    k         : Attenuation constant
    time_steps: Number of animation frames (wave-front expansion steps)
    """

    def __init__(
        self,
        grid: SeismicGrid,
        epicenter: tuple[int, int] = config.EPICENTER,
        I0: float = config.INITIAL_INTENSITY,
        k: float = config.ATTENUATION_CONSTANT,
        time_steps: int = config.TIME_STEPS,
    ):
        self.grid = grid
        self.epicenter = epicenter
        self.I0 = I0
        self.k = k
        self.time_steps = time_steps

        # Pre-compute the full distance matrix once (vectorised).
        self.distance: np.ndarray = grid.distance_from(epicenter)

        # Maximum possible wave-front radius (diagonal of the grid).
        self.max_radius: float = float(np.sqrt(2) * grid.size)

        # Radius increment per time step so the wave reaches the grid corner
        # at the final frame.
        self.radius_step: float = self.max_radius / max(time_steps, 1)

        # Full steady-state intensity field (computed once).
        self.intensity_full: np.ndarray = self._compute_intensity(self.distance)

        # Working intensity field updated each animation frame.
        self.intensity_current: np.ndarray = np.zeros_like(self.intensity_full)

    # ------------------------------------------------------------------
    # Core physics
    # ------------------------------------------------------------------
    def _compute_intensity(self, distance: np.ndarray) -> np.ndarray:
        """
        Vectorised intensity decay formula.

        I = I0 / (1 + k * d²)

        Parameters
        ----------
        distance : ndarray of distances (cell units)

        Returns
        -------
        ndarray of intensity values (same shape as distance)
        """
        return self.I0 / (1.0 + self.k * distance ** 2)

    def intensity_at_radius(self, radius: float) -> np.ndarray:
        """
        Return the intensity field masked to cells within *radius* cell-units
        of the epicenter.  Cells outside the wave front have intensity 0.

        This drives the frame-by-frame animation: each frame reveals more of
        the grid as the wave front expands.
        """
        mask = self.distance <= radius
        field = np.where(mask, self.intensity_full, 0.0)
        return field

    # ------------------------------------------------------------------
    # Simulation runner
    # ------------------------------------------------------------------
    def compute_frame(self, step: int) -> np.ndarray:
        """
        Compute and cache the intensity field for animation frame *step*.

        Parameters
        ----------
        step : 0-indexed time step

        Returns
        -------
        intensity ndarray for this frame
        """
        radius = (step + 1) * self.radius_step
        self.intensity_current = self.intensity_at_radius(radius)
        return self.intensity_current

    def run_full(self) -> np.ndarray:
        """
        Return the time-averaged (steady-state) full intensity field,
        i.e. intensity for every cell in the grid regardless of wave-front.
        """
        return self.intensity_full

    # ------------------------------------------------------------------
    # Summary statistics
    # ------------------------------------------------------------------
    def peak_intensity(self) -> float:
        return float(self.intensity_full.max())

    def mean_intensity(self) -> float:
        return float(self.intensity_full.mean())

    def radius_for_intensity(self, threshold: float) -> float:
        """
        Compute the radius (in grid cells) at which intensity falls below
        *threshold*, by inverting the decay formula analytically.

        r = sqrt((I0/threshold - 1) / k)
        """
        if threshold <= 0 or threshold >= self.I0:
            return 0.0
        return float(np.sqrt((self.I0 / threshold - 1.0) / self.k))
