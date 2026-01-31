"""
Main StudyGuideGenerator class - the primary interface for the library.
"""

import os
from pathlib import Path
from typing import Optional

from .models import StudyGuide, Flashcard, PracticeQuestion, ConceptMap, QuestionType
from .extractors import PowerPointExtractor, PDFExtractor
from .extractors.base import ExtractedContent
from .generators.base import AIProvider
from .generators import (
    StudyGuideGeneratorAI,
    QuestionGenerator,
    FlashcardGenerator,
    ConceptMapGenerator
)
from .exporters import AnkiExporter, MarkdownExporter, JSONExporter


class StudyGuideGenerator:
    """
    Main class for generating study guides from lecture materials.

    Usage:
        generator = StudyGuideGenerator(api_key="your-api-key")
        guide = generator.generate("lecture.pptx")
        guide.export_all("output/")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "anthropic",
        model: Optional[str] = None
    ):
        """
        Initialize the study guide generator.

        Args:
            api_key: API key for AI provider (or set ANTHROPIC_API_KEY/OPENAI_API_KEY env var)
            provider: AI provider - 'anthropic' or 'openai'
            model: Specific model to use (defaults based on provider)
        """
        self.ai_provider = AIProvider(api_key=api_key, provider=provider, model=model)

        # Initialize generators
        self._study_guide_gen = StudyGuideGeneratorAI(self.ai_provider)
        self._question_gen = QuestionGenerator(self.ai_provider)
        self._flashcard_gen = FlashcardGenerator(self.ai_provider)
        self._concept_map_gen = ConceptMapGenerator(self.ai_provider)

    def generate(
        self,
        input_path: str | Path,
        num_questions: int = 20,
        num_flashcards: int = 30,
        question_types: Optional[list[QuestionType]] = None
    ) -> StudyGuide:
        """
        Generate a complete study guide from lecture materials.

        Args:
            input_path: Path to lecture file (.pptx, .pdf)
            num_questions: Number of practice questions to generate
            num_flashcards: Number of flashcards to generate
            question_types: Types of questions (defaults to all types)

        Returns:
            Complete StudyGuide object with all components
        """
        input_path = Path(input_path)

        # Extract content from file
        print(f"📚 Extracting content from {input_path.name}...")
        extracted = self._extract_content(input_path)
        print(f"   Found {extracted.slide_count} slides/pages")

        # Generate base study guide (summary, sections, concepts)
        print("📝 Generating study guide...")
        study_guide = self._study_guide_gen.generate(extracted)

        # Generate practice questions
        print(f"❓ Generating {num_questions} practice questions...")
        questions = self._question_gen.generate(
            extracted,
            num_questions=num_questions,
            question_types=question_types
        )
        study_guide.practice_questions = questions

        # Generate flashcards
        print(f"🗂️  Generating {num_flashcards} flashcards...")
        flashcards = self._flashcard_gen.generate(
            extracted,
            concepts=study_guide.concepts,
            num_cards=num_flashcards
        )
        study_guide.flashcards = flashcards

        # Generate concept map
        print("🗺️  Generating concept map...")
        concept_map = self._concept_map_gen.generate(
            extracted,
            concepts=study_guide.concepts
        )
        study_guide.concept_map = concept_map

        print("✅ Study guide generation complete!")
        return study_guide

    def _extract_content(self, input_path: Path) -> ExtractedContent:
        """Extract content using appropriate extractor."""
        ext = input_path.suffix.lower()

        if ext in [".pptx", ".ppt"]:
            extractor = PowerPointExtractor(input_path)
        elif ext == ".pdf":
            extractor = PDFExtractor(input_path)
        else:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                "Supported formats: .pptx, .ppt, .pdf"
            )

        return extractor.extract()

    def export_all(
        self,
        study_guide: StudyGuide,
        output_dir: str | Path,
        formats: Optional[list[str]] = None
    ) -> dict[str, Path]:
        """
        Export study guide to multiple formats.

        Args:
            study_guide: Generated study guide
            output_dir: Output directory
            formats: List of formats ('markdown', 'json', 'anki_txt', 'anki_csv')
                    Defaults to all formats

        Returns:
            Dictionary mapping format names to output paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if formats is None:
            formats = ['markdown', 'json', 'anki_txt', 'anki_csv']

        outputs = {}
        base_name = Path(study_guide.source_file).stem

        if 'markdown' in formats:
            path = output_dir / f"{base_name}_study_guide.md"
            MarkdownExporter.export(study_guide, path)
            outputs['markdown'] = path
            print(f"📄 Exported Markdown: {path}")

        if 'json' in formats:
            path = output_dir / f"{base_name}_study_guide.json"
            JSONExporter.export(study_guide, path)
            outputs['json'] = path
            print(f"📋 Exported JSON: {path}")

        if 'anki_txt' in formats and study_guide.flashcards:
            path = output_dir / f"{base_name}_flashcards.txt"
            AnkiExporter.export_txt(study_guide.flashcards, path)
            outputs['anki_txt'] = path
            print(f"🗂️  Exported Anki TXT: {path}")

        if 'anki_csv' in formats and study_guide.flashcards:
            path = output_dir / f"{base_name}_flashcards.csv"
            AnkiExporter.export_csv(study_guide.flashcards, path)
            outputs['anki_csv'] = path
            print(f"📊 Exported Anki CSV: {path}")

        return outputs


def generate_study_guide(
    input_path: str,
    output_dir: str = "output",
    api_key: Optional[str] = None,
    provider: str = "anthropic",
    num_questions: int = 20,
    num_flashcards: int = 30
) -> StudyGuide:
    """
    Convenience function to generate and export a study guide.

    Args:
        input_path: Path to lecture file
        output_dir: Output directory for exports
        api_key: AI API key
        provider: 'anthropic' or 'openai'
        num_questions: Number of practice questions
        num_flashcards: Number of flashcards

    Returns:
        Generated StudyGuide object
    """
    generator = StudyGuideGenerator(api_key=api_key, provider=provider)
    study_guide = generator.generate(
        input_path,
        num_questions=num_questions,
        num_flashcards=num_flashcards
    )

    generator.export_all(study_guide, output_dir)

    return study_guide
