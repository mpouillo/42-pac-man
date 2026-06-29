from pathlib import Path
from pydantic import BaseModel, Field, TypeAdapter


class HighscoreEntry(BaseModel):
    """Represent a single validated player highscore record."""

    name: str = Field(..., min_length=1, max_length=10)
    score: int = Field(..., ge=0)


class HighscoreManager:
    """Manage persistence, retrieval, and modification of highscores."""

    def __init__(self, file_path: str) -> None:
        """Initialize the manager path and pull stored scores from disk."""
        self._file_path: Path = Path(file_path)
        self._scores: list[HighscoreEntry] = []
        self.load_scores()

    def __str__(self) -> str:
        """Return a scannable string representation of stored scores."""
        return str(self._scores)

    def add_entry(self, entry: HighscoreEntry) -> None:
        """Append a new highscore entry to the tracked list."""
        self._scores.append(entry)

    def remove_entry(self, entry: HighscoreEntry) -> bool:
        """Remove a specific highscore entry from the tracked list."""
        try:
            self._scores.remove(entry)
            return True
        except ValueError:
            return False

    def get_top_scores(self, amount: int) -> list[HighscoreEntry]:
        """Return a sorted slice of the highest scoring records."""
        sorted_scores = sorted(
            self._scores, key=lambda entry: entry.score, reverse=True
        )
        return sorted_scores[:amount]

    def load_scores(self) -> None:
        """Load and parse highscore entries from the local file."""
        if not self._file_path.exists():
            self._scores = []
            return
        if self._file_path.is_dir():
            raise ValueError("Highscore path points to a directory.")

        try:
            raw_data = self._file_path.read_bytes()
            if not raw_data.strip():
                self._scores = []
                return
            adapter = TypeAdapter(list[HighscoreEntry])
            self._scores = list(adapter.validate_json(raw_data))
        except Exception:
            self._scores = []

    def save_scores(self) -> None:
        """Serialize and save current highscore records to disk."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        adapter = TypeAdapter(list[HighscoreEntry])
        json_bytes = adapter.dump_json(self._scores, indent=4)
        self._file_path.write_bytes(json_bytes)
