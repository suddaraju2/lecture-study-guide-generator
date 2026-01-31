"""
JSON export for study guides.
"""

import json
from pathlib import Path
from typing import Any
from ..models import StudyGuide


class JSONExporter:
    """Export study guides to JSON format."""

    @staticmethod
    def export(
        study_guide: StudyGuide,
        output_path: str | Path,
        pretty: bool = True
    ) -> Path:
        """
        Export complete study guide to JSON.

        Args:
            study_guide: StudyGuide object to export
            output_path: Path for output file
            pretty: Whether to format with indentation

        Returns:
            Path to created file
        """
        output_path = Path(output_path)

        data = study_guide.to_dict()

        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)

        return output_path

    @staticmethod
    def load(input_path: str | Path) -> dict[str, Any]:
        """
        Load study guide data from JSON.

        Args:
            input_path: Path to JSON file

        Returns:
            Dictionary with study guide data
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
