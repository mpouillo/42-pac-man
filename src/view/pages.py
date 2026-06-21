"""Highscore, instructions, and end-game page rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import pyray as ray

from src.constants import (
    ERROR_TEXT_COLOR,
    HIGHSCORE_DISPLAY_LIMIT,
    HIGHSCORE_QUERY_LIMIT,
    MUTED_TEXT_COLOR,
    SCORE_ENTRY_CURRENT_SCORE_SCALE,
    SCORE_ENTRY_CURSOR_BLINK_SECONDS,
    SCORE_ENTRY_CURSOR_GAP,
    SCORE_ENTRY_ERROR_BOTTOM_OFFSET,
    SCORE_ENTRY_NAME_BOTTOM_OFFSET,
    SELECTED_COLOR,
    TEXT_COLOR,
    TEXT_PAGE_BODY_FONT_SIZE,
    TEXT_PAGE_BODY_LINE_SPACING,
    TEXT_PAGE_BODY_TOP_OFFSET,
    TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
    TEXT_PAGE_TITLE_FONT_SIZE,
)
from src.types.protocols import ModelProtocol

if TYPE_CHECKING:
    from src.view.ui import ViewState

ScoreEntryLine = tuple[str, bool]


class PageRendererMixin:
    """Draw non-3D information and end-game pages."""

    _window_width: int
    _window_height: int
    _draw_centered_text: Callable[[str, int, int, Any], None]
    _info_page_start_y: Callable[[], int]

    def _draw_highscores(self, model: ModelProtocol) -> None:
        """Draw highscore screen."""
        scores = model.get_top_scores(HIGHSCORE_DISPLAY_LIMIT)
        start_y = self._info_page_start_y()

        self._draw_centered_text(
            "Highscores",
            start_y,
            TEXT_PAGE_TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        if not scores:
            self._draw_centered_text(
                "No highscores yet",
                start_y + TEXT_PAGE_BODY_TOP_OFFSET,
                TEXT_PAGE_BODY_FONT_SIZE,
                TEXT_COLOR,
            )
        else:
            for index, entry in enumerate(scores):
                text = f"{index + 1}. {entry.name} - {entry.score} pts"
                self._draw_centered_text(
                    text,
                    start_y
                    + TEXT_PAGE_BODY_TOP_OFFSET
                    + index * TEXT_PAGE_BODY_LINE_SPACING,
                    TEXT_PAGE_BODY_FONT_SIZE,
                    TEXT_COLOR,
                )

        self._draw_centered_text(
            "Press Enter or Escape to return",
            self._window_height - TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
            TEXT_PAGE_BODY_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_score_entry_page(
        self,
        model: ModelProtocol,
        state: ViewState,
    ) -> None:
        """Draw highscore preview and username input after the game ends."""
        start_y = self._info_page_start_y()

        self._draw_centered_text(
            "Highscores",
            start_y,
            TEXT_PAGE_TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        lines = self._build_score_entry_lines(model, state)

        y = start_y + TEXT_PAGE_BODY_TOP_OFFSET
        for index, (line, is_current_score) in enumerate(lines):
            if is_current_score and index > 0:
                y += self._score_entry_current_extra_spacing()

            font_size = self._score_entry_line_font_size(is_current_score)
            self._draw_centered_text(
                line,
                y,
                font_size,
                TEXT_COLOR,
            )
            y += self._score_entry_line_spacing(is_current_score)

            if is_current_score and index < len(lines) - 1:
                y += self._score_entry_current_extra_spacing()

        displayed_name = state.pending_player_name.strip()

        self._draw_score_entry_name(
            displayed_name,
            state.score_entry_saved,
        )

        if state.name_error:
            self._draw_centered_text(
                state.name_error,
                self._window_height - SCORE_ENTRY_ERROR_BOTTOM_OFFSET,
                TEXT_PAGE_BODY_FONT_SIZE,
                ERROR_TEXT_COLOR,
            )

        if state.score_entry_saved:
            footer = "Score saved. Press Enter or Escape to return"
        else:
            footer = "Enter: save score"

        self._draw_centered_text(
            footer,
            self._window_height - TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
            TEXT_PAGE_BODY_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _build_score_entry_lines(
        self,
        model: ModelProtocol,
        state: ViewState,
    ) -> list[ScoreEntryLine]:
        """Build highscore preview lines with the current player's rank."""
        scores = model.get_top_scores(HIGHSCORE_QUERY_LIMIT)
        current_score = model.get_score()

        player_name = "YOU"
        if state.score_entry_saved and state.pending_player_name.strip():
            player_name = state.pending_player_name.strip()

        base_scores = scores

        if state.score_entry_saved:
            base_scores = self._scores_without_current_saved_entry(
                scores,
                player_name,
                current_score,
            )

        rank = 1 + sum(
            1 for entry in base_scores
            if entry.score >= current_score
        )

        if rank <= HIGHSCORE_DISPLAY_LIMIT:
            return self._build_top_ten_with_player(
                base_scores,
                rank,
                player_name,
                current_score,
            )

        lines = [
            (f"{index + 1}. {entry.name} - {entry.score} pts", False)
            for index, entry in enumerate(
                base_scores[:HIGHSCORE_DISPLAY_LIMIT]
            )
        ]

        if rank > HIGHSCORE_DISPLAY_LIMIT + 1:
            lines.append(("...", False))

        lines.append((f"{rank}. {player_name} - {current_score} pts", True))
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
    ) -> list[ScoreEntryLine]:
        """Build top 10 lines with current player inserted."""
        lines: list[ScoreEntryLine] = []
        inserted = False
        display_index = 1
        score_index = 0

        while len(lines) < HIGHSCORE_DISPLAY_LIMIT:
            if display_index == rank:
                lines.append(
                    (
                        f"{display_index}. {player_name}"
                        f" - {current_score} pts",
                        True,
                    )
                )
                inserted = True
                display_index += 1
                continue

            if score_index >= len(scores):
                break

            entry = scores[score_index]
            lines.append(
                (f"{display_index}. {entry.name} - {entry.score} pts", False)
            )
            score_index += 1
            display_index += 1

        if not inserted and len(lines) < HIGHSCORE_DISPLAY_LIMIT:
            lines.append(
                (f"{rank}. {player_name} - {current_score} pts", True)
            )

        return lines

    def _score_entry_line_font_size(self, is_current_score: bool) -> int:
        """Return preview font size for normal or current score rows."""
        if is_current_score:
            return int(
                TEXT_PAGE_BODY_FONT_SIZE * SCORE_ENTRY_CURRENT_SCORE_SCALE
            )
        return TEXT_PAGE_BODY_FONT_SIZE

    def _score_entry_line_spacing(self, is_current_score: bool) -> int:
        """Return preview line spacing for normal or current score rows."""
        if is_current_score:
            return int(
                TEXT_PAGE_BODY_LINE_SPACING
                * SCORE_ENTRY_CURRENT_SCORE_SCALE
            )
        return TEXT_PAGE_BODY_LINE_SPACING

    def _score_entry_current_extra_spacing(self) -> int:
        """Return extra spacing around the current score row."""
        return int(
            TEXT_PAGE_BODY_LINE_SPACING
            * (SCORE_ENTRY_CURRENT_SCORE_SCALE - 1.0)
        )

    def _draw_score_entry_name(
        self,
        displayed_name: str,
        saved: bool,
    ) -> None:
        """Draw username input with a blinking cursor."""
        text = f"Enter name: {displayed_name}"
        y = self._window_height - SCORE_ENTRY_NAME_BOTTOM_OFFSET
        font_size = TEXT_PAGE_BODY_FONT_SIZE
        cursor = "|"
        cursor_width = ray.measure_text(cursor, font_size)
        text_width = ray.measure_text(text, font_size)
        group_width = text_width
        if not saved:
            group_width += SCORE_ENTRY_CURSOR_GAP + cursor_width

        x = (self._window_width - group_width) // 2

        ray.draw_text(text, x, y, font_size, TEXT_COLOR)

        if not saved and self._should_show_score_entry_cursor():
            ray.draw_text(
                cursor,
                x + text_width + SCORE_ENTRY_CURSOR_GAP,
                y,
                font_size,
                TEXT_COLOR,
            )

    def _should_show_score_entry_cursor(self) -> bool:
        """Return whether the score-entry cursor is visible this frame."""
        return int(ray.get_time() / SCORE_ENTRY_CURSOR_BLINK_SECONDS) % 2 == 0

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
            TEXT_PAGE_TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        for index, line in enumerate(lines):
            self._draw_centered_text(
                line,
                start_y
                + TEXT_PAGE_BODY_TOP_OFFSET
                + index * TEXT_PAGE_BODY_LINE_SPACING,
                TEXT_PAGE_BODY_FONT_SIZE,
                TEXT_COLOR,
            )

        self._draw_centered_text(
            "Press Enter or Escape to return",
            self._window_height - TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
            TEXT_PAGE_BODY_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_end_screen(self, model: ModelProtocol, title: str) -> None:
        """Draw game over or victory screen."""
        start_y = self._info_page_start_y()
        self._draw_centered_text(
            title,
            start_y,
            TEXT_PAGE_TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        score_text = f"Final score: {model.get_score()}"
        score_y = start_y + TEXT_PAGE_BODY_TOP_OFFSET
        self._draw_centered_text(
            score_text,
            score_y,
            TEXT_PAGE_BODY_FONT_SIZE,
            TEXT_COLOR,
        )
