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

    fov_increase: bool = False
    fov_decrease: bool = False

def collect_input() -> InputState:
    """Collect keyboard input for the current frame."""
    return InputState(
        up=(
            is_key_pressed(KeyboardKey.KEY_UP)
            or is_key_pressed(KeyboardKey.KEY_W)
        ),
        down=(
            is_key_pressed(KeyboardKey.KEY_DOWN)
            or is_key_pressed(KeyboardKey.KEY_S)
        ),
        left=(
            is_key_pressed(KeyboardKey.KEY_LEFT)
            or is_key_pressed(KeyboardKey.KEY_A)
        ),
        right=(
            is_key_pressed(KeyboardKey.KEY_RIGHT)
            or is_key_pressed(KeyboardKey.KEY_D)
        ),
        pause=is_key_pressed(KeyboardKey.KEY_SPACE),
        confirm=is_key_pressed(KeyboardKey.KEY_ENTER),
        escape=is_key_pressed(KeyboardKey.KEY_ESCAPE),
        fov_increase=is_key_down(KeyboardKey.KEY_R),
        fov_decrease=is_key_down(KeyboardKey.KEY_F),
    )
