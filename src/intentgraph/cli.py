"""Command-line interface for IntentGraph."""

from __future__ import annotations

# Standard library imports
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import TYPE_CHECKING

# Third-party imports
import click
import typer
from rich.console import Console

if TYPE_CHECKING:
    from .domain.models import AnalysisResult
    from .query_engine import QueryEngine

app = typer.Typer(
    name="intentgraph",
    help="🧬 Your Codebase's Genome - AI-optimized intelligence for autonomous coding agents",
    no_args_is_help=True,
)
console = Console()


def validate_languages_input(value: str | None) -> str | None:
    """Validate languages input parameter with Unicode normalization."""
    if value is None:
        return None
    
    # Normalize Unicode to prevent bypass attempts
    normalized = unicodedata.normalize('NFKC', value)
    
    # Check for reasonable length
    if len(normalized) > 100:
        raise typer.BadParameter("Languages string too long")
    
    # Enhanced character validation
    if not re.match(r'^[a-zA-Z,\s]+$', normalized):
        raise typer.BadParameter("Languages string contains invalid characters")
    
    # Validate individual language codes
    valid_languages = {'py', 'js', 'ts', 'go', 'python', 'javascript', 'typescript', 'golang'}
    languages = [lang.strip().lower() for lang in normalized.split(',')]
    
    for lang in languages:
        if lang and lang not in valid_languages:
            raise typer.BadParameter(f"Unknown language: {lang}")
    
    return normalized


def filter_result_by_level(result: AnalysisResult, level: str) -> dict:
    """Filter analysis result based on detail level for AI-friendly output."""

    if level == "full":
        return result.model_dump()

    # Build UUID to path mapping for dependencies
    file_id_map = {str(file_info.id): str(file_info.path) for file_info in result.files}

    # Start with basic structure
    filtered_result = {
        "analyzed_at": result.analyzed_at,
        "root": str(result.root),
        "language_summary": {str(k): v.model_dump() for k, v in result.language_summary.items()},
        "file_id_map": file_id_map,  # Add UUID to path mapping
        "files": []
    }
    
    for file_info in result.files:
        if level == "minimal":
            # Minimal: paths, language, dependencies, imports, basic metrics only
            filtered_file = {
                "path": str(file_info.path),
                "language": file_info.language,
                "dependencies": [str(dep) for dep in file_info.dependencies],
                "imports": file_info.imports,
                "loc": file_info.loc,
                "complexity_score": file_info.complexity_score,
            }
        
        elif level == "medium":
            # Medium: add key symbols, exports, detailed metrics
            filtered_file = {
                "path": str(file_info.path),
                "language": file_info.language,
                "dependencies": [str(dep) for dep in file_info.dependencies],
                "imports": file_info.imports,
                "loc": file_info.loc,
                "complexity_score": file_info.complexity_score,
                "maintainability_index": file_info.maintainability_index,
                # Include only key symbols (classes and main functions)
                "symbols": [
                    {
                        "name": symbol.name,
                        "symbol_type": symbol.symbol_type,
                        "line_start": symbol.line_start,
                        "is_exported": getattr(symbol, 'is_exported', False),
                    }
                    for symbol in file_info.symbols
                    if symbol.symbol_type in ["class", "function"] and 
                       (symbol.name.startswith("_") == False or symbol.symbol_type == "class")
                ],
                "exports": [
                    {
                        "name": export.name,
                        "export_type": export.export_type,
                    }
                    for export in file_info.exports
                ],
                "file_purpose": file_info.file_purpose,
            }

        else:
            # Unknown level, default to minimal
            filtered_file = {
                "path": str(file_info.path),
                "language": file_info.language,
                "dependencies": [str(dep) for dep in file_info.dependencies],
                "imports": file_info.imports,
                "loc": file_info.loc,
                "complexity_score": file_info.complexity_score,
            }

        filtered_result["files"].append(filtered_file)
    
    return filtered_result


@app.command(
    epilog="💡 Pro tips:\n"
           "  • Default output (~10KB) fits any AI context window\n"
           "  • Use --cluster for massive repos (outputs to .intentgraph/)\n"
           "  • Add .intentgraph/ to your .gitignore\n"
           "  • Start with --level minimal for AI agents\n\n"
           "📚 Full documentation: https://github.com/Raytracer76/intentgraph"
)
def analyze(
    repository_path: Path = typer.Argument(
        ...,
        help="Path to the Git repository to analyze",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output: Path | None = typer.Option(
        None,
        "-o",
        "--output",
        help="Output file path (- for stdout)",
    ),
    languages: str | None = typer.Option(
        None,
        "--lang",
        help="Comma-separated list of languages to analyze (py,js,ts,go)",
        callback=validate_languages_input,
    ),
    include_tests: bool = typer.Option(
        False,
        "--include-tests",
        help="Include test files in analysis",
    ),
    output_format: str = typer.Option(
        "pretty",
        "--format",
        help="Output format",
        click_type=click.Choice(["pretty", "compact"]),
    ),
    show_cycles: bool = typer.Option(
        False,
        "--show-cycles",
        help="Show dependency cycles and exit with code 2 if any found",
    ),
    workers: int = typer.Option(
        0,
        "--workers",
        help="Number of parallel workers (0 = auto)",
    ),
    level: str = typer.Option(
        "minimal",
        "--level",
        help="🤖 Output level: minimal (~10KB, perfect for AI agents), medium (~70KB, detailed analysis), full (~340KB, comprehensive audit)",
        click_type=click.Choice(["minimal", "medium", "full"]),
    ),
    cluster: bool = typer.Option(
        False,
        "--cluster",
        help="🧩 Enable intelligent clustering for massive repos (outputs to .intentgraph/ by default)",
    ),
    cluster_mode: str = typer.Option(
        "analysis",
        "--cluster-mode",
        help="🎯 Clustering strategy: analysis (understand code), refactoring (make changes), navigation (explore large repos)",
        click_type=click.Choice(["analysis", "refactoring", "navigation"]),
    ),
    cluster_size: str = typer.Option(
        "15KB",
        "--cluster-size",
        help="Target cluster size: 10KB, 15KB, 20KB",
        click_type=click.Choice(["10KB", "15KB", "20KB"]),
    ),
    index_level: str = typer.Option(
        "rich",
        "--index-level",
        help="Index detail level: basic (simple mapping), rich (full metadata)",
        click_type=click.Choice(["basic", "rich"]),
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
) -> None:
    """Analyze a Git repository and generate dependency graph."""

    # Setup logging (RichHandler is cheap — rich already loaded for Console)
    import logging
    from rich.logging import RichHandler
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_path=debug)],
    )

    logger = logging.getLogger(__name__)

    try:
        # Lazy imports — keep startup cost near-zero for --help
        from rich.progress import Progress, SpinnerColumn, TextColumn
        from rich.table import Table
        from .application.analyzer import RepositoryAnalyzer
        from .application.clustering import ClusteringEngine
        from .domain.clustering import ClusterConfig, ClusterMode, IndexLevel
        from .domain.exceptions import CyclicDependencyError, IntentGraphError
        from .domain.models import Language

        # Parse language filter
        lang_filter = None
        if languages:
            lang_filter = []
            for lang in languages.split(","):
                lang = lang.strip().lower()
                if lang == "py":
                    lang_filter.append(Language.PYTHON)
                elif lang == "js":
                    lang_filter.append(Language.JAVASCRIPT)
                elif lang == "ts":
                    lang_filter.append(Language.TYPESCRIPT)
                elif lang == "go":
                    lang_filter.append(Language.GO)
                else:
                    logger.warning(f"Unknown language: {lang}")

        # Initialize analyzer
        analyzer = RepositoryAnalyzer(
            workers=workers or None,
            include_tests=include_tests,
            language_filter=lang_filter,
        )

        # Run analysis with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Analyzing repository...", total=None)
            result = analyzer.analyze(repository_path.resolve())
            progress.update(task, description="Analysis complete")

        # Check for cycles
        if show_cycles:
            cycles = analyzer.graph.find_cycles()
            if cycles:
                console.print("[red]Dependency cycles found:[/red]")
                for i, cycle in enumerate(cycles, 1):
                    console.print(f"  {i}. {' -> '.join(str(analyzer.graph.get_file_info(f).path) for f in cycle)}")
                raise CyclicDependencyError(cycles)

        # Handle cluster mode or regular analysis
        if cluster:
            # Parse cluster configuration
            cluster_mode_enum = ClusterMode(cluster_mode)
            index_level_enum = IndexLevel(index_level)
            target_size_kb = int(cluster_size.replace("KB", ""))
            
            # Create cluster configuration
            cluster_config = ClusterConfig(
                mode=cluster_mode_enum,
                target_size_kb=target_size_kb,
                index_level=index_level_enum,
                allow_overlap=(cluster_mode_enum == ClusterMode.ANALYSIS)
            )
            
            # Run clustering
            clustering_engine = ClusteringEngine(cluster_config)
            cluster_result = clustering_engine.cluster_repository(result)
            
            # Handle cluster output
            if output is None:
                # Default to .intentgraph/ directory (gitignore-friendly)
                output_dir = repository_path / ".intentgraph"
                output_dir.mkdir(exist_ok=True)
                
                # Write index and cluster files to default directory
                index_path = output_dir / "index.json"
                index_json = json.dumps(
                    cluster_result.index.model_dump(),
                    indent=2 if output_format == "pretty" else None,
                    ensure_ascii=False,
                    default=str
                )
                index_path.write_text(index_json, encoding="utf-8")
                
                # Write cluster files
                for cluster_id, cluster_data in cluster_result.cluster_files.items():
                    cluster_path = output_dir / f"{cluster_id}.json"
                    cluster_json = json.dumps(
                        cluster_data,
                        indent=2 if output_format == "pretty" else None,
                        ensure_ascii=False,
                        default=str
                    )
                    cluster_path.write_text(cluster_json, encoding="utf-8")
                
                console.print(f"[green]Cluster analysis complete![/green] Results written to {output_dir}")
                console.print(f"📁 Generated {len(cluster_result.cluster_files)} clusters + index.json")
                
            elif str(output) == "-":
                # Output index to stdout for cluster mode
                index_json = json.dumps(
                    cluster_result.index.model_dump(),
                    indent=2 if output_format == "pretty" else None,
                    ensure_ascii=False,
                    default=str
                )
                console.print(index_json)
            else:
                # Create output directory for clusters
                output_dir = output.parent / output.stem if output.suffix else output
                # Handle special file paths like /dev/stdout
                if not str(output_dir).startswith(("/dev/", "/proc/")):
                    output_dir.mkdir(exist_ok=True)
                
                # Write index file
                index_path = output_dir / "index.json"
                index_json = json.dumps(
                    cluster_result.index.model_dump(),
                    indent=2 if output_format == "pretty" else None,
                    ensure_ascii=False,
                    default=str
                )
                index_path.write_text(index_json, encoding="utf-8")
                
                # Write cluster files
                for cluster_id, cluster_data in cluster_result.cluster_files.items():
                    cluster_path = output_dir / f"{cluster_id}.json"
                    cluster_json = json.dumps(
                        cluster_data,
                        indent=2 if output_format == "pretty" else None,
                        ensure_ascii=False,
                        default=str
                    )
                    cluster_path.write_text(cluster_json, encoding="utf-8")
                
                console.print(f"[green]Cluster analysis complete![/green] Results written to {output_dir}")
                console.print(f"📁 Generated {len(cluster_result.cluster_files)} clusters + index.json")
            
            # Show cluster summary
            cluster_table = Table(title="Cluster Analysis Summary")
            cluster_table.add_column("Metric", style="cyan")
            cluster_table.add_column("Value", style="magenta")
            
            cluster_table.add_row("Files analyzed", str(cluster_result.index.total_files))
            cluster_table.add_row("Clusters generated", str(cluster_result.index.total_clusters))
            cluster_table.add_row("Cluster mode", cluster_mode.title())
            cluster_table.add_row("Target size", cluster_size)
            cluster_table.add_row("Index level", index_level.title())
            
            console.print(cluster_table)
            return
        
        # Regular analysis mode - apply level filtering
        filtered_result = filter_result_by_level(result, level)
        
        # Format output
        if output_format == "pretty":
            result_json = json.dumps(filtered_result, indent=2, ensure_ascii=False, default=str)
        else:
            result_json = json.dumps(filtered_result, ensure_ascii=False, default=str)

        # Write output
        if output is None or str(output) == "-":
            console.print(result_json)
        else:
            output.write_text(result_json, encoding="utf-8")
            console.print(f"[green]Analysis complete![/green] Results written to {output}")

        # Show summary
        stats = analyzer.graph.get_stats()
        summary_table = Table(title="Analysis Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")

        summary_table.add_row("Files analyzed", str(stats["nodes"]))
        summary_table.add_row("Dependencies", str(stats["edges"]))
        summary_table.add_row("Cycles", str(stats["cycles"]))
        summary_table.add_row("Components", str(stats["components"]))

        console.print(summary_table)

    except CyclicDependencyError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)
    except IntentGraphError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        console.print(f"[red]Unexpected error:[/red] {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# New Typer sub-apps — query and cache
# ---------------------------------------------------------------------------

query_app = typer.Typer(
    name="query",
    help="Query cached repository analysis.",
    no_args_is_help=True,
)
cache_app = typer.Typer(
    name="cache",
    help="Manage the analysis cache.",
    no_args_is_help=True,
)
app.add_typer(query_app)
app.add_typer(cache_app)


def _load_engine(repo: Path) -> tuple[QueryEngine, AnalysisResult]:
    """Load or analyse the repo and return ``(engine, result)``."""
    from .cache import CacheManager
    from .query_engine import QueryEngine
    result = CacheManager(repo).load_or_analyze()
    engine = QueryEngine(result)
    return engine, result


# ---------------------------------------------------------------------------
# query sub-commands
# ---------------------------------------------------------------------------


@query_app.command("callers")
def query_callers(
    symbol: str = typer.Argument(..., help="Symbol name to look up callers for."),
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Return all callers of a symbol."""
    try:
        engine, _ = _load_engine(repo)
        out = engine.callers(symbol)
        print(json.dumps(out, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


@query_app.command("dependents")
def query_dependents(
    file: str = typer.Argument(..., help="File path to look up dependents for."),
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Return files that depend on the given file."""
    try:
        engine, _ = _load_engine(repo)
        out = engine.dependents(file)
        print(json.dumps(out, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


@query_app.command("deps")
def query_deps(
    file: str = typer.Argument(..., help="File path to list dependencies for."),
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Return direct dependencies of the given file."""
    try:
        engine, _ = _load_engine(repo)
        out = engine.deps(file)
        print(json.dumps(out, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


@query_app.command("context")
def query_context(
    file: str = typer.Argument(..., help="File path to get context for."),
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Return full context for the given file."""
    try:
        engine, _ = _load_engine(repo)
        out = engine.context(file)
        print(json.dumps(out, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


@query_app.command("search")
def query_search(
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
    name_matches: str | None = typer.Option(None, "--name-matches", help="Regex pattern for file name."),
    complexity_gt: int | None = typer.Option(None, "--complexity-gt", help="Minimum complexity score."),
    lang: str | None = typer.Option(None, "--lang", help="Language filter."),
    has_symbol: str | None = typer.Option(None, "--has-symbol", help="Symbol that must be present."),
) -> None:
    """Search files by criteria. At least one filter option must be provided."""
    if name_matches is None and complexity_gt is None and lang is None and has_symbol is None:
        typer.echo(json.dumps({"error": "At least one search option must be provided"}), err=True)
        raise typer.Exit(1)
    try:
        engine, _ = _load_engine(repo)
        out = engine.search(name_matches, complexity_gt, lang, has_symbol)
        print(json.dumps(out, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


@query_app.command("path")
def query_path(
    file_a: str = typer.Argument(..., help="Source file path."),
    file_b: str = typer.Argument(..., help="Target file path."),
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Find the dependency path between two files."""
    try:
        engine, _ = _load_engine(repo)
        out = engine.path(file_a, file_b)
        print(json.dumps(out, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


@query_app.command("symbols")
def query_symbols(
    file: str = typer.Argument(..., help="File path to list symbols for."),
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Return all symbols defined in the given file."""
    try:
        engine, _ = _load_engine(repo)
        out = engine.symbols(file)
        print(json.dumps(out, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# cache sub-commands
# ---------------------------------------------------------------------------


@cache_app.command("status")
def cache_status(
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Show cache status for the repository."""
    try:
        from .cache import CacheManager
        out = CacheManager(repo).status()
        print(json.dumps(out, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


@cache_app.command("warm")
def cache_warm(
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Warm the cache by running analysis if needed."""
    try:
        from .cache import CacheManager
        result = CacheManager(repo).load_or_analyze()
        print(json.dumps({"warmed": True, "file_count": len(result.files)}, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)


@cache_app.command("clear")
def cache_clear(
    repo: Path = typer.Option(Path("."), "--repo", help="Path to the repository."),
) -> None:
    """Clear the analysis cache for the repository."""
    try:
        from .cache import CacheManager
        CacheManager(repo).clear()
        print(json.dumps({"cleared": True}, indent=2))
    except Exception as e:
        typer.echo(json.dumps({"error": str(e)}), err=True)
        raise typer.Exit(1)
