"""
AI-powered study guide generator.
"""

from typing import Optional
from ..models import StudyGuide, ContentSection, Concept, Difficulty
from ..extractors.base import ExtractedContent
from .base import BaseGenerator, AIProvider


class StudyGuideGeneratorAI(BaseGenerator):
    """Generate comprehensive study guides from lecture content."""

    SYSTEM_PROMPT = """You are an expert educational content analyst. Your job is to analyze
lecture content and extract the most important information for studying.

Focus on:
1. Identifying key concepts and their definitions
2. Finding relationships between concepts
3. Highlighting important examples
4. Noting areas that require more attention based on content density

Be thorough but concise. Prioritize clarity over completeness."""

    def generate(
        self,
        extracted_content: ExtractedContent,
        focus_topics: Optional[list[str]] = None
    ) -> StudyGuide:
        """
        Generate a complete study guide from extracted content.

        Args:
            extracted_content: Content extracted from lecture materials
            focus_topics: Optional list of topics to prioritize

        Returns:
            StudyGuide object with all components
        """
        # Generate summary and sections
        sections = self._generate_sections(extracted_content)
        summary = self._generate_summary(extracted_content)
        concepts = self._generate_concepts(extracted_content)
        priorities = self._identify_review_priorities(extracted_content, concepts)

        # Determine title
        title = (
            extracted_content.metadata.get("title") or
            extracted_content.slides[0].get("title", "Lecture Study Guide")
            if extracted_content.slides else "Lecture Study Guide"
        )

        return StudyGuide(
            title=title,
            source_file=extracted_content.source_file,
            summary=summary,
            sections=sections,
            concepts=concepts,
            review_priorities=priorities
        )

    def _generate_summary(self, content: ExtractedContent) -> str:
        """Generate an executive summary of the lecture."""
        prompt = f"""Analyze this lecture content and provide a concise summary (2-3 paragraphs)
that captures the main topics, key takeaways, and learning objectives.

LECTURE CONTENT:
{content.get_all_text()[:8000]}

Provide a clear, student-friendly summary:"""

        return self.ai.generate(prompt, self.SYSTEM_PROMPT, max_tokens=1000)

    def _generate_sections(self, content: ExtractedContent) -> list[ContentSection]:
        """Generate organized content sections from slides."""
        sections = []

        for slide in content.slides:
            # Calculate content density (simple heuristic)
            text_length = len(slide.get("content", ""))
            has_table = slide.get("has_table", False)
            has_image = slide.get("has_image", False)

            # Higher density = more content to study
            density = min(1.0, text_length / 500)
            if has_table:
                density = min(1.0, density + 0.2)
            if has_image:
                density = min(1.0, density + 0.1)

            # Extract key points using AI for content-heavy slides
            key_points = []
            if text_length > 100:
                key_points = self._extract_key_points(slide.get("content", ""))

            section = ContentSection(
                title=slide.get("title", f"Slide {slide.get('number', '?')}"),
                content=slide.get("content", ""),
                slide_number=slide.get("number"),
                key_points=key_points,
                content_density=density
            )
            sections.append(section)

        return sections

    def _extract_key_points(self, content: str) -> list[str]:
        """Extract key points from slide content."""
        if len(content) < 50:
            return []

        prompt = f"""Extract 2-4 key points from this slide content.
Be concise - each point should be one sentence.

CONTENT:
{content[:2000]}

Return as a JSON array of strings:"""

        try:
            result = self.ai.generate_json(prompt, max_tokens=500)
            if isinstance(result, list):
                return result[:4]
        except (Exception,):
            pass

        return []

    def _generate_concepts(self, content: ExtractedContent) -> list[Concept]:
        """Extract key concepts and definitions."""
        prompt = f"""Analyze this lecture and identify the key concepts that students need to learn.

LECTURE CONTENT:
{content.get_all_text()[:10000]}

For each concept, provide:
1. Name - the concept/term name
2. Definition - clear, concise definition
3. Related concepts - other concepts it connects to
4. Examples - if mentioned in the lecture

Return as JSON array with objects having keys: name, definition, related_concepts (array), examples (array)

Extract 5-15 key concepts:"""

        try:
            result = self.ai.generate_json(prompt, max_tokens=3000)
            concepts = []

            if isinstance(result, list):
                for item in result:
                    concept = Concept(
                        name=item.get("name", ""),
                        definition=item.get("definition", ""),
                        related_concepts=item.get("related_concepts", []),
                        examples=item.get("examples", []),
                        importance=self._assess_importance(item.get("definition", ""))
                    )
                    concepts.append(concept)

            return concepts
        except Exception as e:
            print(f"Warning: Could not extract concepts: {e}")
            return []

    def _assess_importance(self, definition: str) -> Difficulty:
        """Assess importance based on definition complexity."""
        length = len(definition)
        if length > 200:
            return Difficulty.HARD
        elif length > 100:
            return Difficulty.MEDIUM
        return Difficulty.EASY

    def _identify_review_priorities(
        self,
        content: ExtractedContent,
        concepts: list[Concept]
    ) -> list[str]:
        """Identify areas that need more study attention."""
        priorities = []

        # High-density slides need attention
        for slide in content.slides:
            content_text = slide.get("content", "")
            if len(content_text) > 300:
                title = slide.get("title", f"Slide {slide.get('number')}")
                priorities.append(f"Review {title} - high content density")

        # Complex concepts need attention
        for concept in concepts:
            if concept.importance == Difficulty.HARD:
                priorities.append(f"Master concept: {concept.name}")

        # Slides with tables often have important data
        for slide in content.slides:
            if slide.get("has_table"):
                title = slide.get("title", f"Slide {slide.get('number')}")
                priorities.append(f"Study tables in {title}")

        return priorities[:10]  # Limit to top 10
