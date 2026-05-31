from collections import defaultdict
from typing import Dict, List

from protocols import HighscoreEntry


class HighscoreManager:
    def __init__(self) -> None:
        self._scores: Dict[str, List[int]] = defaultdict(list)

    def add_entry(self, name: str, score: int) -> bool:
        """Add an entry to highscores."""
        try:
            entry = HighscoreEntry(name=name, score=score)
        except ValueError:
            return False

        self._scores[entry.name].append(entry.score)
        return True

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

        self._scores[entry.name].append(entry.score)
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
