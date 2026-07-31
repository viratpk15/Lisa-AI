"""
Jarvis AIOS — Base Live Data Validator
---------------------------------------

Abstract base class for domain-specific live data validators.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseLiveValidator(ABC):
    """Abstract base class for domain-specific live data validators."""

    @abstractmethod
    def validate(self, payload: dict, source: str) -> Tuple[bool, float, str]:
        """
        Validates domain payload & source.

        Args:
            payload: Structured dictionary containing domain parameters.
            source: Source string or URL.

        Returns:
            Tuple of (is_valid: bool, confidence_score: float, reason: str).
        """
        pass
