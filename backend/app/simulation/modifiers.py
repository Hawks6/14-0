from typing import Protocol
import numpy as np
from app.simulation.models import MatchState

class SimulationModifier(Protocol):
    def apply(self, state: MatchState, probs: np.ndarray) -> np.ndarray:
        """
        Applies context-specific changes to the outcome probability vector.
        """
        ...
