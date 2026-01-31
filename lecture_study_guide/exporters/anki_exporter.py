"""
Anki flashcard export functionality.
"""

import csv
import json
from pathlib import Path
from typing import Optional
from ..models import Flashcard, StudyGuide


class AnkiExporter:
    """Export flashcards to Anki-compatible formats."""

    @staticmethod
    def export_txt(
        flashcards: list[Flashcard],
        output_path: str | Path,
        include_tags: bool = True
    ) -> Path:
        """
        Export flashcards to Anki-importable text format.

        Format: Front<tab>Back<tab>Tags

        Args:
            flashcards: List of flashcards to export
            output_path: Path for output file
            include_tags: Whether to include tags column

        Returns:
            Path to created file
        """
        output_path = Path(output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            for card in flashcards:
                # Escape newlines for Anki
                front = card.front.replace('\n', '<br>')
                back = card.back.replace('\n', '<br>')

                if include_tags and card.tags:
                    tags = ' '.join(card.tags)
                    f.write(f"{front}\t{back}\t{tags}\n")
                else:
                    f.write(f"{front}\t{back}\n")

        return output_path

    @staticmethod
    def export_csv(
        flashcards: list[Flashcard],
        output_path: str | Path,
        include_metadata: bool = True
    ) -> Path:
        """
        Export flashcards to CSV format for Anki import.

        Args:
            flashcards: List of flashcards to export
            output_path: Path for output file
            include_metadata: Include extra columns (tags, difficulty)

        Returns:
            Path to created file
        """
        output_path = Path(output_path)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if include_metadata:
                writer = csv.writer(f)
                writer.writerow(['Front', 'Back', 'Tags', 'Difficulty'])

                for card in flashcards:
                    writer.writerow([
                        card.front,
                        card.back,
                        ' '.join(card.tags),
                        card.difficulty.value
                    ])
            else:
                writer = csv.writer(f)
                for card in flashcards:
                    writer.writerow([card.front, card.back])

        return output_path

    @staticmethod
    def export_apkg_deck_json(
        flashcards: list[Flashcard],
        output_path: str | Path,
        deck_name: str = "Lecture Study Guide"
    ) -> Path:
        """
        Export flashcards as JSON for use with genanki or similar tools.

        This creates a JSON file that can be used with the genanki library
        to create an actual .apkg file.

        Args:
            flashcards: List of flashcards to export
            output_path: Path for output file
            deck_name: Name of the Anki deck

        Returns:
            Path to created file
        """
        output_path = Path(output_path)

        deck_data = {
            "deck_name": deck_name,
            "cards": [
                {
                    "front": card.front,
                    "back": card.back,
                    "tags": card.tags,
                    "difficulty": card.difficulty.value,
                    "source_slide": card.source_slide
                }
                for card in flashcards
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(deck_data, f, indent=2, ensure_ascii=False)

        return output_path

    @staticmethod
    def generate_apkg(
        flashcards: list[Flashcard],
        output_path: str | Path,
        deck_name: str = "Lecture Study Guide"
    ) -> Optional[Path]:
        """
        Generate actual Anki .apkg file using genanki.

        Requires genanki to be installed.

        Args:
            flashcards: List of flashcards to export
            output_path: Path for output file (should end in .apkg)
            deck_name: Name of the Anki deck

        Returns:
            Path to created file, or None if genanki not available
        """
        try:
            import genanki
            import random
        except ImportError:
            print("genanki not installed. Install with: pip install genanki")
            print("Falling back to JSON export.")
            return None

        output_path = Path(output_path)

        # Create a unique model ID and deck ID
        model_id = random.randrange(1 << 30, 1 << 31)
        deck_id = random.randrange(1 << 30, 1 << 31)

        # Define the card model
        model = genanki.Model(
            model_id,
            'Study Guide Card',
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
                },
            ],
            css='''
            .card {
                font-family: arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
            }
            '''
        )

        # Create the deck
        deck = genanki.Deck(deck_id, deck_name)

        # Add cards
        for card in flashcards:
            note = genanki.Note(
                model=model,
                fields=[card.front, card.back],
                tags=card.tags
            )
            deck.add_note(note)

        # Create the package
        package = genanki.Package(deck)
        package.write_to_file(str(output_path))

        return output_path


def create_anki_import_instructions() -> str:
    """Return instructions for importing flashcards into Anki."""
    return """
# How to Import Flashcards into Anki

## For .txt or .csv files:

1. Open Anki
2. Click "File" > "Import"
3. Select the exported file
4. Configure import settings:
   - Field separator: Tab (for .txt) or Comma (for .csv)
   - Allow HTML in fields: Yes
   - Field mapping:
     - Field 1 -> Front
     - Field 2 -> Back
     - Field 3 -> Tags (optional)
5. Click "Import"

## For .apkg files:

1. Open Anki
2. Click "File" > "Import"
3. Select the .apkg file
4. Click "Import"
5. The deck will appear in your deck list

## Tips:

- Review new cards daily for best retention
- Use the built-in spaced repetition algorithm
- Add your own notes or mnemonics as you study
"""
