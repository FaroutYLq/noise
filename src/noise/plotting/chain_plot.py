"""Figure 7.4-style grouped bar chart for chain noise analysis.

Produces a visualization showing signal and noise power levels (as equivalent
noise temperatures) at each stage boundary in a readout chain. Each stage
position shows:
- Black bar: signal level
- Colored bars: individual noise contributions from each component
- Gold bar: total noise

Optionally, faded bars show noise components back-referred to each stage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from noise.constants import K_B

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from noise.chain import ReadoutChain
    from noise.johnson import ChainAnalysis


# Distinct colors for noise sources (enough for large chains)
_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf", "#aec7e8", "#ffbb78",
    "#98df8a", "#ff9896", "#c5b0d5", "#c49c94",
    "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5",
    "#393b79", "#637939", "#8c6d31", "#843c39",
    "#7b4173", "#5254a3", "#6b6ecf", "#b5cf6b",
    "#e7969c", "#bd9e39", "#ad494a", "#a55194",
]


def plot_chain_analysis(
    chain: "ReadoutChain",
    analysis: "ChainAnalysis",
    *,
    show_back_referred: bool = True,
    bandwidth_Hz: float = 1.0,
    ax: "Axes | None" = None,
    figsize: tuple[float, float] = (14, 7),
) -> "Figure":
    """Plot a Figure 7.4-style grouped bar chart of chain noise analysis.

    Parameters
    ----------
    chain : ReadoutChain
        The readout chain (used for component labels/annotations).
    analysis : ChainAnalysis
        Result from ``analyze_chain()``.
    show_back_referred : bool
        If True, show faded bars for back-referred noise at each stage.
    bandwidth_Hz : float
        Measurement bandwidth [Hz] for the dBm secondary axis.
    ax : Axes, optional
        Matplotlib axes to plot on. If None, a new figure is created.
    figsize : tuple
        Figure size if creating a new figure.

    Returns
    -------
    Figure
        The matplotlib figure.
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.get_figure()

    stages = analysis.stages
    components = chain.components
    n_stages = len(stages)

    # Collect all noise source names in order of first appearance
    all_sources: list[str] = []
    for stage in stages:
        for name in stage.noise_contributions:
            if name not in all_sources:
                all_sources.append(name)

    # Assign colors
    source_colors = {}
    for i, name in enumerate(all_sources):
        source_colors[name] = _COLORS[i % len(_COLORS)]

    # Bar layout: at each stage we have signal + sources + total
    n_bars_per_stage = 1 + len(all_sources) + 1  # signal + sources + total
    bar_width = 0.8 / n_bars_per_stage
    stage_positions = np.arange(n_stages)

    # Track which labels have been added to the legend
    labeled: set[str] = set()

    # Plot bars for each stage
    for si, stage in enumerate(stages):
        x_base = si - 0.4  # left edge of group
        bar_idx = 0

        # Signal bar (black)
        val = max(stage.signal_temp, 1e-30)  # clamp for log scale
        ax.bar(x_base + bar_idx * bar_width, val, bar_width,
               color="black", label="Signal" if "Signal" not in labeled else None)
        labeled.add("Signal")
        bar_idx += 1

        # Noise source bars
        for name in all_sources:
            noise_val = stage.noise_contributions.get(name, 0.0)
            if noise_val > 0:
                ax.bar(x_base + bar_idx * bar_width, noise_val, bar_width,
                       color=source_colors[name],
                       label=name if name not in labeled else None)
                labeled.add(name)
            bar_idx += 1

        # Total noise bar (gold)
        if stage.total_noise > 0:
            ax.bar(x_base + bar_idx * bar_width, stage.total_noise, bar_width,
                   color="gold", edgecolor="goldenrod",
                   label="Total noise" if "Total noise" not in labeled else None)
            labeled.add("Total noise")

    # Back-referred faded bars
    if show_back_referred and analysis.back_referred:
        total_gain_to_stage = [1.0]
        g = 1.0
        for comp in components:
            g *= comp.gain_linear
            total_gain_to_stage.append(g)

        for si, stage in enumerate(stages):
            x_base = si - 0.4
            bar_idx = 1  # skip signal bar
            gain_here = total_gain_to_stage[si]

            for name in all_sources:
                back_val = analysis.back_referred.get(name, 0.0)
                referred_val = back_val * gain_here
                if referred_val > 0:
                    ax.bar(x_base + bar_idx * bar_width, referred_val, bar_width,
                           color=source_colors[name], alpha=0.2,
                           edgecolor=source_colors[name], linestyle="--",
                           linewidth=0.5)
                bar_idx += 1

    ax.set_yscale("log")
    ax.set_ylabel("Equivalent noise temperature [K]")
    ax.set_title("Signal and noise propagation through readout chain")

    # X-axis labels
    xlabels = ["Input"]
    for comp in components:
        xlabels.append(comp.name)
    ax.set_xticks(stage_positions)
    ax.set_xticklabels(xlabels, rotation=30, ha="right")
    ax.tick_params(axis="x", which="both", length=0)

    # Secondary y-axis: dBm (linear scale, since dBm is already logarithmic)
    ax_right = ax.twinx()
    y_lo, y_hi = ax.get_ylim()
    dbm_lo = 10.0 * np.log10(K_B * y_lo * bandwidth_Hz / 1e-3)
    dbm_hi = 10.0 * np.log10(K_B * y_hi * bandwidth_Hz / 1e-3)
    ax_right.set_ylim(dbm_lo, dbm_hi)
    ax_right.set_ylabel(f"Noise power [dBm] (BW = {bandwidth_Hz:.0f} Hz)")

    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    return fig
