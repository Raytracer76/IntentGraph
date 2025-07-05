"""Language parsers for dependency extraction."""

from typing import Optional

from ...domain.models import Language
from .base import LanguageParser
from .go_parser import GoParser
from .javascript_parser import JavaScriptParser
from .python_parser import PythonParser
from .typescript_parser import TypeScriptParser


class _ParserRegistry:
    def __init__(self):
        self._parsers = {
            Language.PYTHON: PythonParser(),
            Language.JAVASCRIPT: JavaScriptParser(),
            Language.TYPESCRIPT: TypeScriptParser(),
            Language.GO: GoParser(),
        }

    def get_parser(self, language: Language) -> LanguageParser | None:
        return self._parsers.get(language)

_registry = _ParserRegistry()

def get_parser_for_language(language: Language) -> LanguageParser | None:
    """Get appropriate parser for a language."""
    return _registry.get_parser(language)


__all__ = [
    "GoParser",
    "JavaScriptParser",
    "LanguageParser",
    "PythonParser",
    "TypeScriptParser",
    "get_parser_for_language",
]
