from typing import Any


class ComparisonResult:
    def __init__(self, passed: bool, message: str, warning: bool = False):
        self.passed = passed
        self.message = message
        self.warning = warning


class ExactComparator:
    """Level 1 - Exact"""

    @staticmethod
    def compare(expected: Any, actual: Any, field_path: str = "") -> ComparisonResult:
        if expected != actual:
            return ComparisonResult(
                False,
                f"Exact match failed at {field_path}: expected '{expected}', got '{actual}'",
            )
        return ComparisonResult(True, f"Exact match passed at {field_path}")


class NumericComparator:
    """Level 2 - Numeric with tolerance"""

    @staticmethod
    def compare(
        expected: float,
        actual: float,
        tolerance: float,
        field_path: str = "",
        is_percentage: bool = False,
    ) -> ComparisonResult:
        if is_percentage:
            diff = abs(expected - actual)
            # if expected is 0, just use diff directly. If we want relative % error: (abs(e-a)/e)*100
            # Let's interpret tolerance as an absolute difference (e.g. ±0.02)
            if diff > tolerance:
                return ComparisonResult(
                    False,
                    f"Numeric drift exceeded at {field_path}: expected {expected}, got {actual} (diff {diff} > {tolerance})",
                )
        else:
            diff = abs(expected - actual)
            if diff > tolerance:
                return ComparisonResult(
                    False,
                    f"Numeric drift exceeded at {field_path}: expected {expected}, got {actual} (diff {diff} > {tolerance})",
                )
        return ComparisonResult(True, f"Numeric check passed at {field_path}")


class StructuralComparator:
    """Level 3 - Structural (compare structure instead of wording)"""

    @staticmethod
    def compare(expected: Any, actual: Any, field_path: str = "") -> ComparisonResult:
        if isinstance(expected, dict) and isinstance(actual, dict):
            expected_keys = set(expected.keys())
            actual_keys = set(actual.keys())

            missing = expected_keys - actual_keys
            extra = actual_keys - expected_keys

            if missing or extra:
                return ComparisonResult(
                    False,
                    f"Structural drift at {field_path}: missing keys {missing}, extra keys {extra}",
                )

            # Recurse for nested dictionaries
            for k in expected_keys:
                res = StructuralComparator.compare(
                    expected[k], actual[k], f"{field_path}.{k}"
                )
                if not res.passed:
                    return res

            return ComparisonResult(True, f"Structural check passed at {field_path}")

        elif isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                return ComparisonResult(
                    False,
                    f"Structural drift at {field_path}: expected {len(expected)} items, got {len(actual)}",
                )
            # Basic list structural comparison could just verify length and types
            return ComparisonResult(
                True, f"Structural check passed at {field_path} (list sizes match)"
            )

        else:
            # For scalar values in structural check, we don't care about the exact text, just that they exist
            # So if both are present, it passes.
            return ComparisonResult(True, f"Structural check passed at {field_path}")


class SemanticComparator:
    """Level 4 - Semantic (stub for future)"""

    @staticmethod
    def compare(expected: str, actual: str, field_path: str = "") -> ComparisonResult:
        if expected != actual:
            return ComparisonResult(
                True,  # Never blocks
                f"Semantic difference detected at {field_path} (Stub - Warning only)",
                warning=True,
            )
        return ComparisonResult(True, f"Semantic check passed at {field_path}")
