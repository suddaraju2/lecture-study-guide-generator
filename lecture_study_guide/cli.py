"""
Command-line interface for Lecture Study Guide Generator.
"""

import argparse
import sys
from pathlib import Path

from .core import StudyGuideGenerator
from .models import QuestionType


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive study guides from lecture materials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate study guide from PowerPoint
  lecture-study-guide lecture.pptx -o output/

  # Generate from PDF with custom question count
  lecture-study-guide slides.pdf -o output/ --questions 30

  # Use OpenAI instead of Anthropic
  lecture-study-guide lecture.pptx -o output/ --provider openai

Environment Variables:
  ANTHROPIC_API_KEY  - API key for Anthropic (Claude)
  OPENAI_API_KEY     - API key for OpenAI (GPT)
        """
    )

    parser.add_argument(
        "input",
        type=str,
        help="Input lecture file (.pptx, .pdf)"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output",
        help="Output directory (default: output/)"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="AI API key (or set ANTHROPIC_API_KEY/OPENAI_API_KEY env var)"
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["anthropic", "openai"],
        default="anthropic",
        help="AI provider (default: anthropic)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Specific model to use (optional)"
    )

    parser.add_argument(
        "--questions",
        type=int,
        default=20,
        help="Number of practice questions (default: 20)"
    )

    parser.add_argument(
        "--flashcards",
        type=int,
        default=30,
        help="Number of flashcards (default: 30)"
    )

    parser.add_argument(
        "--formats",
        type=str,
        nargs="+",
        choices=["markdown", "json", "anki_txt", "anki_csv"],
        default=None,
        help="Export formats (default: all)"
    )

    parser.add_argument(
        "--question-types",
        type=str,
        nargs="+",
        choices=["multiple_choice", "short_answer", "true_false", "fill_in_blank", "essay"],
        default=None,
        help="Types of questions to generate (default: all)"
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Parse question types
    question_types = None
    if args.question_types:
        question_types = [QuestionType(qt) for qt in args.question_types]

    try:
        print(f"\n{'='*60}")
        print("  LECTURE STUDY GUIDE GENERATOR")
        print(f"{'='*60}\n")

        # Initialize generator
        generator = StudyGuideGenerator(
            api_key=args.api_key,
            provider=args.provider,
            model=args.model
        )

        # Generate study guide
        study_guide = generator.generate(
            input_path,
            num_questions=args.questions,
            num_flashcards=args.flashcards,
            question_types=question_types
        )

        # Export
        print(f"\n📁 Exporting to {args.output}/...")
        outputs = generator.export_all(
            study_guide,
            args.output,
            formats=args.formats
        )

        print(f"\n{'='*60}")
        print("  GENERATION COMPLETE!")
        print(f"{'='*60}")
        print(f"\n📊 Summary:")
        print(f"   • Title: {study_guide.title}")
        print(f"   • Sections: {len(study_guide.sections)}")
        print(f"   • Concepts: {len(study_guide.concepts)}")
        print(f"   • Practice Questions: {len(study_guide.practice_questions)}")
        print(f"   • Flashcards: {len(study_guide.flashcards)}")
        print(f"   • Concept Map Nodes: {len(study_guide.concept_map.nodes) if study_guide.concept_map else 0}")
        print(f"\n📂 Output files:")
        for fmt, path in outputs.items():
            print(f"   • {path}")
        print()

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
