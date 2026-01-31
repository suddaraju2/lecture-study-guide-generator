"""
Markdown export for study guides.
"""

from pathlib import Path
from typing import Optional
from ..models import StudyGuide, PracticeQuestion, QuestionType


class MarkdownExporter:
    """Export study guides to Markdown format."""

    @staticmethod
    def export(
        study_guide: StudyGuide,
        output_path: str | Path,
        include_answers: bool = True
    ) -> Path:
        """
        Export complete study guide to Markdown.

        Args:
            study_guide: StudyGuide object to export
            output_path: Path for output file
            include_answers: Whether to include question answers

        Returns:
            Path to created file
        """
        output_path = Path(output_path)
        md = MarkdownExporter._generate_markdown(study_guide, include_answers)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)

        return output_path

    @staticmethod
    def _generate_markdown(guide: StudyGuide, include_answers: bool) -> str:
        """Generate Markdown content from study guide."""
        lines = []

        # Title and metadata
        lines.append(f"# {guide.title}")
        lines.append("")
        lines.append(f"*Generated from: {guide.source_file}*")
        lines.append("")

        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        lines.append("1. [Summary](#summary)")
        lines.append("2. [Key Concepts](#key-concepts)")
        lines.append("3. [Content Overview](#content-overview)")
        lines.append("4. [Practice Questions](#practice-questions)")
        lines.append("5. [Flashcards](#flashcards)")
        if guide.concept_map:
            lines.append("6. [Concept Map](#concept-map)")
        lines.append("7. [Review Priorities](#review-priorities)")
        lines.append("")

        # Summary
        lines.append("---")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(guide.summary)
        lines.append("")

        # Key Concepts
        lines.append("---")
        lines.append("")
        lines.append("## Key Concepts")
        lines.append("")

        for concept in guide.concepts:
            lines.append(f"### {concept.name}")
            lines.append("")
            lines.append(f"**Definition:** {concept.definition}")
            lines.append("")

            if concept.examples:
                lines.append("**Examples:**")
                for ex in concept.examples:
                    lines.append(f"- {ex}")
                lines.append("")

            if concept.related_concepts:
                related = ", ".join(concept.related_concepts)
                lines.append(f"**Related concepts:** {related}")
                lines.append("")

        # Content Overview
        lines.append("---")
        lines.append("")
        lines.append("## Content Overview")
        lines.append("")

        for section in guide.sections:
            if section.title:
                lines.append(f"### {section.title}")
                if section.slide_number:
                    lines.append(f"*Slide {section.slide_number}*")
                lines.append("")

            if section.key_points:
                lines.append("**Key Points:**")
                for point in section.key_points:
                    lines.append(f"- {point}")
                lines.append("")

            # Content density indicator
            if section.content_density >= 0.7:
                lines.append("⚠️ *High content density - review carefully*")
                lines.append("")

        # Practice Questions
        lines.append("---")
        lines.append("")
        lines.append("## Practice Questions")
        lines.append("")

        # Group by type
        by_type: dict[QuestionType, list[PracticeQuestion]] = {}
        for q in guide.practice_questions:
            if q.question_type not in by_type:
                by_type[q.question_type] = []
            by_type[q.question_type].append(q)

        for q_type, questions in by_type.items():
            type_name = q_type.value.replace("_", " ").title()
            lines.append(f"### {type_name}")
            lines.append("")

            for i, q in enumerate(questions, 1):
                lines.append(f"**Q{i}.** {q.question}")
                lines.append("")

                # Multiple choice options
                if q.options:
                    for opt in q.options:
                        lines.append(f"- {opt}")
                    lines.append("")

                if include_answers:
                    lines.append(f"<details>")
                    lines.append(f"<summary>Show Answer</summary>")
                    lines.append("")
                    lines.append(f"**Answer:** {q.answer}")
                    if q.explanation:
                        lines.append("")
                        lines.append(f"**Explanation:** {q.explanation}")
                    lines.append("")
                    lines.append("</details>")
                    lines.append("")

        # Flashcards
        lines.append("---")
        lines.append("")
        lines.append("## Flashcards")
        lines.append("")
        lines.append("*Use these for quick review or export to Anki*")
        lines.append("")

        for i, card in enumerate(guide.flashcards[:20], 1):  # Limit display
            lines.append(f"### Card {i}")
            lines.append("")
            lines.append(f"**Front:** {card.front}")
            lines.append("")
            lines.append("<details>")
            lines.append("<summary>Show Back</summary>")
            lines.append("")
            lines.append(card.back)
            lines.append("")
            lines.append("</details>")
            lines.append("")

        if len(guide.flashcards) > 20:
            lines.append(f"*...and {len(guide.flashcards) - 20} more cards (see exported file)*")
            lines.append("")

        # Concept Map
        if guide.concept_map and guide.concept_map.nodes:
            lines.append("---")
            lines.append("")
            lines.append("## Concept Map")
            lines.append("")
            lines.append("```mermaid")
            lines.append(guide.concept_map.to_mermaid())
            lines.append("```")
            lines.append("")

        # Review Priorities
        lines.append("---")
        lines.append("")
        lines.append("## Review Priorities")
        lines.append("")
        lines.append("Focus your study time on these areas:")
        lines.append("")

        for priority in guide.review_priorities:
            lines.append(f"- [ ] {priority}")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Study guide generated by Lecture Study Guide Generator*")

        return "\n".join(lines)

    @staticmethod
    def export_questions_only(
        questions: list[PracticeQuestion],
        output_path: str | Path,
        include_answers: bool = False
    ) -> Path:
        """Export only practice questions to Markdown."""
        output_path = Path(output_path)
        lines = ["# Practice Questions", ""]

        for i, q in enumerate(questions, 1):
            lines.append(f"## Question {i}")
            lines.append("")
            lines.append(q.question)
            lines.append("")

            if q.options:
                for opt in q.options:
                    lines.append(f"- {opt}")
                lines.append("")

            if include_answers:
                lines.append(f"**Answer:** {q.answer}")
                if q.explanation:
                    lines.append(f"**Explanation:** {q.explanation}")
                lines.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        return output_path
