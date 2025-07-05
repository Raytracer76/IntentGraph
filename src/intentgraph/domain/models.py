"""Core domain models for IntentGraph."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class Language(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    UNKNOWN = "unknown"

    @classmethod
    def from_extension(cls, extension: str) -> "Language":
        """Determine language from file extension."""
        ext_map = {
            ".py": cls.PYTHON,
            ".js": cls.JAVASCRIPT,
            ".jsx": cls.JAVASCRIPT,
            ".ts": cls.TYPESCRIPT,
            ".tsx": cls.TYPESCRIPT,
            ".go": cls.GO,
        }
        return ext_map.get(extension.lower(), cls.UNKNOWN)


@dataclass(frozen=True)
class CodeSymbol:
    """Represents a function, class, or other code symbol.
    
    This class captures detailed information about code symbols including
    their location, signature, documentation, and export status. Used by
    AI agents to understand code structure and relationships.
    
    Attributes:
        name: The symbol name as it appears in code
        symbol_type: Type of symbol ('function', 'class', 'variable', 'import')
        line_start: Starting line number in source file
        line_end: Ending line number in source file
        signature: Full signature for functions/classes
        docstring: Documentation string if present
        is_exported: True if part of public API
        is_private: True if starts with underscore
        decorators: List of decorator names applied to symbol
        parent: Parent symbol name for nested definitions
        
    Examples:
        >>> symbol = CodeSymbol(
        ...     name="analyze_repository", 
        ...     symbol_type="function",
        ...     line_start=42,
        ...     line_end=58,
        ...     signature="def analyze_repository(path: Path) -> AnalysisResult",
        ...     is_exported=True
        ... )
        >>> print(symbol.name)
        analyze_repository
    """
    
    name: str = field()
    symbol_type: str = field()  # 'function', 'class', 'variable', 'import'
    line_start: int = field()
    line_end: int = field()
    signature: Optional[str] = field(default=None)  # Function signature or class definition
    docstring: Optional[str] = field(default=None)
    is_exported: bool = field(default=False)  # Part of public API
    is_private: bool = field(default=False)  # Starts with underscore
    decorators: list[str] = field(default_factory=list)
    parent: Optional[str] = field(default=None)  # For nested classes/functions
    id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class FunctionDependency:
    """Represents a specific function-level dependency."""
    
    from_symbol: UUID = field()  # Symbol that has the dependency
    to_symbol: UUID = field()    # Symbol being depended on
    to_file: UUID = field()      # File containing the target symbol
    dependency_type: str = field()  # 'calls', 'inherits', 'imports', 'instantiates'
    line_number: int = field()   # Where this dependency occurs
    context: Optional[str] = field(default=None)  # Code context around dependency


@dataclass(frozen=True)
class APIExport:
    """Represents something exported by a module."""
    
    name: str = field()
    export_type: str = field()  # 'function', 'class', 'variable', 'constant'
    symbol_id: Optional[UUID] = field(default=None)  # Link to CodeSymbol if defined here
    is_reexport: bool = field(default=False)  # Re-exported from another module
    original_module: Optional[str] = field(default=None)  # If re-exported
    docstring: Optional[str] = field(default=None)


@dataclass(frozen=True)
class FileInfo:
    """Information about a source file."""

    path: Path = field()
    language: Language = field()
    sha256: str = field()
    loc: int = field()
    id: UUID = field(default_factory=uuid4)
    dependencies: list[UUID] = field(default_factory=list)  # File-level dependencies
    
    # Enhanced code structure analysis
    symbols: list[CodeSymbol] = field(default_factory=list)  # Functions, classes, etc.
    exports: list[APIExport] = field(default_factory=list)   # Public API surface
    function_dependencies: list[FunctionDependency] = field(default_factory=list)  # Function-level deps
    imports: list[str] = field(default_factory=list)        # Import statements
    complexity_score: int = field(default=0)                # Cyclomatic complexity
    maintainability_index: float = field(default=0.0)      # Maintainability score
    
    # Semantic information for AI agents
    file_purpose: Optional[str] = field(default=None)       # Inferred purpose
    key_abstractions: list[str] = field(default_factory=list)  # Main concepts
    design_patterns: list[str] = field(default_factory=list)   # Detected patterns

    @classmethod
    def from_path(cls, path: Path, root: Path) -> "FileInfo":
        """Create FileInfo from file path."""
        relative_path = path.relative_to(root)
        language = Language.from_extension(path.suffix)

        content = path.read_bytes()
        sha256 = hashlib.sha256(content).hexdigest()

        # Count lines of code (excluding empty lines and comments)
        try:
            text_content = content.decode("utf-8")
            lines = text_content.splitlines()
            loc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])
        except UnicodeDecodeError:
            loc = 0

        return cls(
            path=relative_path,
            language=language,
            sha256=sha256,
            loc=loc,
        )


class LanguageSummary(BaseModel):
    """Summary statistics for a language."""

    file_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)


class AnalysisResult(BaseModel):
    """Complete analysis result."""

    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    root: Path = Field()
    language_summary: dict[Language, LanguageSummary] = Field(default_factory=dict)
    files: list[FileInfo] = Field(default_factory=list)

    @validator("analyzed_at", pre=True)
    def validate_analyzed_at(cls, v):
        """Ensure analyzed_at is a datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            Path: str,
            UUID: str,
        }
