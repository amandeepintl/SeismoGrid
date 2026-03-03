"""
config.py – SeismoGrid Simulation Parameters
=============================================
Central configuration store for all simulation constants and tunable parameters.
Modify these values to explore different seismic scenarios.

All physical relationships here are SIMPLIFIED and EDUCATIONAL.
This is NOT a real seismic hazard assessment tool.
"""

# ---------------------------------------------------------------------------
# Grid Configuration
# ---------------------------------------------------------------------------
GRID_SIZE = 100          # Number of cells along each axis (GRID_SIZE x GRID_SIZE)
RANDOM_SEED = 42         # Fixed seed for deterministic/reproducible runs; set None for random

# ---------------------------------------------------------------------------
# Epicenter Configuration
# ---------------------------------------------------------------------------
# Grid coordinates of the earthquake epicenter (row, col).
# Defaults to centre of the grid; override via CLI args in main.py.
EPICENTER = (50, 50)

# ---------------------------------------------------------------------------
# Seismic Intensity Parameters
# ---------------------------------------------------------------------------
# Initial intensity I0 at the epicenter (arbitrary units, conceptually proportional
# to seismic moment release).  Real-world peak ground motion depends on fault
# mechanism, depth, and crustal structure – none of which are modelled here.
INITIAL_INTENSITY = 10.0

# Attenuation constant k in the decay formula  I = I0 / (1 + k * d²).
# Larger k → intensity falls off more steeply with distance.
# This mimics geometric spreading in a homogeneous, isotropic elastic half-space.
# Real attenuation also includes anelastic damping (Q-factor) and scattering.
ATTENUATION_CONSTANT = 0.01

# ---------------------------------------------------------------------------
# Damage Model Parameters
# ---------------------------------------------------------------------------
# Structural resistance values are drawn from a smoothed uniform distribution
# [RESISTANCE_MIN, RESISTANCE_MAX].  A value of 1.0 means perfect resistance
# (no damage); 0.0 means no resistance (fully damaged at any intensity).
RESISTANCE_MIN = 0.2
RESISTANCE_MAX = 0.9

# Damage threshold below which a cell is considered "significantly damaged"
# (used only for counting damaged-area cells in the summary).
DAMAGE_THRESHOLD = 0.3

# ---------------------------------------------------------------------------
# Population Density Configuration
# ---------------------------------------------------------------------------
# Synthetic population per cell is generated as a spatially smooth field
# by blurring a random matrix with a Gaussian kernel.
# MAX_POPULATION controls the upper bound (persons per cell).
MAX_POPULATION = 5000

# ---------------------------------------------------------------------------
# Wave Propagation / Animation
# ---------------------------------------------------------------------------
# Number of discrete simulation time-steps.
# The seismic wave front expands by one cell radius per step.
TIME_STEPS = 60

# Frames-per-second for the Matplotlib animation.
ANIMATION_FPS = 15

# Whether to draw intensity contour rings overlaid on the heatmap.
SHOW_CONTOURS = True

# Intensity levels at which contour rings are drawn.
CONTOUR_LEVELS = [0.5, 1.0, 2.0, 4.0, 7.0]

# ---------------------------------------------------------------------------
# Colormaps (Matplotlib named colormaps)
# ---------------------------------------------------------------------------
CMAP_INTENSITY  = "hot"
CMAP_DAMAGE     = "RdYlGn_r"
CMAP_POPULATION = "YlOrRd"

# ---------------------------------------------------------------------------
# Advanced Extension Hooks (design stubs – not yet implemented)
# ---------------------------------------------------------------------------
# TERRAIN_MODIFIER_FILE = None       # Path to a .npy terrain amplification matrix
# MULTI_EPICENTERS     = []          # List of (row, col, I0) tuples for superposition
# AFTERSHOCK_ENABLED   = False       # Toggle aftershock generator
# ATTENUATION_MODEL    = "quadratic" # "quadratic" | "linear" | "exponential"
# GIS_INPUT_FILE       = None        # Path to GIS population raster (GeoTIFF etc.)
