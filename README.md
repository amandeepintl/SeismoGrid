# 🌍 SeismoGrid

**SeismoGrid** is a research-oriented earthquake impact simulation tool that models seismic wave propagation across a population grid.  
It demonstrates how intensity decays over distance and estimates structural damage and affected regions using simplified physical principles.

> ⚠️ This is a conceptual simulation for educational and research purposes — not a real-world prediction system.

---

## 🚀 Overview

SeismoGrid simulates:

- 🌋 Earthquake epicenter generation  
- 🌊 Seismic wave propagation over time  
- 📉 Intensity decay with distance  
- 🏙️ Population distribution across a grid  
- 🏚️ Structural damage estimation  
- 👥 Affected population calculation  

The focus is analytical modeling and scientific reasoning.

---

## 🧠 How It Works

1. A 2D grid represents a geographic region.
2. Each grid cell contains:
   - Population density
   - Structural resistance factor
3. An earthquake epicenter is defined.
4. Wave intensity spreads outward from the epicenter.
5. Intensity decreases with distance.
6. Damage and impact are calculated per cell.
7. Results are visualized using matplotlib.

---

## 📐 Mathematical Model (Simplified)

### Intensity Decay
I = I₀ / (1 + k · d²)

Where:
- `I` = intensity at distance `d`
- `I₀` = initial intensity
- `d` = distance from epicenter
- `k` = attenuation constant

### Damage Estimation
Damage ∝ Intensity × (1 − Resistance)

These equations are simplified for educational modeling.

---

## ✨ Features

- 🗺️ 2D grid-based simulation  
- 📊 Distance-based intensity decay  
- 🏗️ Structural resistance modeling  
- 👥 Population impact estimation  
- 🎞️ Animated wave visualization  
- 📚 Research-style structure  

---

## 🛠️ Tech Stack

- 🐍 Python 3  
- 🔢 NumPy  
- 📈 Matplotlib  

---

## 📦 Installation

```bash
git clone https://github.com/amandeepintl/SeismoGrid.git
cd SeismoGrid
pip install -r requirements.txt
