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
        # Lazy initialization: parsers are created on first access
        self._parsers = {}
        self._parser_factories = {
            Language.PYTHON: PythonParser,
            Language.JAVASCRIPT: JavaScriptParser,
            Language.TYPESCRIPT: TypeScriptParser,
            Language.GO: GoParser,
        }

    def get_parser(self, language: Language) -> LanguageParser | None:
        # Create parser on first access (lazy initialization)
        if language not in self._parsers and language in self._parser_factories:
            try:
                self._parsers[language] = self._parser_factories[language]()
            except Exception as e:
                # Log but don't fail if a parser can't be initialized
                # (e.g., tree-sitter native libraries blocked by security policy)
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to initialize {language.value} parser: {e}")
                return None
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
