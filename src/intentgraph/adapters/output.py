"""Output formatting and validation."""

import json
import logging
from pathlib import Path
from types import MappingProxyType
from typing import Any
from uuid import UUID

import orjson

from ..domain.models import AnalysisResult

logger = logging.getLogger(__name__)


class OutputFormatter:
    """Formats and validates analysis results for output."""

    def __init__(self, schema_path: Path | None = None):
        self.schema_path = schema_path
        self._schema: dict[str, Any] | None = None

        if schema_path and schema_path.exists():
            try:
                self._schema = json.loads(schema_path.read_text())
            except Exception as e:
                logger.warning(f"Failed to load schema from {schema_path}: {e}")

    def format_json(self, result: AnalysisResult, pretty: bool = True) -> str:
        """Format analysis result as JSON."""
        try:
            # Validate with pydantic
            result_dict = result.dict()

            # Convert paths and UUIDs to strings
            converted_dict = self._convert_types(result_dict)

            # Format with orjson
            if pretty:
                return orjson.dumps(
                    converted_dict,
                    option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
                ).decode('utf-8')
            else:
                return orjson.dumps(converted_dict).decode('utf-8')

        except Exception as e:
            logger.error(f"Failed to format JSON output: {e}")
            raise

    def _convert_types(self, obj: Any, seen: set = None) -> Any:
        """Convert complex types to JSON-serializable formats."""
        if seen is None:
            seen = set()

        # Prevent recursion by tracking object ids
        obj_id = id(obj)
        if obj_id in seen:
            return str(obj)  # Fallback to string representation

        if isinstance(obj, (dict, MappingProxyType)):
            seen.add(obj_id)
            try:
                return {str(key): self._convert_types(value, seen) for key, value in obj.items()}
            finally:
                seen.remove(obj_id)
        elif isinstance(obj, list):
            return [self._convert_types(item, seen) for item in obj]
        elif isinstance(obj, Path) or isinstance(obj, UUID):
            return str(obj)
        elif hasattr(obj, '__dict__') and not isinstance(obj, type(lambda: None)):
            # Skip function types and Mock objects
            if 'Mock' in str(type(obj)):
                return str(obj)
            seen.add(obj_id)
            try:
                return self._convert_types(obj.__dict__, seen)
            finally:
                seen.remove(obj_id)
        else:
            # Handle any other complex types by converting to string
            try:
                # Test if it's JSON serializable
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)

    def validate_against_schema(self, result: AnalysisResult) -> bool:
        """Validate result against JSON schema."""
        if not self._schema:
            logger.warning("No schema available for validation")
            return True

        try:
            import jsonschema

            result_dict = result.dict()
            converted_dict = self._convert_types(result_dict)

            jsonschema.validate(converted_dict, self._schema)
            return True

        except ImportError:
            logger.warning("jsonschema not available, skipping validation")
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    def export_to_file(self, result: AnalysisResult, output_path: Path, pretty: bool = True) -> None:
        """Export result to file."""
        try:
            json_output = self.format_json(result, pretty)
            output_path.write_text(json_output, encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to export to {output_path}: {e}")
            raise
