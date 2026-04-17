# noise
Noise calculator for quantum device readout chains.

## Installation

```bash
git clone https://github.com/FaroutYLq/noise.git
cd noise
pip install -e ".[dev]"
```

This installs the package in editable mode with development dependencies (pytest, jupyter).

## Quick start

```python
from noise import Component, ReadoutChain, analyze_chain
from noise.plotting import plot_chain_analysis

chain = (
    ReadoutChain(signal_temp_K=300.0)
    .add(Component("20dB atten",  gain_dB=-20.0, temperature_K=4.0))
    .add(Component("HEMT",        gain_dB=40.0,  temperature_K=4.0, noise_temp_K=5.0))
)

analysis = analyze_chain(chain)
print(f"System noise temperature: {analysis.friis_noise_temp:.1f} K")
plot_chain_analysis(chain, analysis)
```

See `notebooks/johnson_noise.ipynb` for a full walkthrough with the Figure 7.4 example chain.

## Tests

```bash
pytest tests/
```
