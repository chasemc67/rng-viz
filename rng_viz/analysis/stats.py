"""Statistical analysis for random bitstreams."""

import math
from collections import deque
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np
from scipy import stats


class AnomalyResult(NamedTuple):
    """Result of anomaly detection."""

    position: int
    z_score: float
    p_value: float
    significance_level: str
    test_type: str


@dataclass
class StatisticalWindow:
    """Moving window for statistical analysis."""

    window_size: int
    data: deque = None

    def __post_init__(self) -> None:
        if self.data is None:
            self.data = deque(maxlen=self.window_size)

    def add_byte(self, byte_val: int) -> None:
        """Add a byte to the window."""
        self.data.append(byte_val)

    def is_full(self) -> bool:
        """Check if window is full."""
        return len(self.data) == self.window_size

    def get_bits(self) -> list[int]:
        """Get all bits from the current window."""
        bits = []
        for byte_val in self.data:
            for i in range(8):
                bits.append((byte_val >> i) & 1)
        return bits


class RandomnessAnalyzer:
    """Analyzer for detecting statistical anomalies in random bitstreams."""

    def __init__(self, window_size: int = 1000, sensitivity: float = 0.01):
        """Initialize the analyzer.

        Args:
            window_size: Size of moving window in bytes
            sensitivity: P-value threshold for significance (default 0.01 = 99% confidence)
        """
        self.window_size = window_size
        self.sensitivity = sensitivity
        self.window = StatisticalWindow(window_size=window_size)
        self.position = 0
        self.anomalies: list[AnomalyResult] = []

        # Significance levels
        self.significance_levels = {
            0.001: "***",  # 99.9% confidence
            0.01: "**",  # 99% confidence
            0.05: "*",  # 95% confidence
            1.0: "",  # Not significant
        }

    def add_byte(self, byte_val: int) -> list[AnomalyResult]:
        """Add a byte and analyze for anomalies.

        Args:
            byte_val: Byte value (0-255)

        Returns:
            List of detected anomalies in this position
        """
        self.window.add_byte(byte_val)
        self.position += 1

        anomalies = []

        if self.window.is_full():
            # Run multiple statistical tests
            anomalies.extend(self._test_frequency())
            anomalies.extend(self._test_runs())
            anomalies.extend(self._test_chi_square())

        return anomalies

    def _test_frequency(self) -> list[AnomalyResult]:
        """Test for frequency deviations (bias toward 0s or 1s)."""
        bits = self.window.get_bits()
        n_bits = len(bits)
        n_ones = sum(bits)
        n_zeros = n_bits - n_ones

        # Expected is 50/50 split
        expected_ones = n_bits / 2

        # Z-test for proportion
        p_hat = n_ones / n_bits
        expected_p = 0.5

        # Standard error for proportion
        se = math.sqrt(expected_p * (1 - expected_p) / n_bits)
        z_score = (p_hat - expected_p) / se

        # Two-tailed test
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

        anomalies = []
        if p_value < self.sensitivity:
            sig_level = self._get_significance_level(p_value)
            anomalies.append(
                AnomalyResult(
                    position=self.position,
                    z_score=z_score,
                    p_value=p_value,
                    significance_level=sig_level,
                    test_type="frequency",
                )
            )

        return anomalies

    def _test_runs(self) -> list[AnomalyResult]:
        """Test for runs (consecutive sequences of same bit)."""
        bits = self.window.get_bits()
        if len(bits) < 2:
            return []

        # Count runs
        runs = 1
        for i in range(1, len(bits)):
            if bits[i] != bits[i - 1]:
                runs += 1

        n = len(bits)
        n_ones = sum(bits)
        n_zeros = n - n_ones

        if n_ones == 0 or n_zeros == 0:
            return []  # Can't compute runs test

        # Expected number of runs
        expected_runs = (2 * n_ones * n_zeros) / n + 1

        # Variance of runs
        variance = (2 * n_ones * n_zeros * (2 * n_ones * n_zeros - n)) / (
            n * n * (n - 1)
        )

        if variance <= 0:
            return []

        # Z-score for runs test
        z_score = (runs - expected_runs) / math.sqrt(variance)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

        anomalies = []
        if p_value < self.sensitivity:
            sig_level = self._get_significance_level(p_value)
            anomalies.append(
                AnomalyResult(
                    position=self.position,
                    z_score=z_score,
                    p_value=p_value,
                    significance_level=sig_level,
                    test_type="runs",
                )
            )

        return anomalies

    def _test_chi_square(self) -> list[AnomalyResult]:
        """Chi-square test for uniformity of byte values."""
        byte_values = list(self.window.data)
        if len(byte_values) < 50:  # Need sufficient sample size
            return []

        # Count frequency of each byte value
        observed_freq = np.bincount(byte_values, minlength=256)
        expected_freq = len(byte_values) / 256

        # Chi-square test
        chi2_stat = np.sum((observed_freq - expected_freq) ** 2 / expected_freq)
        dof = 255  # degrees of freedom
        p_value = 1 - stats.chi2.cdf(chi2_stat, dof)

        # Convert to z-score approximation for consistency
        z_score = (chi2_stat - dof) / math.sqrt(2 * dof)

        anomalies = []
        if p_value < self.sensitivity:
            sig_level = self._get_significance_level(p_value)
            anomalies.append(
                AnomalyResult(
                    position=self.position,
                    z_score=z_score,
                    p_value=p_value,
                    significance_level=sig_level,
                    test_type="chi_square",
                )
            )

        return anomalies

    def _get_significance_level(self, p_value: float) -> str:
        """Get significance level string based on p-value."""
        for threshold, symbol in self.significance_levels.items():
            if p_value < threshold:
                return symbol
        return ""

    def get_summary_stats(self) -> dict:
        """Get summary statistics for current window."""
        if not self.window.is_full():
            return {}

        bits = self.window.get_bits()
        byte_values = list(self.window.data)

        return {
            "total_bits": len(bits),
            "ones_count": sum(bits),
            "zeros_count": len(bits) - sum(bits),
            "ones_ratio": sum(bits) / len(bits),
            "byte_mean": np.mean(byte_values),
            "byte_std": np.std(byte_values),
            "total_anomalies": len(self.anomalies),
            "current_position": self.position,
        }
