"""Custom exceptions for IntentGraph."""


class IntentGraphError(Exception):
    """Base exception for IntentGraph."""


class AnalysisError(IntentGraphError):
    """Error during file analysis."""


class LanguageNotSupportedError(IntentGraphError):
    """Language is not supported."""


class InvalidRepositoryError(IntentGraphError):
    """Repository is invalid or not found."""


class CyclicDependencyError(IntentGraphError):
    """Cyclic dependency detected."""

    def __init__(self, cycles: list) -> None:
        self.cycles = cycles
        super().__init__(f"Cyclic dependencies detected: {len(cycles)} cycles")
