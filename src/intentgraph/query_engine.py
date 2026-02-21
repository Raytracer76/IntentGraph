"""QueryEngine — in-memory index and query interface over AnalysisResult.

T-02 of SPEC-IG-QUERY-0001.

This module MUST NOT import from intentgraph.ai.
"""

from __future__ import annotations

import re
from collections import deque
from uuid import UUID

from intentgraph.domain.models import AnalysisResult, CodeSymbol, FileInfo


class QueryEngine:
    """Build in-memory indices from an AnalysisResult and expose query methods."""

    def __init__(self, result: AnalysisResult) -> None:
        self._result = result

        # Index: UUID -> FileInfo
        self._file_by_id: dict[UUID, FileInfo] = {}

        # Index: normalised relative path string -> FileInfo
        self._file_by_path: dict[str, FileInfo] = {}

        # Index: symbol name -> list of (FileInfo, CodeSymbol)
        self._symbol_by_name: dict[str, list[tuple[FileInfo, CodeSymbol]]] = {}

        # Index: file UUID -> list of file UUIDs that declare it as a dependency
        self._reverse_deps: dict[UUID, list[UUID]] = {}

        self._build_indices()

    # ------------------------------------------------------------------
    # Index construction
    # ------------------------------------------------------------------

    def _build_indices(self) -> None:
        for fi in self._result.files:
            self._file_by_id[fi.id] = fi
            self._file_by_path[str(fi.path)] = fi

            for sym in fi.symbols:
                self._symbol_by_name.setdefault(sym.name, []).append((fi, sym))

        for fi in self._result.files:
            for dep_id in fi.dependencies:
                self._reverse_deps.setdefault(dep_id, []).append(fi.id)

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def callers(self, symbol_name: str) -> dict[str, object]:
        """Return all FunctionDependency records whose target symbol matches symbol_name.

        Note: callers() resolves symbol names via the UUID-based symbol index.
        FunctionDependency records referencing symbols not present in this
        AnalysisResult (external/out-of-graph symbols) cannot be found by name
        and will be silently omitted. This is a constraint of the domain model,
        not a bug.
        """
        # Collect target symbol UUIDs for this name
        target_sym_ids: set[UUID] = set()
        for fi, sym in self._symbol_by_name.get(symbol_name, []):
            target_sym_ids.add(sym.id)

        callers_list = []
        for fi in self._result.files:
            for fd in fi.function_dependencies:
                if fd.to_symbol in target_sym_ids:
                    callers_list.append({
                        "file": str(fi.path),
                        "line": fd.line_number,
                        "context": fd.context,
                    })

        return {"symbol": symbol_name, "callers": callers_list}

    def dependents(self, file_path: str) -> dict[str, object]:
        """Return files that declare file_path as a dependency."""
        fi = self._file_by_path.get(file_path)
        if fi is None:
            return {"file": file_path, "dependents": []}

        dependent_ids = self._reverse_deps.get(fi.id, [])
        result_list = []
        for dep_id in dependent_ids:
            dep_fi = self._file_by_id.get(dep_id)
            if dep_fi is not None:
                result_list.append({
                    "file": str(dep_fi.path),
                    "dependency_type": "file-level",
                })

        return {"file": file_path, "dependents": result_list}

    def deps(self, file_path: str) -> dict[str, object]:
        """Return files that file_path declares as dependencies."""
        fi = self._file_by_path.get(file_path)
        if fi is None:
            return {"file": file_path, "deps": []}

        result_list = []
        for dep_id in fi.dependencies:
            dep_fi = self._file_by_id.get(dep_id)
            if dep_fi is not None:
                result_list.append({
                    "file": str(dep_fi.path),
                    "dependency_type": "file-level",
                })

        return {"file": file_path, "deps": result_list}

    def context(self, file_path: str) -> dict[str, object]:
        """Return full context dict for a file."""
        fi = self._file_by_path.get(file_path)
        if fi is None:
            raise FileNotFoundError(f"File not found in analysis result: {file_path!r}")

        symbols = [_symbol_to_dict(sym) for sym in fi.symbols]
        exports = [
            {"name": ex.name, "export_type": ex.export_type}
            for ex in fi.exports
        ]
        deps_data = self.deps(file_path)["deps"]
        dependents_data = self.dependents(file_path)["dependents"]

        return {
            "file": file_path,
            "language": fi.language.value,
            "loc": fi.loc,
            "sha256": fi.sha256,
            "symbols": symbols,
            "exports": exports,
            "deps": deps_data,
            "dependents": dependents_data,
        }

    def search(
        self,
        name_pattern: str | None = None,
        complexity_gt: int | None = None,
        lang: str | None = None,
        has_symbol: str | None = None,
    ) -> dict[str, object]:
        """Search files by optional filters; all active filters are ANDed."""
        query_echo = {
            "name_pattern": name_pattern,
            "complexity_gt": complexity_gt,
            "lang": lang,
            "has_symbol": has_symbol,
        }

        results = []
        for fi in self._result.files:
            if not _passes_name_pattern(fi, name_pattern):
                continue
            if not _passes_lang(fi, lang):
                continue
            if not _passes_has_symbol(fi, has_symbol):
                continue
            if not _passes_complexity(fi, complexity_gt):
                continue

            results.append({
                "file": str(fi.path),
                "language": fi.language.value,
                "loc": fi.loc,
                "symbol_count": len(fi.symbols),
            })

        return {"query": query_echo, "results": results}

    def path(self, file_a: str, file_b: str) -> dict[str, object]:
        """Compute shortest directed dependency path from file_a to file_b via BFS."""
        if file_a == file_b:
            return {
                "from": file_a,
                "to": file_b,
                "path": [file_a],
                "found": True,
            }

        fi_a = self._file_by_path.get(file_a)
        fi_b = self._file_by_path.get(file_b)
        if fi_a is None or fi_b is None:
            return {"from": file_a, "to": file_b, "path": [], "found": False}

        # BFS over forward dependency graph: fi -> fi.dependencies
        # predecessor map: UUID -> UUID | None (how we reached this node)
        predecessors: dict[UUID, UUID | None] = {fi_a.id: None}
        queue: deque[UUID] = deque([fi_a.id])
        found = False

        while queue and not found:
            current_id = queue.popleft()
            current_fi = self._file_by_id[current_id]
            for dep_id in current_fi.dependencies:
                if dep_id not in self._file_by_id:  # guard first
                    continue
                if dep_id not in predecessors:
                    predecessors[dep_id] = current_id
                    if dep_id == fi_b.id:  # early exit second
                        found = True
                        break
                    queue.append(dep_id)

        if found:
            # Reconstruct path
            path_ids = []
            node: UUID | None = fi_b.id
            while node is not None:
                path_ids.append(node)
                node = predecessors[node]
            path_ids.reverse()
            path_strs = [str(self._file_by_id[n].path) for n in path_ids]
            return {"from": file_a, "to": file_b, "path": path_strs, "found": True}

        return {"from": file_a, "to": file_b, "path": [], "found": False}

    def symbols(self, file_path: str) -> dict[str, object]:
        """Return all symbols for a file."""
        fi = self._file_by_path.get(file_path)
        if fi is None:
            raise FileNotFoundError(f"File not found in analysis result: {file_path!r}")

        return {
            "file": file_path,
            "symbols": [_symbol_to_dict(sym) for sym in fi.symbols],
        }


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------

def _symbol_to_dict(sym: CodeSymbol) -> dict[str, object]:
    return {
        "name": sym.name,
        "type": sym.symbol_type,
        "line_start": sym.line_start,
        "line_end": sym.line_end,
        "signature": sym.signature,
        "is_exported": sym.is_exported,
        "is_private": sym.is_private,
    }


def _passes_name_pattern(fi: FileInfo, name_pattern: str | None) -> bool:
    if name_pattern is None:
        return True
    return bool(re.search(name_pattern, str(fi.path)))


def _passes_lang(fi: FileInfo, lang: str | None) -> bool:
    if lang is None:
        return True
    return fi.language.value.lower() == lang.lower()


def _passes_has_symbol(fi: FileInfo, has_symbol: str | None) -> bool:
    if has_symbol is None:
        return True
    return any(sym.name == has_symbol for sym in fi.symbols)


def _passes_complexity(fi: FileInfo, complexity_gt: int | None) -> bool:
    """Filter by complexity.

    Complexity is read from FileInfo.complexity_score.
    A score of 0 is treated as "no metric" — those files are NOT excluded.
    Files with complexity_score > 0 are checked against complexity_gt.
    """
    if complexity_gt is None:
        return True
    score = getattr(fi, "complexity_score", 0)
    if score == 0:
        # No metric available — do not exclude
        return True
    return score > complexity_gt
