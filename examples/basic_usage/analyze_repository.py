"""Basic usage examples for IntentGraph repository analysis."""

import json
import subprocess
from pathlib import Path
from intentgraph import RepositoryAnalyzer
from intentgraph.domain.models import Language


def analyze_repository_basic():
    """Basic repository analysis example."""
    # Initialize analyzer
    analyzer = RepositoryAnalyzer()
    
    # Analyze current directory
    result = analyzer.analyze(Path.cwd())
    
    print(f"Files analyzed: {len(result.files)}")
    print(f"Languages found: {list(result.language_summary.keys())}")
    
    return result


def analyze_with_options():
    """Repository analysis with custom options."""
    analyzer = RepositoryAnalyzer(
        workers=4,  # Use 4 parallel workers
        include_tests=True,  # Include test files
        language_filter=[Language.PYTHON, Language.JAVASCRIPT]  # Only Python and JS
    )
    
    result = analyzer.analyze(Path.cwd())
    
    for file_info in result.files:
        print(f"{file_info.path}: {len(file_info.symbols)} symbols")
    
    return result


def analyze_with_streaming():
    """Memory-efficient analysis for large repositories."""
    from intentgraph.application.streaming_analyzer import StreamingAnalyzer
    
    streaming_analyzer = StreamingAnalyzer(batch_size=50)
    
    total_files = 0
    for batch in streaming_analyzer.analyze_repository(Path.cwd()):
        print(f"Processed batch of {len(batch)} files")
        total_files += len(batch)
    
    print(f"Total files processed: {total_files}")


def analyze_incremental():
    """Incremental analysis for changed files only."""
    from intentgraph.application.streaming_analyzer import IncrementalAnalyzer
    
    incremental_analyzer = IncrementalAnalyzer()
    
    # First run analyzes all files
    result = incremental_analyzer.analyze_changed_files(Path.cwd())
    print(f"Initial analysis: {len(result.files)} files")
    
    # Subsequent runs only analyze changed files
    result = incremental_analyzer.analyze_changed_files(Path.cwd())
    print(f"Incremental analysis: {len(result.files)} files")


def demonstrate_output_levels():
    """Demonstrate the three AI-optimized output levels."""
    print("\n🤖 AI-Optimized Output Levels:")
    
    levels = ["minimal", "medium", "full"]
    
    for level in levels:
        print(f"\n--- {level.upper()} Level (--level {level}) ---")
        
        # Use CLI to demonstrate actual output
        result = subprocess.run([
            "intentgraph", ".", 
            "--level", level,
            "--format", "compact"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Calculate size
            size_kb = len(result.stdout.encode('utf-8')) / 1024
            analysis = json.loads(result.stdout)
            
            print(f"Size: {size_kb:.1f}KB")
            print(f"Files: {len(analysis.get('files', []))}")
            
            # Show sample of first file
            if analysis.get('files'):
                first_file = analysis['files'][0]
                print(f"Sample file: {first_file.get('path', 'unknown')}")
                
                # Show what's included at this level
                if level == "minimal":
                    print(f"  Imports: {len(first_file.get('imports', []))}")
                    print(f"  Complexity: {first_file.get('complexity_score', 0)}")
                elif level == "medium":
                    print(f"  Symbols: {len(first_file.get('symbols', []))}")
                    print(f"  Exports: {len(first_file.get('exports', []))}")
                    print(f"  Maintainability: {first_file.get('maintainability_index', 0)}")
                else:  # full
                    print(f"  Complete metadata available")
                    print(f"  Design patterns: {first_file.get('design_patterns', [])}")
        else:
            print(f"Error: {result.stderr}")


def extract_detailed_info():
    """Extract detailed code structure information."""
    analyzer = RepositoryAnalyzer()
    result = analyzer.analyze(Path.cwd())
    
    for file_info in result.files:
        if file_info.language == Language.PYTHON:
            print(f"\nFile: {file_info.path}")
            print(f"Purpose: {file_info.file_purpose}")
            print(f"Complexity: {file_info.complexity_score}")
            print(f"Key abstractions: {file_info.key_abstractions}")
            print(f"Design patterns: {file_info.design_patterns}")
            
            # Show exported symbols
            exports = [s.name for s in file_info.symbols if s.is_exported]
            print(f"Exports: {exports}")


if __name__ == "__main__":
    print("=== IntentGraph Usage Examples ===")
    
    print("\n=== AI-Optimized Output Levels ===")
    demonstrate_output_levels()
    
    print("\n=== Basic Analysis ===")
    analyze_repository_basic()
    
    print("\n=== Analysis with Options ===")
    analyze_with_options()
    
    print("\n=== Streaming Analysis ===")
    analyze_with_streaming()
    
    print("\n=== Incremental Analysis ===")
    analyze_incremental()
    
    print("\n=== Detailed Information ===")
    extract_detailed_info()