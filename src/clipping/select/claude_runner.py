"""Poziv Claude Codea u načinu `-p` sa shemom odgovora, i izbor kandidata s ponovnim pokušajima.

Claude Code se poziva bez korisničkih postavki, dodataka i MCP poslužitelja i s vlastitim kratkim
sistemskim upitom: s njima je svaki poziv u probi nosio ~415 000 tokena konteksta (0,42 $ za haiku),
bez njih ~1 500. Odgovor stiže u polju `structured_output` (provjereno na Claude Code 2.1.316);
shema traži jedan dodatni krug, pa je `max_turns` najmanje 2.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from string import Template
from typing import Any, Protocol

from clipping.candidates import CANDIDATES_JSON_SCHEMA, Candidate, validate_candidates
from clipping.profile import CampaignProfile
from clipping.transcript import Transcript

PROMPT_TEMPLATE = Path(__file__).with_name("prompt.md")
DEFAULT_MODEL = "opus"
DEFAULT_TIMEOUT_S = 900
MAX_ATTEMPTS = 3
SYSTEM_PROMPT = (
    "You are a careful video editor working for a clipping tool. Read the task, then answer only "
    "through the structured output in the requested JSON schema."
)
_EMPTY_MCP = '{"mcpServers":{}}'


class SelectionError(RuntimeError):
    """Claude nije vratio upotrebljiv odgovor ili premalo ispravnih kandidata."""


class Runner(Protocol):
    def __call__(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]: ...


def resolve_claude_exe(exe: str | None = None) -> list[str]:
    """Naredba za pokretanje Claude Codea.

    Na Windowsu `claude` iz npm-a je `.cmd` omotač; kroz `cmd.exe` bi se JSON shema lomila na
    navodnicima, pa se izravno zove `claude.exe` koji omotač pokreće. `.py` znači lažni Claude u
    testovima. `CLIPPING_CLAUDE_EXE` nadjačava sve.
    """
    chosen = exe or os.environ.get("CLIPPING_CLAUDE_EXE") or shutil.which("claude")
    if not chosen:
        raise SelectionError("naredba `claude` nije pronađena; je li Claude Code instaliran?")
    path = Path(chosen)
    if path.suffix.lower() == ".py":
        return [sys.executable, str(path)]
    if path.suffix.lower() in (".cmd", ".ps1", ""):
        native = (
            path.parent / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
        )
        if native.is_file():
            return [str(native)]
    return [str(path)]


def run_claude(
    prompt: str,
    schema: dict[str, Any],
    *,
    model: str = DEFAULT_MODEL,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    exe: str | None = None,
    tools: str = "",
    max_turns: int = 3,
    cwd: Path | None = None,
) -> dict[str, Any]:
    """Pošalji uputu na stdin `claude -p` i vrati `structured_output` kao rječnik.

    Claude Code (2.1.316) odbija shemu s ključem `$schema` („no schema with key or ref“), pa se on
    izbacuje; ostatak sheme ide netaknut.
    """
    cli_schema = {k: v for k, v in schema.items() if k != "$schema"}
    command = [
        *resolve_claude_exe(exe),
        "-p",
        "--model", model,
        "--output-format", "json",
        "--json-schema", json.dumps(cli_schema, ensure_ascii=False),
        "--max-turns", str(max_turns),
        "--tools", tools,
        "--setting-sources", "",
        "--strict-mcp-config", "--mcp-config", _EMPTY_MCP,
        "--disable-slash-commands",
        "--no-session-persistence",
        "--system-prompt", SYSTEM_PROMPT,
    ]  # fmt: skip
    if tools:
        command += ["--allowedTools", tools]
    try:
        proc = subprocess.run(
            command,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
            cwd=cwd,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise SelectionError(f"claude -p nije odgovorio u {timeout_s} s") from exc
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout)[-800:]
        raise SelectionError(f"claude -p je završio s kodom {proc.returncode}:\n{tail}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SelectionError(f"claude -p nije vratio JSON: {proc.stdout[:300]!r}") from exc
    if not isinstance(payload, dict):
        raise SelectionError("claude -p je vratio JSON koji nije objekt")
    if payload.get("is_error"):
        raise SelectionError(f"claude -p javlja grešku: {str(payload.get('result'))[:300]}")
    output = payload.get("structured_output")
    if not isinstance(output, dict):
        raise SelectionError(
            f"claude -p nije vratio structured_output (podtip {payload.get('subtype')!r})"
        )
    return output


def build_prompt(
    profile: CampaignProfile,
    window_path: Path,
    *,
    min_n: int = 6,
    max_n: int = 10,
    feedback: list[str] | None = None,
) -> str:
    povratna = ""
    if feedback:
        lines = "\n".join(f"- {reason}" for reason in feedback)
        povratna = (
            "\n## Your previous answer was rejected\n\n"
            "The program rejected these clips; return a full new list that avoids the problems:\n\n"
            f"{lines}\n"
        )
    rules = profile.isjecak.trajanje_s
    return Template(PROMPT_TEMPLATE.read_text(encoding="utf-8")).substitute(
        platforme=", ".join(profile.platforme),
        kreator=profile.kreator,
        min_s=f"{rules.min:g}",
        max_s=f"{rules.max:g}",
        jezik=profile.isjecak.jezik,
        zabranjeno="; ".join(profile.pravila_sadrzaja.zabranjeno) or "(nothing listed)",
        prozor=window_path.read_text(encoding="utf-8").rstrip("\n"),
        min_n=min_n,
        max_n=max_n,
        povratna=povratna,
    )


def select_candidates(
    transcript: Transcript,
    profile: CampaignProfile,
    work_dir: Path,
    *,
    window_path: Path,
    runner: Runner | None = None,
    log: Callable[[str], None] = print,
    min_n: int = 6,
    max_n: int = 10,
) -> list[Candidate]:
    """Do 3 pokušaja; drugi i treći nose razloge odbijanja. Rezultat ide u `candidates.json`."""
    call: Runner = runner or (lambda prompt, schema: run_claude(prompt, schema, cwd=work_dir))
    feedback: list[str] = []
    best: list[Candidate] = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        prompt = build_prompt(profile, window_path, min_n=min_n, max_n=max_n, feedback=feedback)
        try:
            raw = call(prompt, CANDIDATES_JSON_SCHEMA)
        except SelectionError as exc:
            log(f"izbor, pokušaj {attempt}: {exc}")
            feedback = [f"the previous call failed: {exc}"]
            continue
        (work_dir / f"izbor_pokusaj_{attempt}.json").write_text(
            json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        accepted, rejected = validate_candidates(raw, transcript, profile.isjecak)
        accepted = accepted[:max_n]
        log(
            f"izbor, pokušaj {attempt}: prihvaćeno {len(accepted)}, odbijeno {len(rejected)}"
            + "".join(f"\n  odbijen: {r}" for r in rejected)
        )
        if len(accepted) > len(best):
            best = accepted
        if len(accepted) >= min_n:
            break
        feedback = rejected + [
            f"only {len(accepted)} valid clips were returned; at least {min_n} are needed"
        ]
    if len(best) < min_n:
        raise SelectionError(
            f"nakon {MAX_ATTEMPTS} pokušaja samo {len(best)} ispravnih kandidata (treba {min_n})"
        )
    save_candidates(work_dir / "candidates.json", best)
    return best


def save_candidates(path: Path, candidates: list[Candidate]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"kandidati": [c.model_dump() for c in candidates]}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_candidates(path: Path) -> list[Candidate]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Candidate.model_validate(item) for item in data["kandidati"]]
