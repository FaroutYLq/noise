"""Physical constants and unit conversions for noise calculations.

Noise power and equivalent noise temperature are related by:

    P = k_B · T · Δf

where Δf is the measurement bandwidth. Converting to dBm:

    P_dBm = 10 · log10(k_B · T · Δf / 1 mW)
"""

import math

K_B = 1.380649e-23  # Boltzmann constant [J/K]


def temp_to_dBm(temperature_K: float, bandwidth_Hz: float) -> float:
    """Convert equivalent noise temperature to power in dBm.

    Parameters
    ----------
    temperature_K : float
        Equivalent noise temperature [K].
    bandwidth_Hz : float
        Measurement bandwidth [Hz].

    Returns
    -------
    float
        Noise power [dBm].
    """
    power_W = K_B * temperature_K * bandwidth_Hz
    return 10.0 * math.log10(power_W / 1e-3)


def dBm_to_temp(power_dBm: float, bandwidth_Hz: float) -> float:
    """Convert power in dBm to equivalent noise temperature.

    Parameters
    ----------
    power_dBm : float
        Noise power [dBm].
    bandwidth_Hz : float
        Measurement bandwidth [Hz].

    Returns
    -------
    float
        Equivalent noise temperature [K].
    """
    power_W = 1e-3 * 10.0 ** (power_dBm / 10.0)
    return power_W / (K_B * bandwidth_Hz)
