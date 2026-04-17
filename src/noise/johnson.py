"""Johnson noise propagation through a readout chain.

This module implements the Friis noise analysis for a cascaded chain of
components. At each stage boundary, we track:

1. The signal power (as equivalent noise temperature)
2. Every individual noise contribution from each component, propagated
   through all subsequent stages
3. The total noise at each point

The Friis formula for total system noise temperature referred to the input:

    T_sys = T_1 + T_2/G_1 + T_3/(G_1·G_2) + ...

where T_i is the noise added by component i (referred to its own input)
and G_i is the gain of component i.

Propagation rules at stage i:
    signal *= G_i
    all existing noise contributions *= G_i
    new noise from component i:
        passive:  T_phys × (1 - G_i)   [thermal noise from loss]
        active:   T_noise × G_i        [amplifier noise]
"""

from dataclasses import dataclass, field

from noise.chain import ReadoutChain


@dataclass
class StageResult:
    """Noise analysis result at a single stage boundary.

    Each stage boundary is the output of one component. The noise_contributions
    dict maps component name to the noise temperature contributed by that
    component at this point in the chain (after propagation through all
    subsequent gains).

    Attributes
    ----------
    stage_index : int
        Index of the stage (0 = input, 1 = after first component, ...).
    signal_temp : float
        Signal equivalent noise temperature at this point [K].
    noise_contributions : dict[str, float]
        Noise temperature from each component at this point [K].
    total_noise : float
        Sum of all noise contributions at this point [K].
    """

    stage_index: int
    signal_temp: float
    noise_contributions: dict[str, float] = field(default_factory=dict)
    total_noise: float = 0.0


@dataclass
class ChainAnalysis:
    """Complete noise analysis of a readout chain.

    Attributes
    ----------
    stages : list[StageResult]
        Results at each stage boundary (input + after each component).
    friis_noise_temp : float
        Total system noise temperature referred to the input [K].
    back_referred : dict[str, float]
        Each component's noise contribution referred back to the input [K].
    """

    stages: list[StageResult] = field(default_factory=list)
    friis_noise_temp: float = 0.0
    back_referred: dict[str, float] = field(default_factory=dict)


def analyze_chain(chain: ReadoutChain) -> ChainAnalysis:
    """Perform Friis noise analysis on a readout chain.

    Walks the chain left-to-right, tracking the signal and every individual
    noise contribution at each stage boundary. Also computes the Friis
    system noise temperature and back-referred noise contributions.

    Parameters
    ----------
    chain : ReadoutChain
        The readout chain to analyze.

    Returns
    -------
    ChainAnalysis
        Complete analysis with per-stage results and system noise temperature.
    """
    components = chain.components
    n = len(components)

    # Track signal and noise contributions as we walk the chain
    signal = chain.signal_temp_K
    # noise_contribs[component_name] = current noise temp from that component
    noise_contribs: dict[str, float] = {}

    stages: list[StageResult] = []

    # Stage 0: the input
    stages.append(StageResult(
        stage_index=0,
        signal_temp=signal,
        noise_contributions=dict(noise_contribs),
        total_noise=sum(noise_contribs.values()),
    ))

    # Walk through each component
    for i, comp in enumerate(components):
        g = comp.gain_linear

        # Propagate signal
        signal *= g

        # Propagate all existing noise contributions
        for name in noise_contribs:
            noise_contribs[name] *= g

        # Add new noise from this component
        added = comp.added_noise_temp
        if comp.name in noise_contribs:
            noise_contribs[comp.name] += added
        else:
            noise_contribs[comp.name] = added

        total = sum(noise_contribs.values())
        stages.append(StageResult(
            stage_index=i + 1,
            signal_temp=signal,
            noise_contributions=dict(noise_contribs),
            total_noise=total,
        ))

    # Compute total chain gain for back-referral
    total_gain = 1.0
    for comp in components:
        total_gain *= comp.gain_linear

    # Back-refer: divide final noise contributions by total chain gain
    final_contribs = stages[-1].noise_contributions if stages else {}
    back_referred = {}
    if total_gain > 0:
        for name, noise in final_contribs.items():
            back_referred[name] = noise / total_gain

    friis_noise_temp = sum(back_referred.values())

    return ChainAnalysis(
        stages=stages,
        friis_noise_temp=friis_noise_temp,
        back_referred=back_referred,
    )
