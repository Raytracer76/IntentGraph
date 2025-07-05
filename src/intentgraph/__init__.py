"""IntentGraph - A best-in-class repository dependency analyzer."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .domain.models import AnalysisResult, FileInfo, Language, LanguageSummary

__all__ = [
    "AnalysisResult",
    "FileInfo",
    "Language",
    "LanguageSummary",
]
