from abc import ABC, abstractmethod
from typing import Dict, Any


class Effector(ABC):
    """Base interface for effectors such as email, calendar, slack, etc."""

    @abstractmethod
    def deliver(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action and return result metadata."""
        raise NotImplementedError
