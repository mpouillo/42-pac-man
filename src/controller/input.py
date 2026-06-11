from dataclasses import dataclass

from pyray import (
    KeyboardKey,
    is_key_down,
    is_key_pressed,
)


@dataclass(frozen=True)
class InputState:
    """Keyboard input state for one frame."""
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False

    pause: bool = False
    confirm: bool = False
    escape: bool = False


def collect_input() -> InputState:
    """Collect keyboard input for the current frame."""
    return InputState(
        up=is_key_pressed(KeyboardKey.KEY_UP),
        down=is_key_pressed(KeyboardKey.KEY_DOWN),
        left=is_key_pressed(KeyboardKey.KEY_LEFT),
        right=is_key_pressed(KeyboardKey.KEY_RIGHT),
        pause=is_key_pressed(KeyboardKey.KEY_SPACE),
        confirm=is_key_pressed(KeyboardKey.KEY_ENTER),
        escape=is_key_pressed(KeyboardKey.KEY_ESCAPE),
    )
