from dataclasses import dataclass

from src.controller.input import InputState


@dataclass
class MenuCursor:
    """Menu cursor."""
    size: int
    selected_index: int = 0

    def update(self, input_state: InputState) -> None:
        """Move the cursor with up/down input."""
        if input_state.up:
            self.selected_index = (self.selected_index - 1) % self.size
        elif input_state.down:
            self.selected_index = (self.selected_index + 1) % self.size

    def current(self) -> int:
        """Return the currently selected item index."""
        return self.selected_index

    def reset(self) -> None:
        """Reset cursor to first item."""
        self.selected_index = 0
