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


T_0 = 290.0  # IEEE standard reference temperature [K]


def noise_figure_to_temp(nf_dB: float) -> float:
    """Convert noise figure in dB to equivalent noise temperature.

    Uses the IEEE standard reference temperature T_0 = 290 K:

        T_n = T_0 × (10^(NF/10) - 1)

    Parameters
    ----------
    nf_dB : float
        Noise figure [dB].

    Returns
    -------
    float
        Equivalent noise temperature [K].
    """
    return T_0 * (10.0 ** (nf_dB / 10.0) - 1.0)


def temp_to_noise_figure(noise_temp_K: float) -> float:
    """Convert equivalent noise temperature to noise figure in dB.

    Inverse of ``noise_figure_to_temp``:

        NF = 10 × log10(1 + T_n / T_0)

    Parameters
    ----------
    noise_temp_K : float
        Equivalent noise temperature [K].

    Returns
    -------
    float
        Noise figure [dB].
    """
    return 10.0 * math.log10(1.0 + noise_temp_K / T_0)
