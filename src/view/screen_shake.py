"""Small 3D-world-only camera shake effect."""

from __future__ import annotations

import math


class ScreenShake:
    """Track a short decaying shake offset for the 3D world camera."""

    def __init__(self) -> None:
        """Initialize an inactive shake effect."""
        self._duration = 0.0
        self._elapsed = 0.0
        self._strength = 0.0
        self.offset_x = 0.0
        self.offset_z = 0.0

    def start(self, duration: float = 0.40, strength: float = 0.12) -> None:
        """Start or restart the shake effect."""
        self._duration = max(0.0, duration)
        self._elapsed = 0.0
        self._strength = max(0.0, strength)
        self.offset_x = 0.0
        self.offset_z = 0.0

    def update(self, dt: float) -> None:
        """Advance the shake timer and update current offsets."""
        if not self.is_active():
            self.offset_x = 0.0
            self.offset_z = 0.0
            return

        self._elapsed = min(self._duration, self._elapsed + max(0.0, dt))
        progress = self._elapsed / self._duration if self._duration else 1.0
        falloff = (1.0 - progress) ** 2
        amplitude = self._strength * falloff

        self.offset_x = math.sin(self._elapsed * 95.0) * amplitude
        self.offset_z = math.cos(self._elapsed * 117.0) * amplitude

        if not self.is_active():
            self.offset_x = 0.0
            self.offset_z = 0.0

    def is_active(self) -> bool:
        """Return whether the shake is still running."""
        return self._elapsed < self._duration and self._strength > 0.0
