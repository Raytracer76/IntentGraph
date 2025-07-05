"""Graph operations and cycle detection."""

from uuid import UUID

import networkx as nx

from .models import FileInfo


class DependencyGraph:
    """Manages dependency relationships between files."""

    def __init__(self) -> None:
        self._graph = nx.DiGraph()
        self._file_map: dict[UUID, FileInfo] = {}

    def add_file(self, file_info: FileInfo) -> None:
        """Add a file to the graph."""
        self._graph.add_node(file_info.id)
        self._file_map[file_info.id] = file_info

    def add_dependency(self, from_file: UUID, to_file: UUID) -> None:
        """Add a dependency edge from one file to another."""
        if from_file in self._file_map and to_file in self._file_map:
            self._graph.add_edge(from_file, to_file)

    def find_cycles(self) -> list[list[UUID]]:
        """Find all cycles in the dependency graph."""
        try:
            cycles = list(nx.simple_cycles(self._graph))
            return cycles
        except nx.NetworkXNoCycle:
            return []

    def get_dependencies(self, file_id: UUID) -> list[UUID]:
        """Get direct dependencies of a file."""
        return list(self._graph.successors(file_id))

    def get_dependents(self, file_id: UUID) -> list[UUID]:
        """Get files that depend on this file."""
        return list(self._graph.predecessors(file_id))

    def topological_sort(self) -> list[UUID]:
        """Get files in topological order (dependencies first)."""
        try:
            return list(nx.topological_sort(self._graph))
        except nx.NetworkXError:
            # Graph has cycles, return approximate ordering
            return list(self._graph.nodes())

    def strongly_connected_components(self) -> list[set[UUID]]:
        """Find strongly connected components (circular dependencies)."""
        return [set(component) for component in nx.strongly_connected_components(self._graph)]

    def get_file_info(self, file_id: UUID) -> FileInfo:
        """Get file information by ID."""
        return self._file_map[file_id]

    def get_stats(self) -> dict[str, int]:
        """Get graph statistics."""
        return {
            "nodes": self._graph.number_of_nodes(),
            "edges": self._graph.number_of_edges(),
            "cycles": len(self.find_cycles()),
            "components": len(self.strongly_connected_components()),
        }
