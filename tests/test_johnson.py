"""Tests for Johnson noise propagation (Friis analysis)."""

import math

from noise.components import Component
from noise.chain import ReadoutChain
from noise.johnson import analyze_chain


def test_single_attenuator():
    """A single -20dB attenuator at 300K.

    G = 0.01
    Signal: 300 × 0.01 = 3K
    Added noise: 300 × (1 - 0.01) = 297K
    Total noise at output: 297K
    Back-referred noise: 297 / 0.01 = 29700K
    """
    chain = ReadoutChain(signal_temp_K=300.0)
    chain.add(Component("atten", gain_dB=-20.0, temperature_K=300.0))

    result = analyze_chain(chain)

    assert len(result.stages) == 2  # input + 1 component

    # After attenuator
    out = result.stages[1]
    assert math.isclose(out.signal_temp, 3.0, rel_tol=1e-9)
    assert math.isclose(out.noise_contributions["atten"], 297.0, rel_tol=1e-9)
    assert math.isclose(out.total_noise, 297.0, rel_tol=1e-9)


def test_single_amplifier():
    """A single +20dB amplifier with 5K noise temperature.

    G = 100
    Signal: 300 × 100 = 30000K
    Added noise: 5 × 100 = 500K
    Friis noise temp: 5K (just the amplifier noise referred to input)
    """
    chain = ReadoutChain(signal_temp_K=300.0)
    chain.add(Component("amp", gain_dB=20.0, temperature_K=4.0, noise_temp_K=5.0))

    result = analyze_chain(chain)

    out = result.stages[1]
    assert math.isclose(out.signal_temp, 30000.0, rel_tol=1e-9)
    assert math.isclose(out.noise_contributions["amp"], 500.0, rel_tol=1e-9)
    assert math.isclose(result.friis_noise_temp, 5.0, rel_tol=1e-9)


def test_attenuator_then_amplifier():
    """Friis formula for attenuator + amplifier.

    -20dB atten at 300K, then +20dB amp with T_n=5K.

    Friis: T_sys = T_atten + T_amp / G_atten
                 = (1-G)/G × T_phys + T_n / G
    For G_atten = 0.01:
        T_atten referred to input = 297/0.01 = 29700K
        T_amp referred to input = 5/0.01 = 500K (then ×G_amp/G_amp cancels)
    Actually: back-referred = final_noise / total_gain
        atten noise at output: 297 × 100 = 29700
        amp noise at output: 500
        total gain: 0.01 × 100 = 1
        back-referred atten: 29700
        back-referred amp: 500
        friis = 30200
    """
    chain = ReadoutChain(signal_temp_K=300.0)
    chain.add(Component("atten", gain_dB=-20.0, temperature_K=300.0))
    chain.add(Component("amp", gain_dB=20.0, temperature_K=4.0, noise_temp_K=5.0))

    result = analyze_chain(chain)

    # After both components
    out = result.stages[2]
    assert math.isclose(out.signal_temp, 300.0, rel_tol=1e-6)  # 300 × 0.01 × 100
    assert math.isclose(out.noise_contributions["atten"], 29700.0, rel_tol=1e-6)
    assert math.isclose(out.noise_contributions["amp"], 500.0, rel_tol=1e-6)

    # Friis system noise temp
    assert math.isclose(result.friis_noise_temp, 30200.0, rel_tol=1e-6)


def test_figure_74_chain():
    """The full Figure 7.4 chain — smoke test for consistency.

    input(300K) → atten(-20dB,4K) → atten(-10dB,1K) → atten(-10dB,50mK)
    → KID(0dB,50mK) → HEMT(+40dB,4K) → warm_amp(+25dB,300K)
    """
    chain = ReadoutChain(signal_temp_K=300.0)
    chain.add(Component("20dB atten", gain_dB=-20.0, temperature_K=4.0))
    chain.add(Component("10dB atten (1K)", gain_dB=-10.0, temperature_K=1.0))
    chain.add(Component("10dB atten (50mK)", gain_dB=-10.0, temperature_K=50e-3))
    chain.add(Component("KID", gain_dB=0.0, temperature_K=50e-3))
    chain.add(Component("HEMT", gain_dB=40.0, temperature_K=4.0, noise_temp_K=5.0))
    chain.add(Component("Warm amp", gain_dB=25.0, temperature_K=300.0, noise_temp_K=50.0))

    result = analyze_chain(chain)

    # Basic consistency checks
    assert len(result.stages) == 7  # input + 6 components

    # Signal should be attenuated then amplified
    # Total gain: -20 -10 -10 +0 +40 +25 = +25 dB
    total_gain_dB = -20 + -10 + -10 + 0 + 40 + 25
    expected_signal = 300.0 * 10 ** (total_gain_dB / 10)
    assert math.isclose(result.stages[-1].signal_temp, expected_signal, rel_tol=1e-6)

    # Friis noise temp should be dominated by the first attenuator (lossy at 4K)
    # and HEMT (first amplifier after losses)
    assert result.friis_noise_temp > 0

    # Back-referred contributions should sum to friis_noise_temp
    assert math.isclose(
        sum(result.back_referred.values()),
        result.friis_noise_temp,
        rel_tol=1e-9,
    )


def test_fluent_chaining():
    """ReadoutChain.add() returns self for fluent API."""
    chain = (
        ReadoutChain(signal_temp_K=300.0)
        .add(Component("a", gain_dB=-10.0, temperature_K=300.0))
        .add(Component("b", gain_dB=20.0, temperature_K=4.0, noise_temp_K=5.0))
    )
    assert len(chain.components) == 2
