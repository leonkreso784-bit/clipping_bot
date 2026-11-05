"""Glađenje putanje kadra: One Euro filtar, mrtva zona, ograničenje brzine.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/reframe/smoothing.py`.
Sirovi položaji lica trzaju za nekoliko piksela; zaključan kadar koji je malo decentriran bolji je
od kadra koji se stalno ispravlja. Referenca: Casiez, Roussel, Vogel, "1€ Filter" (CHI 2012).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

DEFAULT_MIN_CUTOFF = 0.6
DEFAULT_BETA = 0.02
DEFAULT_DERIVATIVE_CUTOFF = 1.0


def _alpha(cutoff: float, dt: float) -> float:
    tau = 1.0 / (2.0 * math.pi * cutoff)
    return 1.0 / (1.0 + tau / dt)


class _LowPass:
    def __init__(self) -> None:
        self.value: float | None = None

    def __call__(self, sample: float, alpha: float) -> float:
        if self.value is None:
            self.value = sample
        else:
            self.value = alpha * sample + (1.0 - alpha) * self.value
        return self.value


class OneEuroFilter:
    """Prilagodljivi niskopropusni filtar: jako glađenje u miru, malo pri brzom pomaku."""

    def __init__(
        self,
        *,
        min_cutoff: float = DEFAULT_MIN_CUTOFF,
        beta: float = DEFAULT_BETA,
        derivative_cutoff: float = DEFAULT_DERIVATIVE_CUTOFF,
    ) -> None:
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.derivative_cutoff = derivative_cutoff
        self._value = _LowPass()
        self._derivative = _LowPass()
        self._last_sample: float | None = None
        self._last_time: float | None = None

    def __call__(self, sample: float, timestamp: float) -> float:
        if self._last_time is None or timestamp <= self._last_time:
            self._last_time = timestamp
            self._last_sample = sample
            return self._value(sample, 1.0)
        dt = timestamp - self._last_time
        derivative = (sample - (self._last_sample or sample)) / dt
        smoothed = self._derivative(derivative, _alpha(self.derivative_cutoff, dt))
        cutoff = self.min_cutoff + self.beta * abs(smoothed)
        result = self._value(sample, _alpha(cutoff, dt))
        self._last_time = timestamp
        self._last_sample = sample
        return result


@dataclass
class SmoothingConfig:
    min_cutoff: float = DEFAULT_MIN_CUTOFF
    beta: float = DEFAULT_BETA
    #: Pomak manji od ovoga (px) se ne prati.
    dead_zone_px: float = 12.0
    #: Najveća brzina kadra, px/s.
    max_velocity_px_s: float = 260.0


def smooth_series(
    samples: list[tuple[float, float]], config: SmoothingConfig | None = None
) -> list[tuple[float, float]]:
    """Izgladi `(vrijeme, vrijednost)` uzorke kroz sva tri koraka (uzorci sortirani po vremenu)."""
    config = config or SmoothingConfig()
    if len(samples) <= 1:
        return list(samples)
    one_euro = OneEuroFilter(min_cutoff=config.min_cutoff, beta=config.beta)
    output: list[tuple[float, float]] = []
    held: float | None = None
    previous_time: float | None = None
    for timestamp, raw in samples:
        filtered = one_euro(raw, timestamp)
        if held is None:
            held = filtered
        elif abs(filtered - held) >= config.dead_zone_px:
            target = filtered
            if previous_time is not None:
                dt = max(1e-6, timestamp - previous_time)
                max_step = config.max_velocity_px_s * dt
                delta = target - held
                if abs(delta) > max_step:
                    target = held + math.copysign(max_step, delta)
            held = target
        output.append((timestamp, held))
        previous_time = timestamp
    return output
