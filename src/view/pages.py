"""Highscore, instructions, and end-game page rendering."""
# mypy: disable-error-code="attr-defined,no-untyped-def"

from typing import Any

import pyray as ray

from src.constants import (
    ERROR_TEXT_COLOR,
    HIGHSCORE_DISPLAY_LIMIT,
    HIGHSCORE_QUERY_LIMIT,
    HIGHSCORES_TITLE,
    INSTRUCTION_LINES,
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
    TEXT_PAGE_RETURN_FOOTER,
    TEXT_PAGE_TITLE_FONT_SIZE,
)
from src.types.protocols import ModelProtocol


def _format_score_line(rank: int, name: str, score: int) -> str:
    """Return one consistently formatted highscore line."""
    return f"{rank}. {name} - {score} pts"


class PageRendererMixin:
    """Draw non-3D information and end-game pages."""

    def _draw_highscores(self, model: ModelProtocol) -> None:
        """Draw highscore screen."""
        scores = model.get_top_scores(HIGHSCORE_DISPLAY_LIMIT)
        start_y = self._info_page_start_y()

        self._draw_centered_text(
            HIGHSCORES_TITLE,
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
                self._draw_centered_text(
                    _format_score_line(
                        index + 1,
                        entry.name,
                        entry.score,
                    ),
                    start_y
                    + TEXT_PAGE_BODY_TOP_OFFSET
                    + index * TEXT_PAGE_BODY_LINE_SPACING,
                    TEXT_PAGE_BODY_FONT_SIZE,
                    TEXT_COLOR,
                )

        self._draw_centered_text(
            TEXT_PAGE_RETURN_FOOTER,
            self._window_height - TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
            TEXT_PAGE_BODY_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _draw_score_entry_page(
        self,
        model: ModelProtocol,
        state,
    ) -> None:
        """Draw highscore preview and username input after the game ends."""
        start_y = self._info_page_start_y()

        self._draw_centered_text(
            HIGHSCORES_TITLE,
            start_y,
            TEXT_PAGE_TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        lines = self._build_score_entry_lines(model, state)

        y = start_y + TEXT_PAGE_BODY_TOP_OFFSET
        extra_spacing = int(
            TEXT_PAGE_BODY_LINE_SPACING
            * (SCORE_ENTRY_CURRENT_SCORE_SCALE - 1.0)
        )
        for index, (line, is_current_score) in enumerate(lines):
            if is_current_score and index > 0:
                y += extra_spacing

            font_size = TEXT_PAGE_BODY_FONT_SIZE
            line_spacing = TEXT_PAGE_BODY_LINE_SPACING
            if is_current_score:
                font_size = int(
                    TEXT_PAGE_BODY_FONT_SIZE
                    * SCORE_ENTRY_CURRENT_SCORE_SCALE
                )
                line_spacing = int(
                    TEXT_PAGE_BODY_LINE_SPACING
                    * SCORE_ENTRY_CURRENT_SCORE_SCALE
                )

            self._draw_centered_text(
                line,
                y,
                font_size,
                TEXT_COLOR,
            )
            y += line_spacing

            if is_current_score and index < len(lines) - 1:
                y += extra_spacing

        displayed_name = state.pending_player_name

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

        footer = "Enter: save score"
        if state.score_entry_saved:
            footer = "Score saved. Press Enter or Escape to return"
        self._draw_centered_text(
            footer,
            self._window_height - TEXT_PAGE_FOOTER_BOTTOM_OFFSET,
            TEXT_PAGE_BODY_FONT_SIZE,
            MUTED_TEXT_COLOR,
        )

    def _build_score_entry_lines(
        self,
        model: ModelProtocol,
        state,
    ) -> list[tuple[str, bool]]:
        """Build highscore preview lines with the current player's rank."""
        scores = model.get_top_scores(HIGHSCORE_QUERY_LIMIT)

        if state.score_entry_saved:
            return [
                (
                    _format_score_line(index + 1, entry.name, entry.score),
                    False,
                )
                for index, entry in enumerate(
                    scores[:HIGHSCORE_DISPLAY_LIMIT]
                )
            ]

        player_name = state.pending_player_name or "YOU"
        current_score = model.get_score()

        rank = 1 + sum(
            1 for entry in scores
            if entry.score >= current_score
        )

        if rank <= HIGHSCORE_DISPLAY_LIMIT:
            return self._build_top_ten_with_player(
                scores,
                rank,
                player_name,
                current_score,
            )

        lines = [
            (
                _format_score_line(index + 1, entry.name, entry.score),
                False,
            )
            for index, entry in enumerate(
                scores[:HIGHSCORE_DISPLAY_LIMIT]
            )
        ]

        if rank > HIGHSCORE_DISPLAY_LIMIT + 1:
            lines.append(("...", False))

        lines.append(
            (_format_score_line(rank, player_name, current_score), True)
        )
        return lines

    def _build_top_ten_with_player(
        self,
        scores: list[Any],
        rank: int,
        player_name: str,
        current_score: int,
    ) -> list[tuple[str, bool]]:
        """Build top 10 lines with current player inserted."""
        lines: list[tuple[str, bool]] = []
        score_index = 0

        for display_rank in range(1, HIGHSCORE_DISPLAY_LIMIT + 1):
            if display_rank == rank:
                lines.append(
                    (
                        _format_score_line(
                            display_rank,
                            player_name,
                            current_score,
                        ),
                        True,
                    )
                )
                continue

            if score_index >= len(scores):
                break

            entry = scores[score_index]
            lines.append(
                (
                    _format_score_line(
                        display_rank,
                        entry.name,
                        entry.score,
                    ),
                    False,
                )
            )
            score_index += 1

        return lines

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

        show_cursor = (
            int(ray.get_time() / SCORE_ENTRY_CURSOR_BLINK_SECONDS) % 2 == 0
        )
        if not saved and show_cursor:
            ray.draw_text(
                cursor,
                x + text_width + SCORE_ENTRY_CURSOR_GAP,
                y,
                font_size,
                TEXT_COLOR,
            )

    def _draw_instructions(self) -> None:
        """Draw instructions screen."""
        start_y = self._info_page_start_y()
        self._draw_centered_text(
            "Instructions",
            start_y,
            TEXT_PAGE_TITLE_FONT_SIZE,
            SELECTED_COLOR,
        )

        for index, line in enumerate(INSTRUCTION_LINES):
            self._draw_centered_text(
                line,
                start_y
                + TEXT_PAGE_BODY_TOP_OFFSET
                + index * TEXT_PAGE_BODY_LINE_SPACING,
                TEXT_PAGE_BODY_FONT_SIZE,
                TEXT_COLOR,
            )

        self._draw_centered_text(
            TEXT_PAGE_RETURN_FOOTER,
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
