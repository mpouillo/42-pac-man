"""Immutable UI state passed from the controller to the view."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ViewState:
    """Contain the controller-owned state needed for one rendered frame."""

    main_menu_index: int
    pause_menu_index: int
    invincibility_enabled: bool
    ghost_freeze_enabled: bool
    speed_boost_enabled: bool
    pending_player_name: str
    name_error: str
    score_entry_open: bool
    score_entry_saved: bool
