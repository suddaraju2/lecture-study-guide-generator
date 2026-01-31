"""
AI-powered practice question generator.
"""

from typing import Optional
from ..models import PracticeQuestion, QuestionType, Difficulty
from ..extractors.base import ExtractedContent
from .base import BaseGenerator, AIProvider


class QuestionGenerator(BaseGenerator):
    """Generate practice questions from lecture content."""

    SYSTEM_PROMPT = """You are an expert educator creating practice questions for students.
Create questions that:
1. Test understanding, not just memorization
2. Cover key concepts thoroughly
3. Vary in difficulty and type
4. Include clear, educational explanations for answers

Focus on creating questions that help students truly learn the material."""

    def generate(
        self,
        extracted_content: ExtractedContent,
        num_questions: int = 20,
        question_types: Optional[list[QuestionType]] = None
    ) -> list[PracticeQuestion]:
        """
        Generate practice questions from content.

        Args:
            extracted_content: Content extracted from lecture
            num_questions: Number of questions to generate
            question_types: Types of questions to include (defaults to all)

        Returns:
            List of PracticeQuestion objects
        """
        if question_types is None:
            question_types = list(QuestionType)

        questions = []

        # Generate different types of questions
        for q_type in question_types:
            type_count = num_questions // len(question_types)
            type_questions = self._generate_questions_of_type(
                extracted_content, q_type, type_count
            )
            questions.extend(type_questions)

        return questions[:num_questions]

    def _generate_questions_of_type(
        self,
        content: ExtractedContent,
        question_type: QuestionType,
        count: int
    ) -> list[PracticeQuestion]:
        """Generate questions of a specific type."""
        type_prompts = {
            QuestionType.MULTIPLE_CHOICE: self._get_mc_prompt,
            QuestionType.SHORT_ANSWER: self._get_sa_prompt,
            QuestionType.TRUE_FALSE: self._get_tf_prompt,
            QuestionType.FILL_IN_BLANK: self._get_fib_prompt,
            QuestionType.ESSAY: self._get_essay_prompt,
        }

        prompt_fn = type_prompts.get(question_type, self._get_sa_prompt)
        prompt = prompt_fn(content, count)

        try:
            result = self.ai.generate_json(prompt, self.SYSTEM_PROMPT, max_tokens=4000)
            return self._parse_questions(result, question_type)
        except Exception as e:
            print(f"Warning: Could not generate {question_type.value} questions: {e}")
            return []

    def _get_mc_prompt(self, content: ExtractedContent, count: int) -> str:
        return f"""Create {count} multiple choice questions based on this lecture content.

LECTURE CONTENT:
{content.get_all_text()[:8000]}

For each question, provide:
- question: The question text
- options: Array of 4 options (A, B, C, D)
- answer: The correct option letter
- explanation: Why this answer is correct
- difficulty: easy, medium, or hard
- topic: The topic this question covers

Return as JSON array:"""

    def _get_sa_prompt(self, content: ExtractedContent, count: int) -> str:
        return f"""Create {count} short answer questions based on this lecture content.

LECTURE CONTENT:
{content.get_all_text()[:8000]}

For each question, provide:
- question: The question text
- answer: A model answer (2-3 sentences)
- explanation: Additional context or what to look for
- difficulty: easy, medium, or hard
- topic: The topic this question covers

Return as JSON array:"""

    def _get_tf_prompt(self, content: ExtractedContent, count: int) -> str:
        return f"""Create {count} true/false questions based on this lecture content.

LECTURE CONTENT:
{content.get_all_text()[:8000]}

For each question, provide:
- question: A statement to evaluate as true or false
- answer: "True" or "False"
- explanation: Why it's true or false
- difficulty: easy, medium, or hard
- topic: The topic this question covers

Return as JSON array:"""

    def _get_fib_prompt(self, content: ExtractedContent, count: int) -> str:
        return f"""Create {count} fill-in-the-blank questions based on this lecture content.

LECTURE CONTENT:
{content.get_all_text()[:8000]}

For each question, provide:
- question: A sentence with _____ for the blank
- answer: The word/phrase that fills the blank
- explanation: Context for understanding
- difficulty: easy, medium, or hard
- topic: The topic this question covers

Return as JSON array:"""

    def _get_essay_prompt(self, content: ExtractedContent, count: int) -> str:
        return f"""Create {count} essay/discussion questions based on this lecture content.

LECTURE CONTENT:
{content.get_all_text()[:8000]}

For each question, provide:
- question: An open-ended question requiring detailed response
- answer: Key points that should be covered in a good answer
- explanation: Guidance on what makes a strong response
- difficulty: easy, medium, or hard
- topic: The topic this question covers

Return as JSON array:"""

    def _parse_questions(
        self,
        result: list | dict,
        question_type: QuestionType
    ) -> list[PracticeQuestion]:
        """Parse AI response into PracticeQuestion objects."""
        questions = []

        if isinstance(result, dict):
            result = result.get("questions", [result])

        for item in result:
            if not isinstance(item, dict):
                continue

            difficulty = self._parse_difficulty(item.get("difficulty", "medium"))

            question = PracticeQuestion(
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                question_type=question_type,
                options=item.get("options", []),
                explanation=item.get("explanation", ""),
                difficulty=difficulty,
                topic=item.get("topic", "")
            )
            questions.append(question)

        return questions

    def _parse_difficulty(self, diff_str: str) -> Difficulty:
        """Parse difficulty string to enum."""
        diff_str = diff_str.lower()
        if "easy" in diff_str:
            return Difficulty.EASY
        elif "hard" in diff_str:
            return Difficulty.HARD
        return Difficulty.MEDIUM
