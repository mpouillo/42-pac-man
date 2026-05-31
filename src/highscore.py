from collections import defaultdict
from typing import Dict, List

from protocols import HighscoreEntry


class HighscoreManager:
    def __init__(self) -> None:
        self._scores: Dict[str, List[int]] = defaultdict(list)

    def __str__(self) -> str:
        return str(self._scores)

    def add_entry(self, entry: HighscoreEntry) -> None:
        """Add an entry to highscores."""
        self._scores[entry.name].append(entry.score)

    def remove_entry(self, entry: HighscoreEntry) -> bool:
        """
        Attempt to remove an entry from highscores.
        Return False if entry is not in saved highscores, else True.
        """
        if (
            entry.name not in self._scores
            or entry.score not in self._scores[entry.name]
        ):
            return False

        idx = self._scores[entry.name].index(entry.score)
        self._scores[entry.name].pop(idx)
        if len(self._scores[entry.name]) == 0:
            self._scores.pop(entry.name)
        return True

    def get_top_scores(self, amount: int) -> List[HighscoreEntry]:
        """Fetch and return top score HighscoreEntry."""
        scores = dict(self._scores)
        top_scores = []
        for _ in range(amount):
            best_player = max(scores.keys(), key=lambda entry: max(entry))
            top_score = max(scores[best_player])
            top_scores.append(
                HighscoreEntry(name=best_player, score=top_score)
            )
            scores[best_player].pop(top_score)

        return top_scores
