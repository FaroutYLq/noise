"""Readout chain model — an ordered sequence of components.

A readout chain represents the signal path from source to digitizer in a
quantum device measurement setup. The chain carries a signal characterized
by an equivalent noise temperature, which is modified by each component's
gain and noise contribution.
"""

from noise.components import Component


class ReadoutChain:
    """An ordered sequence of components with a defined input signal level.

    Parameters
    ----------
    signal_temp_K : float
        Equivalent noise temperature of the input signal in Kelvin.
        For a thermal source, this is its physical temperature.
    """

    def __init__(self, signal_temp_K: float = 300.0):
        self.signal_temp_K = signal_temp_K
        self.components: list[Component] = []

    def add(self, component: Component) -> "ReadoutChain":
        """Append a component to the chain. Returns self for fluent chaining."""
        self.components.append(component)
        return self
