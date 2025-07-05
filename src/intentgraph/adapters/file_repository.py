"""Repository pattern implementation for file operations."""

import hashlib
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class FileStats:
    """File statistics data class."""
    
    def __init__(self, size: int, modified_time: float, is_directory: bool = False):
        self.size = size
        self.modified_time = modified_time
        self.is_directory = is_directory


class FileRepository(ABC):
    """Abstract repository for file operations."""
    
    @abstractmethod
    def read_file(self, path: Path) -> bytes:
        """Read file contents as bytes."""
        pass
    
    @abstractmethod
    def read_text(self, path: Path, encoding: str = 'utf-8') -> str:
        """Read file contents as text."""
        pass
    
    @abstractmethod
    def get_file_stats(self, path: Path) -> FileStats:
        """Get file statistics."""
        pass
    
    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check if path exists."""
        pass
    
    @abstractmethod
    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        pass
    
    @abstractmethod
    def is_directory(self, path: Path) -> bool:
        """Check if path is a directory."""
        pass
    
    @abstractmethod
    def list_directory(self, path: Path) -> list[Path]:
        """List directory contents."""
        pass
    
    @abstractmethod
    def calculate_sha256(self, path: Path) -> str:
        """Calculate SHA256 hash of file."""
        pass


class FileSystemRepository(FileRepository):
    """File system implementation of FileRepository."""
    
    def __init__(self):
        self._hash_cache: Dict[str, str] = {}
    
    def read_file(self, path: Path) -> bytes:
        """Read file contents as bytes."""
        try:
            return path.read_bytes()
        except (OSError, PermissionError) as e:
            raise FileRepositoryError(f"Cannot read file {path}: {e}")
    
    def read_text(self, path: Path, encoding: str = 'utf-8') -> str:
        """Read file contents as text."""
        try:
            return path.read_text(encoding=encoding)
        except (OSError, PermissionError, UnicodeDecodeError) as e:
            raise FileRepositoryError(f"Cannot read text from {path}: {e}")
    
    def get_file_stats(self, path: Path) -> FileStats:
        """Get file statistics."""
        try:
            stat = path.stat()
            return FileStats(
                size=stat.st_size,
                modified_time=stat.st_mtime,
                is_directory=path.is_dir()
            )
        except (OSError, PermissionError) as e:
            raise FileRepositoryError(f"Cannot get stats for {path}: {e}")
    
    def exists(self, path: Path) -> bool:
        """Check if path exists."""
        return path.exists()
    
    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        try:
            return path.is_file()
        except (OSError, PermissionError):
            return False
    
    def is_directory(self, path: Path) -> bool:
        """Check if path is a directory."""
        try:
            return path.is_dir()
        except (OSError, PermissionError):
            return False
    
    def list_directory(self, path: Path) -> list[Path]:
        """List directory contents."""
        try:
            return list(path.iterdir())
        except (OSError, PermissionError) as e:
            raise FileRepositoryError(f"Cannot list directory {path}: {e}")
    
    def calculate_sha256(self, path: Path) -> str:
        """Calculate SHA256 hash of file with caching."""
        path_str = str(path.resolve())
        
        # Check cache first
        if path_str in self._hash_cache:
            # Verify file hasn't changed
            try:
                stats = self.get_file_stats(path)
                cache_key = f"{path_str}:{stats.size}:{stats.modified_time}"
                if cache_key in self._hash_cache:
                    return self._hash_cache[cache_key]
            except FileRepositoryError:
                pass
        
        # Calculate hash
        try:
            content = self.read_file(path)
            hash_value = hashlib.sha256(content).hexdigest()
            
            # Cache with file metadata
            stats = self.get_file_stats(path)
            cache_key = f"{path_str}:{stats.size}:{stats.modified_time}"
            self._hash_cache[cache_key] = hash_value
            
            return hash_value
        except Exception as e:
            raise FileRepositoryError(f"Cannot calculate hash for {path}: {e}")


class CachedFileRepository(FileRepository):
    """File repository with comprehensive caching."""
    
    def __init__(self, base_repository: FileRepository):
        self.base = base_repository
        self._content_cache: Dict[str, bytes] = {}
        self._stats_cache: Dict[str, FileStats] = {}
        self._exists_cache: Dict[str, bool] = {}
        self._max_cache_size = 1000
    
    def _get_cache_key(self, path: Path) -> str:
        """Generate cache key for path."""
        return str(path.resolve())
    
    def _evict_cache_if_needed(self):
        """Evict oldest entries if cache is too large."""
        if len(self._content_cache) > self._max_cache_size:
            # Simple LRU eviction - remove 10% of entries
            to_remove = len(self._content_cache) // 10
            for key in list(self._content_cache.keys())[:to_remove]:
                del self._content_cache[key]
    
    def read_file(self, path: Path) -> bytes:
        """Read file contents with caching."""
        cache_key = self._get_cache_key(path)
        
        if cache_key in self._content_cache:
            return self._content_cache[cache_key]
        
        content = self.base.read_file(path)
        
        self._evict_cache_if_needed()
        self._content_cache[cache_key] = content
        
        return content
    
    def read_text(self, path: Path, encoding: str = 'utf-8') -> str:
        """Read file contents as text."""
        content = self.read_file(path)
        try:
            return content.decode(encoding)
        except UnicodeDecodeError as e:
            raise FileRepositoryError(f"Cannot decode {path} as {encoding}: {e}")
    
    def get_file_stats(self, path: Path) -> FileStats:
        """Get file statistics with caching."""
        cache_key = self._get_cache_key(path)
        
        if cache_key in self._stats_cache:
            return self._stats_cache[cache_key]
        
        stats = self.base.get_file_stats(path)
        self._stats_cache[cache_key] = stats
        
        return stats
    
    def exists(self, path: Path) -> bool:
        """Check if path exists with caching."""
        cache_key = self._get_cache_key(path)
        
        if cache_key in self._exists_cache:
            return self._exists_cache[cache_key]
        
        exists = self.base.exists(path)
        self._exists_cache[cache_key] = exists
        
        return exists
    
    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        return self.base.is_file(path)
    
    def is_directory(self, path: Path) -> bool:
        """Check if path is a directory."""
        return self.base.is_directory(path)
    
    def list_directory(self, path: Path) -> list[Path]:
        """List directory contents."""
        return self.base.list_directory(path)
    
    def calculate_sha256(self, path: Path) -> str:
        """Calculate SHA256 hash."""
        return self.base.calculate_sha256(path)


class FileRepositoryError(Exception):
    """Exception raised by file repository operations."""
    pass