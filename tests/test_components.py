"""Tests for the Component dataclass."""

import math

from noise.components import Component


def test_gain_linear_positive():
    comp = Component("amp", gain_dB=20.0, temperature_K=4.0)
    assert math.isclose(comp.gain_linear, 100.0, rel_tol=1e-9)


def test_gain_linear_negative():
    comp = Component("atten", gain_dB=-10.0, temperature_K=300.0)
    assert math.isclose(comp.gain_linear, 0.1, rel_tol=1e-9)


def test_gain_linear_zero():
    comp = Component("pass", gain_dB=0.0, temperature_K=50e-3)
    assert math.isclose(comp.gain_linear, 1.0, rel_tol=1e-9)


def test_passive_component():
    comp = Component("atten", gain_dB=-10.0, temperature_K=300.0)
    assert comp.is_passive is True


def test_active_component():
    comp = Component("amp", gain_dB=20.0, temperature_K=4.0, noise_temp_K=5.0)
    assert comp.is_passive is False


def test_passive_added_noise():
    """A -20dB attenuator at 300K: added noise = 300 × (1 - 0.01) = 297K."""
    comp = Component("atten", gain_dB=-20.0, temperature_K=300.0)
    assert math.isclose(comp.added_noise_temp, 297.0, rel_tol=1e-9)


def test_active_added_noise():
    """An amplifier with +20dB gain and 5K noise temp: added = 5 × 100 = 500K."""
    comp = Component("amp", gain_dB=20.0, temperature_K=4.0, noise_temp_K=5.0)
    assert math.isclose(comp.added_noise_temp, 500.0, rel_tol=1e-9)
