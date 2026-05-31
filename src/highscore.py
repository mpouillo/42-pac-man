from pathlib import Path
from typing import List

from pydantic import TypeAdapter

from protocols import HighscoreEntry


class HighscoreManager:
    def __init__(self) -> None:
        self._scores: List[HighscoreEntry] = []

    def __str__(self) -> str:
        return str(self._scores)

    def add_entry(self, entry: HighscoreEntry) -> None:
        """Add an entry to highscores."""
        self._scores.append(entry)

    def remove_entry(self, entry: HighscoreEntry) -> bool:
        """
        Attempt to remove an entry from highscores.
        Return False if entry is not in saved highscores, else True.
        """
        if entry not in self._scores:
            return False

        idx = self._scores.index(entry)
        self._scores.pop(idx)
        return True

    def get_top_scores(self, amount: int) -> List[HighscoreEntry]:
        """Fetch and return top score HighscoreEntry."""
        scores = self._scores[:]
        top_scores = []
        for _ in range(amount):
            top_score = max(scores, key=lambda entry: entry.score)
            top_scores.append(top_score)
            idx = scores.index(top_score)
            scores.pop(idx)

        return top_scores

    def load_scores(self, file_path: Path) -> None:
        if not file_path.exists() or file_path.is_dir():
            raise ValueError("File does not exist.")

        raw_data = file_path.read_bytes()
        adapter = TypeAdapter(list[HighscoreEntry])
        for entry in adapter.validate_json(raw_data):
            self.add_entry(entry)

    def save_scores(self, file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        adapter = TypeAdapter(list[HighscoreEntry])
        json_bytes = adapter.dump_json(self._scores, indent=4)
        file_path.write_bytes(json_bytes)
