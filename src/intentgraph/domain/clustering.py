"""Clustering models and types for IntentGraph."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ClusterMode(str, Enum):
    """Clustering modes for different use cases."""
    
    ANALYSIS = "analysis"        # Code understanding (dependency-based with overlap)
    REFACTORING = "refactoring"  # Code changes (feature-based, no overlap)
    NAVIGATION = "navigation"    # Large codebase exploration (size-optimized)


class IndexLevel(str, Enum):
    """Index detail levels for different AI agent needs."""
    
    BASIC = "basic"    # Simple file → cluster mapping
    RICH = "rich"      # Full metadata with complexity, concerns, relationships


@dataclass(frozen=True)
class ClusterConfig:
    """Configuration for clustering operation."""
    
    mode: ClusterMode = field(default=ClusterMode.ANALYSIS)
    target_size_kb: int = field(default=15)
    index_level: IndexLevel = field(default=IndexLevel.RICH)
    allow_overlap: bool = field(default=True)
    max_overlap_percentage: float = field(default=30.0)  # Max 30% size increase from overlap
    min_cluster_size_kb: int = field(default=5)
    max_cluster_size_kb: int = field(default=25)


@dataclass(frozen=True)  
class ClusterFile:
    """File information within a cluster."""
    
    path: Path = field()
    language: str = field()
    size_kb: float = field()
    complexity_score: int = field()
    is_central: bool = field(default=False)  # Appears in multiple clusters
    role: str = field(default="implementation")  # "interface", "implementation", "utility"


@dataclass(frozen=True)
class ClusterMetadata:
    """Rich metadata for a cluster."""
    
    primary_concerns: List[str] = field(default_factory=list)  # ["data_models", "validation"]
    design_patterns: List[str] = field(default_factory=list)   # ["factory", "adapter"]
    key_abstractions: List[str] = field(default_factory=list)  # ["User", "Parser"]
    entry_points: List[str] = field(default_factory=list)      # Main functions/classes
    complexity_score: int = field(default=0)
    maintainability_index: float = field(default=0.0)
    test_coverage_percentage: float = field(default=0.0)


class ClusterSummary(BaseModel):
    """Summary information for a single cluster."""
    
    cluster_id: str = Field()
    name: str = Field()  # Human-readable name like "domain_models" 
    description: str = Field()
    files: List[ClusterFile] = Field(default_factory=list)
    file_count: int = Field(ge=0)
    total_size_kb: float = Field(ge=0.0)
    dependencies: List[str] = Field(default_factory=list)  # Other cluster IDs
    metadata: ClusterMetadata = Field(default_factory=ClusterMetadata)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CrossClusterDependency(BaseModel):
    """Dependency relationship between clusters."""
    
    from_cluster: str = Field()
    to_cluster: str = Field()
    strength: str = Field()  # "high", "medium", "low"
    dependency_type: str = Field()  # "imports", "calls", "inherits", "configures"
    file_count: int = Field(ge=0)  # Number of files involved in dependency


class ClusterIndex(BaseModel):
    """Master index for cluster navigation."""
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    root_path: Path = Field()
    config: ClusterConfig = Field()
    total_files: int = Field(ge=0)
    total_clusters: int = Field(ge=0)
    
    # Core navigation data
    clusters: List[ClusterSummary] = Field(default_factory=list)
    file_to_cluster_map: Dict[str, str] = Field(default_factory=dict)  # file_path → cluster_id
    cross_cluster_dependencies: List[CrossClusterDependency] = Field(default_factory=list)
    
    # AI agent assistance
    cluster_recommendations: Dict[str, List[str]] = Field(default_factory=dict)  # use_case → cluster_ids
    hotspot_files: List[str] = Field(default_factory=list)  # Files that appear in multiple clusters
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            Path: str,
            UUID: str,
        }


class ClusterResult(BaseModel):
    """Complete clustering result with index and cluster files."""
    
    index: ClusterIndex = Field()
    cluster_files: Dict[str, dict] = Field(default_factory=dict)  # cluster_id → cluster_data
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z", 
            Path: str,
            UUID: str,
        }