from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, TypeAdapter


class HighscoreEntry(BaseModel):
    name: str = Field(..., min_length=1)
    score: int = Field(..., ge=0)


class HighscoreManager:
    def __init__(self, file_path: str) -> None:
        self._file_path: Path = Path(file_path)
        self._scores: List[HighscoreEntry] = []
        self.load_scores()

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
        sorted_scores = sorted(
            self._scores, key=lambda entry: entry.score, reverse=True
        )
        return sorted_scores[:amount]

    def load_scores(self) -> None:
        if not self._file_path.exists():
            self._scores = []
            return
        if self._file_path.is_dir():
            raise ValueError("Highscore path points to a directory.")

        raw_data = self._file_path.read_bytes()
        adapter = TypeAdapter(list[HighscoreEntry])
        self._scores = list(adapter.validate_json(raw_data))
        # self._scores = self.get_top_scores(10)
        # for entry in adapter.validate_json(raw_data):
        #    self.add_entry(entry)

    def save_scores(self) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        adapter = TypeAdapter(list[HighscoreEntry])
        json_bytes = adapter.dump_json(self._scores, indent=4)
        self._file_path.write_bytes(json_bytes)
