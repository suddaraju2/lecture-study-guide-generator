"""
AI-powered flashcard generator.
"""

from typing import Optional
from ..models import Flashcard, Concept, Difficulty
from ..extractors.base import ExtractedContent
from .base import BaseGenerator, AIProvider


class FlashcardGenerator(BaseGenerator):
    """Generate flashcards for spaced repetition study."""

    SYSTEM_PROMPT = """You are an expert at creating effective flashcards for learning.
Create flashcards that:
1. Have clear, concise questions on the front
2. Have complete but focused answers on the back
3. Test one concept at a time
4. Use active recall principles

Make cards that are effective for spaced repetition systems like Anki."""

    def generate(
        self,
        extracted_content: ExtractedContent,
        concepts: Optional[list[Concept]] = None,
        num_cards: int = 30
    ) -> list[Flashcard]:
        """
        Generate flashcards from content.

        Args:
            extracted_content: Content extracted from lecture
            concepts: Pre-extracted concepts (optional)
            num_cards: Target number of flashcards

        Returns:
            List of Flashcard objects
        """
        flashcards = []

        # Generate from concepts if provided
        if concepts:
            concept_cards = self._generate_from_concepts(concepts)
            flashcards.extend(concept_cards)

        # Generate additional cards from content
        if len(flashcards) < num_cards:
            remaining = num_cards - len(flashcards)
            content_cards = self._generate_from_content(extracted_content, remaining)
            flashcards.extend(content_cards)

        return flashcards[:num_cards]

    def _generate_from_concepts(self, concepts: list[Concept]) -> list[Flashcard]:
        """Create flashcards directly from extracted concepts."""
        flashcards = []

        for concept in concepts:
            # Basic definition card
            card = Flashcard(
                front=f"What is {concept.name}?",
                back=concept.definition,
                tags=["concept", "definition"],
                difficulty=concept.importance
            )
            flashcards.append(card)

            # Example cards
            for i, example in enumerate(concept.examples[:2]):
                card = Flashcard(
                    front=f"Give an example of {concept.name}:",
                    back=example,
                    tags=["concept", "example"],
                    difficulty=Difficulty.MEDIUM
                )
                flashcards.append(card)

            # Relationship cards
            if concept.related_concepts:
                related = ", ".join(concept.related_concepts[:3])
                card = Flashcard(
                    front=f"What concepts are related to {concept.name}?",
                    back=related,
                    tags=["concept", "relationships"],
                    difficulty=Difficulty.HARD
                )
                flashcards.append(card)

        return flashcards

    def _generate_from_content(
        self,
        content: ExtractedContent,
        count: int
    ) -> list[Flashcard]:
        """Generate flashcards using AI from raw content."""
        prompt = f"""Create {count} flashcards from this lecture content.

LECTURE CONTENT:
{content.get_all_text()[:10000]}

For each flashcard, provide:
- front: Question or prompt (clear, specific)
- back: Answer (complete but concise)
- tags: Array of relevant tags
- difficulty: easy, medium, or hard

Focus on:
1. Key terms and definitions
2. Important facts and figures
3. Processes and procedures
4. Comparisons and contrasts

Return as JSON array:"""

        try:
            result = self.ai.generate_json(prompt, self.SYSTEM_PROMPT, max_tokens=4000)
            return self._parse_flashcards(result)
        except Exception as e:
            print(f"Warning: Could not generate flashcards: {e}")
            return []

    def _parse_flashcards(self, result: list | dict) -> list[Flashcard]:
        """Parse AI response into Flashcard objects."""
        flashcards = []

        if isinstance(result, dict):
            result = result.get("flashcards", [result])

        for item in result:
            if not isinstance(item, dict):
                continue

            difficulty = self._parse_difficulty(item.get("difficulty", "medium"))
            tags = item.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]

            card = Flashcard(
                front=item.get("front", ""),
                back=item.get("back", ""),
                tags=tags,
                difficulty=difficulty
            )
            flashcards.append(card)

        return flashcards

    def _parse_difficulty(self, diff_str: str) -> Difficulty:
        """Parse difficulty string to enum."""
        diff_str = str(diff_str).lower()
        if "easy" in diff_str:
            return Difficulty.EASY
        elif "hard" in diff_str:
            return Difficulty.HARD
        return Difficulty.MEDIUM
