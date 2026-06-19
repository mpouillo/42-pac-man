"""Highscore, instructions, and end-game page rendering."""

from typing import Any, Callable

import pyray as ray

from src.types.protocols import ModelProtocol
from src.view.constants import (
    CONTENT_FONT_SIZE,
    INFO_CONTENT_OFFSET,
    MUTED_TEXT_COLOR,
    SELECTED_COLOR,
    TEXT_COLOR,
    TITLE_FONT_SIZE,
)


class PageRendererMixin:
    """Draw non-3D information and end-game pages."""

    _window_height: int
    _pending_player_name: str
    _name_error: str
    _score_entry_saved: bool
    _draw_centered_text: Callable[[str, int, int, Any], None]
    _info_page_start_y: Callable[[], int]

    def _draw_highscores(self, model: ModelProtocol) -> None:
        """Draw highscore screen."""
        scores = model.get_top_scores(10)
        start_y = self._info_page_start_y()

        self._draw_centered_text(
            "Highscores",
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        if not scores:
            self._draw_centered_text(
                "No highscores yet",
                start_y + INFO_CONTENT_OFFSET,
                CONTENT_FONT_SIZE,
                TEXT_COLOR,
            )
        else:
            for index, entry in enumerate(scores):
                text = f"{index + 1}. {entry.name} - {entry.score} pts"
                self._draw_centered_text(
                    text,
                    start_y + INFO_CONTENT_OFFSET + index * 36,
                    CONTENT_FONT_SIZE,
                    TEXT_COLOR,
                )

        self._draw_centered_text(
            "Press Enter or Escape to return",
            self._window_height - 80,
            CONTENT_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_score_entry_page(self, model: ModelProtocol) -> None:
        """Draw highscore preview and username input after the game ends."""
        start_y = self._info_page_start_y()

        self._draw_centered_text(
            "Highscores",
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        lines = self._build_score_entry_lines(model)

        y = start_y + 70
        for line in lines:
            self._draw_centered_text(
                line,
                y,
                CONTENT_FONT_SIZE,
                TEXT_COLOR,
            )
            y += 32

        displayed_name = self._pending_player_name.strip()
        if not displayed_name:
            displayed_name = "_"

        self._draw_centered_text(
            f"Enter name: {displayed_name}",
            self._window_height - 180,
            CONTENT_FONT_SIZE,
            TEXT_COLOR,
        )

        if self._name_error:
            self._draw_centered_text(
                self._name_error,
                self._window_height - 140,
                CONTENT_FONT_SIZE,
                ray.Color(255, 80, 80, 255),
            )

        if self._score_entry_saved:
            footer = "Score saved. Press Enter or Escape to return"
        else:
            footer = "Enter: save score"

        self._draw_centered_text(
            footer,
            self._window_height - 90,
            CONTENT_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _build_score_entry_lines(self, model: ModelProtocol) -> list[str]:
        """Build highscore preview lines with the current player's rank."""
        scores = model.get_top_scores(1000)
        current_score = model.get_score()

        player_name = "YOU"
        if self._score_entry_saved and self._pending_player_name.strip():
            player_name = self._pending_player_name.strip()

        base_scores = scores

        if self._score_entry_saved:
            base_scores = self._scores_without_current_saved_entry(
                scores,
                player_name,
                current_score,
            )

        rank = 1 + sum(
            1 for entry in base_scores
            if entry.score >= current_score
        )

        if rank <= 10:
            return self._build_top_ten_with_player(
                base_scores,
                rank,
                player_name,
                current_score,
            )

        lines = [
            f"{index + 1}. {entry.name} - {entry.score} pts"
            for index, entry in enumerate(base_scores[:10])
        ]

        if rank > 11:
            lines.append("...")

        lines.append(f"{rank}. {player_name} - {current_score} pts")
        return lines

    def _scores_without_current_saved_entry(
        self,
        scores: list[Any],
        player_name: str,
        current_score: int,
    ) -> list[Any]:
        """Remove the saved entry to avoid displaying it twice."""
        filtered: list[Any] = []
        removed = False

        for entry in scores:
            if (
                not removed
                and entry.name == player_name
                and entry.score == current_score
            ):
                removed = True
                continue

            filtered.append(entry)

        return filtered

    def _build_top_ten_with_player(
        self,
        scores: list[Any],
        rank: int,
        player_name: str,
        current_score: int,
    ) -> list[str]:
        """Build top 10 lines with current player inserted."""
        lines: list[str] = []
        inserted = False
        display_index = 1
        score_index = 0

        while len(lines) < 10:
            if display_index == rank:
                lines.append(
                    f"{display_index}. {player_name} - {current_score} pts"
                )
                inserted = True
                display_index += 1
                continue

            if score_index >= len(scores):
                break

            entry = scores[score_index]
            lines.append(
                f"{display_index}. {entry.name} - {entry.score} pts"
            )
            score_index += 1
            display_index += 1

        if not inserted and len(lines) < 10:
            lines.append(f"{rank}. {player_name} - {current_score} pts")

        return lines

    def _draw_instructions(self) -> None:
        """Draw instructions screen."""
        lines = [
            "Arrow keys or WASD: move Pac-Man",
            "Escape: pause or resume",
            "Enter: confirm menu selection",
            "F/R: adjust camera FOV",
            "Pause menu: cheat options for testing",
            "",
            "Eat all pacgums to complete the level.",
            "Super pacgums make ghosts edible for a short time.",
            "Avoid ghosts when they are not edible.",
        ]

        start_y = self._info_page_start_y()
        self._draw_centered_text(
            "Instructions",
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        for index, line in enumerate(lines):
            self._draw_centered_text(
                line,
                start_y + INFO_CONTENT_OFFSET + index * 34,
                CONTENT_FONT_SIZE,
                TEXT_COLOR,
            )

        self._draw_centered_text(
            "Press Enter or Escape to return",
            self._window_height - 80,
            CONTENT_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_end_screen(self, model: ModelProtocol, title: str) -> None:
        """Draw game over or victory screen."""
        start_y = self._info_page_start_y()
        self._draw_centered_text(
            title,
            start_y,
            TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        score_text = f"Final score: {model.get_score()}"
        score_y = start_y + INFO_CONTENT_OFFSET
        self._draw_centered_text(
            score_text,
            score_y,
            CONTENT_FONT_SIZE,
            TEXT_COLOR,
        )
