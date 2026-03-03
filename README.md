# 🌍 SeismoGrid

> A research-oriented earthquake impact simulation tool modeling seismic
> wave propagation across a population grid.

SeismoGrid demonstrates how earthquake intensity decays over distance
and estimates structural damage and affected regions using simplified
physical principles.

⚠️ This is a conceptual simulation for educational and analytical
purposes --- not a real-world prediction system.

------------------------------------------------------------------------

## 🚀 Overview

SeismoGrid simulates:

-   🌋 Earthquake epicenter generation\
-   🌊 Seismic wave propagation\
-   📉 Distance-based intensity decay\
-   🏙️ Population distribution on a grid\
-   🏚️ Structural damage estimation\
-   👥 Affected population calculation

The focus is scientific modeling and structured reasoning.

------------------------------------------------------------------------

## 🧠 How It Works

1.  A 2D grid represents a geographic region.
2.  Each cell stores:
    -   Population density\
    -   Structural resistance factor\
3.  An epicenter is defined.
4.  Seismic waves expand outward.
5.  Intensity decreases with distance.
6.  Damage and population impact are computed per cell.
7.  Results are visualized using matplotlib animations.

------------------------------------------------------------------------

## 📐 Mathematical Model (Simplified)

### Intensity Decay

    I = I₀ / (1 + k · d²)

Where:

-   `I` = intensity at distance `d`\
-   `I₀` = initial intensity\
-   `d` = distance from epicenter\
-   `k` = attenuation constant

### Damage Estimation

    Damage ∝ Intensity × (1 − Resistance)

These equations are simplified to demonstrate modeling concepts.

------------------------------------------------------------------------

## ✨ Features

-   🗺️ Grid-based simulation engine\
-   📊 Intensity attenuation modeling\
-   🏗️ Structural resistance calculation\
-   👥 Population impact estimation\
-   🎞️ Animated visualization\
-   📚 Research-style structure

------------------------------------------------------------------------

## 🛠️ Tech Stack

-   🐍 Python 3\
-   🔢 NumPy\
-   📈 Matplotlib

------------------------------------------------------------------------

## 📦 Installation

``` bash
git clone https://github.com/amandeepintl/SeismoGrid.git
cd SeismoGrid
pip install -r requirements.txt
```

------------------------------------------------------------------------

## ▶️ Run the Simulation

``` bash
python main.py
```

------------------------------------------------------------------------

## 🎓 Educational Value

SeismoGrid demonstrates:

-   Applied mathematics\
-   Simulation modeling\
-   Data visualization\
-   Analytical reasoning\
-   Scientific assumptions and limitations

------------------------------------------------------------------------

## ⚠️ Limitations

-   Not a real predictive system\
-   Uses simplified physical models\
-   Does not include geological variability\
-   Not suitable for real disaster forecasting

------------------------------------------------------------------------

## 🔮 Future Improvements

-   🌄 Terrain-based intensity adjustments\
-   🗾 Real geographic data integration\
-   🌐 Multi-epicenter modeling\
-   🔁 Aftershock simulation\
-   📊 Advanced attenuation formulas

------------------------------------------------------------------------

## 📄 License

MIT License
