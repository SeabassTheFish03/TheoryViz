__all__ = {
    "ApplyReverseWave"
}

from typing import Callable, Tuple

import numpy as np

from manim.animation.movement import Homotopy
from manim.utils.rate_functions import smooth
from manim.utils.bezier import interpolate, inverse_interpolate
from manim.utils.space_ops import normalize
from manim.constants import UP
from manim.mobject.mobject import Mobject


class ApplyReverseWave(Homotopy):
    def __init__(
        self,
        mobject: Mobject,
        direction: np.ndarray = UP,
        amplitude: float = 0.2,
        wave_func: Callable[[float], float] = smooth,
        time_width: float = 1,
        ripples: int = 1,
        run_time: float = 2,
        **kwargs
    ):
        x_min = mobject.get_left()[0]
        x_max = mobject.get_right()[0]
        vect = amplitude * normalize(direction)

        def wave(t):
            # Clamp input
            if t >= 1 or t <= 0:
                return 0

            phases = ripples * 2
            phase = int(t * phases)
            if phase == 0:
                # First rising ripple
                return wave_func(t * phases)
            elif phase == phases - 1:
                # last ripple. Rising or falling depending on the number of ripples
                # The (ripples % 2)-term is used to make this distinction.
                t -= phase / phases  # Time relative to the phase
                return (1 - wave_func(t * phases)) * (2 * (ripples % 2) - 1)
            else:
                # Longer phases:
                phase = int((phase - 1) / 2)
                t -= (2 * phase + 1) / phases

                # Similar to last ripple:
                return (1 - 2 * wave_func(t * ripples)) * (1 - 2 * ((phase) % 2))

        def homotopy(
            x: float,
            y: float,
            z: float,
            t: float,
        ) -> Tuple[float, float, float]:
            upper = interpolate(0, 1 + time_width, t)
            lower = upper - time_width
            relative_x = inverse_interpolate(x_max, x_min, x)
            wave_phase = inverse_interpolate(lower, upper, relative_x)
            nudge = wave(wave_phase) * vect
            return np.array([x, y, z]) + nudge

        super().__init__(homotopy, mobject, run_time=run_time, **kwargs)
