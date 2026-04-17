"""Component model for readout chain elements.

Each component in a readout chain is characterized by its gain (or attenuation)
and physical temperature. Passive components (attenuators, cables) have gain ≤ 1
and generate Johnson noise proportional to their physical temperature. Active
components (amplifiers) have gain > 1 and are characterized by an additional
noise temperature.

Noise convention (all quantities are equivalent noise temperatures):
- Passive (G ≤ 1): added noise at output = T_phys × (1 - G)
  This follows from the thermodynamic requirement that a lossy element at
  temperature T in thermal equilibrium emits noise to maintain T at its output.
- Active (G > 1): added noise at output = T_noise × G
  where T_noise is the amplifier's equivalent input noise temperature.
"""

from dataclasses import dataclass


@dataclass
class Component:
    """A single element in a readout chain.

    Parameters
    ----------
    name : str
        Human-readable label (e.g. "HEMT", "20dB atten").
    gain_dB : float
        Power gain in decibels. Negative for attenuators.
    temperature_K : float
        Physical temperature of the component in Kelvin.
    noise_temp_K : float, optional
        Equivalent input noise temperature in Kelvin. Only meaningful for
        active components (amplifiers). Defaults to 0.
    """

    name: str
    gain_dB: float
    temperature_K: float
    noise_temp_K: float = 0.0

    @property
    def gain_linear(self) -> float:
        """Power gain as a linear ratio (10^(gain_dB/10))."""
        return 10.0 ** (self.gain_dB / 10.0)

    @property
    def is_passive(self) -> bool:
        """True if the component has gain ≤ 1 (i.e. gain_dB ≤ 0)."""
        return self.gain_dB <= 0.0

    @property
    def added_noise_temp(self) -> float:
        """Noise temperature added at the output of this component.

        For passive components: T_phys × (1 - G), which is the thermal noise
        from the attenuator's internal resistance.

        For active components: noise_temp_K × G, which is the amplifier's
        input-referred noise amplified to the output.
        """
        g = self.gain_linear
        if self.is_passive:
            return self.temperature_K * (1.0 - g)
        else:
            return self.noise_temp_K * g
