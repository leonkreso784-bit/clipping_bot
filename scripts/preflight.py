"""Preflight: ruff, format, mypy, pytest. Izlazni kod 0 samo ako sve prođe."""

from __future__ import annotations

import subprocess
import sys

KORACI: list[list[str]] = [
    ["uv", "run", "ruff", "check", "."],
    ["uv", "run", "ruff", "format", "--check", "."],
    ["uv", "run", "mypy", "src"],
    ["uv", "run", "pytest", "-m", "not golden", "-q"],
]


def main() -> int:
    pali: list[str] = []
    for korak in KORACI:
        ime = " ".join(korak[2:])
        print(f"== {ime}", flush=True)
        rezultat = subprocess.run(korak, check=False)
        if rezultat.returncode != 0:
            pali.append(ime)
    if pali:
        print(f"PREFLIGHT PAO: {', '.join(pali)}")
        return 1
    print("PREFLIGHT 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
