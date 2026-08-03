"""Idle: 2-frame breathing loop.

Frame 0 is the rest pose. Frame 1 drops the upper body one pixel --
the classic FFT exhale bob -- while the legs stay planted.
"""

from composer import Pose

NAME = "idle"
FRAME_MS = 520  # per-frame duration hint for the game runtime


def frames():
    return [
        Pose(),
        Pose(shift={"upper": (0, 1)}),
    ]
