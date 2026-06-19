from dataclasses import dataclass

import pyray as ray

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

    confirm: bool = False
    escape: bool = False

    fov_increase: bool = False
    fov_decrease: bool = False

    mouse_x: int = 0
    mouse_y: int = 0
    mouse_left_pressed: bool = False


def collect_input() -> InputState:
    """Collect keyboard and mouse input for the current frame."""
    mouse_x = ray.get_mouse_x()
    mouse_y = ray.get_mouse_y()
    mouse_left_pressed = ray.is_mouse_button_pressed(
        ray.MouseButton.MOUSE_BUTTON_LEFT,
    )
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
        confirm=is_key_pressed(KeyboardKey.KEY_ENTER),
        escape=is_key_pressed(KeyboardKey.KEY_ESCAPE),

        fov_increase=is_key_down(KeyboardKey.KEY_F),
        fov_decrease=is_key_down(KeyboardKey.KEY_R),

        mouse_x=mouse_x,
        mouse_y=mouse_y,
        mouse_left_pressed=mouse_left_pressed,
    )
