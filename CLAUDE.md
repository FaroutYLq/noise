# Noise Calculator for Quantum Devices

## Project Overview
Calculate noise in quantum device readout chains. Primary feature: Johnson noise propagation through cascaded readout chains using the Friis formula.

## Project Structure
- `src/noise/` — main package (src layout)
- `tests/` — pytest tests
- `notebooks/` — Jupyter notebooks for visualization

## Conventions
- Python 3.10+, src layout, installable via `pip install -e .`
- Physics units: temperatures in Kelvin, gains in dB (converted to linear internally)
- Noise convention: all noise quantities expressed as equivalent noise temperatures
- Passive components (G ≤ 1): added noise temp at output = T_phys × (1 - G)
- Active components (G > 1): added noise temp at output = T_noise × G
- Testing: `pytest tests/`
- Dependencies: numpy, matplotlib, jupyter
