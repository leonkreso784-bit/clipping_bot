# Clipping cjevovod (C0 do C3) — plan izvedbe

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Za ovaj projekt:** jedna cigla odjednom (`/brick`), grana `feature/<cigla>`, STANI za Leonov OK nakon svake cigle (CLAUDE.md pravilo 2).

**Cilj:** `clipping kreni` od poveznice iz kampanje do mape za pregled s 6 do 10 isječaka 9:16 (titlovi, žig, obvezni tekst), `PREGLED.md`, i nakon odobrenja mapa `mobitel/` za ručnu objavu; sve nastavljivo nakon prekida.

**Arhitektura:** Python paket `clipping` s CLI-jem (typer). Program radi ulaz, zvuk, prijepis (Parakeet kroz onnx-asr), tišine, prozor za Claudea, rezanje (kadar po licu, ASS titlovi, žig), provjeru i pregled. Claude Code (`claude -p`) vraća samo indekse riječi i tekst (ADR-005). SQLite nosi stanje posla; svaki korak upisuje status prije i poslije pa se posao nastavlja od zadnjeg dovršenog koraka.

**Tehnologija:** Python 3.12 (uv), typer, pydantic, PyYAML, onnx-asr[cpu,hub] + onnxruntime, numpy, mediapipe (Tasks API, `face_landmarker.task`), opencv-contrib-python, scenedetect, pysubs2, yt-dlp, FFmpeg 9.0.2 (libass), sqlite3 (stdlib), ruff, mypy, pytest.

**Spec:** `docs/superpowers/specs/2026-11-04-clipping-alat-design.md` (odobren 4. 11. 2026.). Uzor koda: artbyjazi/autoclip (MIT), kopija u scratchpadu probe
`C:\Users\leonk\AppData\Local\Temp\claude\6fa3155ecf1cb79e\74a434f7-fae7-427a-8dd1-0587f92a3a4f\scratchpad\spike\autoclip\backend\autoclip\` (moduli `pipeline/transcript.py`, `boundaries.py`, `captions.py`, `export.py`, `prepare.py`, `reframe/*`). Vendorani ili prepisani kod nosi zaglavlje `# Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi)` i MIT tekst u `THIRD_PARTY_LICENSES.md` (ADR-009).

**Opseg ovog plana:** cigle C0, C1, C2, C3. Cigle C4 (objava Instagram i YouTube kroz API) i C5 (praćenje, prijava) dobivaju vlastiti plan kad računi postoje i imaju tjedan ručne povijesti (dizajn §11a, točka 4).

## Globalna ograničenja

- Python `==3.12.*`; `requires-python = ">=3.12,<3.13"` (MediaPipe nema potvrđenih kotača za 3.13+; pysubs2 1.9.1 i numpy 2.x traže ≥3.12).
- Ovisnosti u `pyproject.toml` pinane `==`; `uv.lock` u gitu. Licence: samo MIT, Apache-2.0, BSD, Unlicense (yt-dlp), PSF (matplotlib kroz mediapipe). Težine modela: Parakeet TDT 0.6B v3 (kartica modela 4. 11. 2026.: CC-BY-4.0, „ready for commercial use“; C1 provjerava tekst licence u preuzetom repozitoriju), `face_landmarker.task` (Apache-2.0), fontovi Anton i Inter (OFL).
- Pinovi (zadnje verzije 4. 11. 2026., ili verzija potvrđena probom): typer 0.27.3, pydantic 2.14.2, PyYAML 6.0.3, onnx-asr 0.12.0, onnxruntime 1.31.1, numpy 2.4.6 (potvrđen s mediapipe u probi), mediapipe 1.2.2, opencv-contrib-python 5.0.0.93, scenedetect 0.7.2, pysubs2 1.9.1, yt-dlp 2026.10.26; dev: ruff 0.17.3, mypy 2.4.1, pytest 9.2.0. `huggingface-hub` pinati na verziju koju `uv lock` razriješi.
- Imena: Python identifikatori na engleskom; sve što Leon vidi ili dizajn zadaje na hrvatskom: CLI naredbe (`kreni`, `odobri`), YAML ključevi profila (§5 dizajna), tablice i statusi baze (§8), datoteke (`PREGLED.md`, `ODOBRENO.txt`, `mobitel/`, `kampanje/<slug>.yaml`, `izlaz/<posao>/`, `data/`).
- `data/`, `izlaz/`, `models/`, `.env`, `*.mp4`, `*.wav` izvan gita (`.gitignore` već pokriva medije; C0 dodaje `models/`).
- Izlazni video: H.264 (libx264, preset medium, crf 20, profile high), 1080×1920, 30 fps, yuv420p, AAC 192k 48 kHz, `loudnorm I=-14:TP=-1.5:LRA=11`, `+faststart`.
- Nikad `git add -A` u ciglama; push samo na Leonov izričit OK.
- Preflight (dodaje C0 u CLAUDE.md): `uv run python scripts/preflight.py` = ruff check + ruff format --check + mypy src + pytest -m "not golden"; mora završiti s 0.
- Testovi s medijima koriste sintetički video iz FFmpeg `lavfi` (fixture u `tests/conftest.py`), ne stvarne datoteke. Testovi označeni `golden` traže `data/izvori/JvLklMRThYs/source.mp4` i preskaču se ako ga nema.

## Fokus pregleda

Ulazi koje dizajn podrazumijeva a nijedan uvjet prolaza ih sam ne pokriva; svaki ima test u zadatku koji drži taj kod:

1. **Prijepis s rupom u govoru dužom od VAD-ovog `max_speech_duration_s`** (glazba, tišina od minute): riječi prije i poslije rupe moraju imati ispravna apsolutna vremena, bez pomaka. → Task 5, test `test_words_absolute_across_segments`.
2. **Claude vrati indekse izvan prijepisa, preklopljene kandidate ili `end < start`**: program odbija kandidat, ne pada, i traži ponovno najviše 2 puta. → Task 16, testovi `test_rejects_out_of_range`, `test_retries_then_fails`.
3. **Profil bez žiga a brief ga traži, ili platforma izvan `platforme`**: posao se odbija prije prijepisa s jasnom porukom. → Task 7, `test_profile_requires_watermark_file`, Task 19, `test_kreni_refuses_platform_not_in_profile`.
4. **Prekid usred rezanja (pola isječaka izrezano)**: nastavak ne reže ponovno gotove isječke i ne ostavlja pola-datoteku kao gotovu. → Task 18, `test_resume_skips_rendered_clips`, `test_partial_file_is_rerendered`.
5. **Video bez lica ili s licem širim od kadra**: kadar pada na centar ili „fit“, nikad iznimka ni odsječeno lice. → Task 10, `test_no_face_centre_crop`, `test_wide_spread_uses_fit`.

---

# Cigla C0 — repozitorij, alati, preflight

**Dokaz cigle:** `uv run python scripts/preflight.py` završi s 0; `uv run clipping --help` ispiše naredbe.

### Task 1: Kostur paketa i pinovi

**Files:**
- Create: `pyproject.toml`, `.python-version` (`3.12`), `src/clipping/__init__.py`, `src/clipping/cli.py`, `tests/__init__.py`, `tests/test_cli.py`, `THIRD_PARTY_LICENSES.md`, `scripts/preflight.py`
- Modify: `.gitignore` (dodaj `models/` i `kampanje/*/` — žigovi i materijali kampanje su tuđi mediji, u gitu ostaju samo `kampanje/*.yaml`), `CLAUDE.md` (odjeljak „Preflight“ s naredbom; stanje „C0 u tijeku“)

**Interfaces:**
- Produces: `clipping.cli.app` (typer.Typer), naredbe `kreni`, `odobri`, `verzija`; `scripts/preflight.py` (exit 0 samo ako sve prođe).

- [ ] **Step 1: Napiši test `tests/test_cli.py`**

```python
from typer.testing import CliRunner
from clipping.cli import app

def test_help_lists_commands():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    for name in ("kreni", "odobri", "verzija"):
        assert name in result.output

def test_verzija_prints_version():
    result = CliRunner().invoke(app, ["verzija"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
```

- [ ] **Step 2: `uv init` okruženje i pyproject**

`pyproject.toml`: `[project] name="clipping" version="0.1.0" requires-python=">=3.12,<3.13"`, `dependencies` s pinovima iz Globalnih ograničenja (bez mediapipe/opencv/scenedetect/onnx-asr dok ih cigla ne treba; dodaju se u C1 i C2), `[project.scripts] clipping = "clipping.cli:app"`, `[dependency-groups] dev = [ruff, mypy, pytest]`, `[tool.ruff] line-length=100 target-version="py312"`, `[tool.ruff.lint] select=["E","F","I","UP","B","SIM","C4"]`, `[tool.mypy] python_version="3.12" strict=true ignore_missing_imports=true`, `[tool.pytest.ini_options] testpaths=["tests"] markers=["golden: traži zlatni video u data/izvori"]`.
Pokreni `uv sync` (uv skida Python 3.12).

- [ ] **Step 3: Pokreni test, očekuj pad**

Run: `uv run pytest tests/test_cli.py -v` → FAIL (`ModuleNotFoundError: clipping.cli`).

- [ ] **Step 4: Implementiraj `src/clipping/cli.py`**

`app = typer.Typer(no_args_is_help=True)`; naredbe `kreni(kampanja: str, izvor: str | None = None)`, `odobri(posao: str, izbaci: str = "")`, `verzija()` — `kreni` i `odobri` zasad dižu `typer.Exit(code=2)` s porukom „još nije izgrađeno (cigla C3)“.

- [ ] **Step 5: `scripts/preflight.py`**

Redom `subprocess.run` za: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, `uv run pytest -m "not golden" -q`; ispiše svaki rezultat; `sys.exit(1)` ako bilo koji padne.

- [ ] **Step 6: Pokreni test i preflight**

Run: `uv run pytest tests/test_cli.py -v` → PASS. Run: `uv run python scripts/preflight.py` → exit 0.

- [ ] **Step 7: `THIRD_PARTY_LICENSES.md` i CLAUDE.md**

U `THIRD_PARTY_LICENSES.md` MIT tekst autoclipa s napomenom koji moduli su po uzoru. U CLAUDE.md dodaj odjeljak `## Preflight` s naredbom i pravilom „mora biti 0 prije commita“.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml .python-version uv.lock src tests scripts THIRD_PARTY_LICENSES.md .gitignore CLAUDE.md
git commit -m "C0: kostur paketa clipping, pinovi, preflight"
```

### Task 2: Sintetički testni video i FFmpeg omotač

**Files:**
- Create: `src/clipping/ffmpeg.py`, `tests/conftest.py`, `tests/test_ffmpeg.py`

**Interfaces:**
- Produces: `ffmpeg.run(args: list[str], *, cwd: Path | None = None) -> None` (diže `FFmpegError(stderr)`), `ffmpeg.probe(path: Path) -> MediaInfo` (`duration_s: float, width: int, height: int, fps: float, has_audio: bool`), `ffmpeg.ffmpeg_path() -> str`, `ffmpeg.ffprobe_path() -> str`.
- Fixture `synthetic_video(tmp_path_factory) -> Path`: 8 s, 1280×720, 30 fps, `testsrc2` + `sine=440`, H.264/AAC, session scope.

- [ ] **Step 1: Test**

```python
def test_probe_synthetic(synthetic_video):
    info = probe(synthetic_video)
    assert abs(info.duration_s - 8.0) < 0.2
    assert (info.width, info.height) == (1280, 720)
    assert info.has_audio

def test_run_raises_on_bad_args(tmp_path):
    with pytest.raises(FFmpegError):
        run(["-i", str(tmp_path / "nema.mp4"), "-f", "null", "-"])
```

- [ ] **Step 2: Pokreni, očekuj pad** — `uv run pytest tests/test_ffmpeg.py -v` → FAIL.
- [ ] **Step 3: Implementiraj** — `run` dodaje `-hide_banner -nostdin -y`; `probe` zove `ffprobe -v error -print_format json -show_streams -show_format`. Fixture u conftest zove `run(["-f","lavfi","-i","testsrc2=size=1280x720:rate=30","-f","lavfi","-i","sine=frequency=440","-t","8","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac", out])`.
- [ ] **Step 4: Test prolazi, preflight 0.**
- [ ] **Step 5: Commit** — `git add src/clipping/ffmpeg.py tests/conftest.py tests/test_ffmpeg.py && git commit -m "C0: ffmpeg omotač i sintetički testni video"`.

**Kraj C0:** ažuriraj `docs/plan/PLAN_V1.md` (C0 ✅ s izlazom preflighta), `docs/records/SLJEDECA_SESIJA.md`. STANI za Leonov OK.

---

# Cigla C1 — prijepis Parakeetom na CPU-u

**Dokaz cigle:** zlatni video (90 min, `audio.wav` iz probe) prepisan ispod 600 s zidnog vremena; isti oblik `transcript.json` kao proba; podudaranje riječi s Whisperovim prijepisom ≥ 85 % na prvih 5 minuta; licenca Parakeeta potvrđena i zapisana u ADR-008.

### Task 3: Model prijepisa (riječi s vremenima)

**Files:**
- Create: `src/clipping/transcript.py`, `tests/test_transcript.py`

**Interfaces:**
- Produces: `@dataclass Word(text: str, start: float, end: float)`; `@dataclass Transcript(words: list[Word], language: str, model: str)` s `duration`, `time_range(first, last) -> (float, float)`, `slice(first, last) -> list[Word]`, `text_between(first, last) -> str`, `sentence_end_indices() -> list[int]`, `save(path)`, `load(path)`; `Word.ends_sentence` (regex `[.!?…]+["'”’)\]]*$`). JSON oblik: `{"language","model","words":[{"text","start","end"}]}` (kao proba, bez `speaker` i `segments`).

- [ ] **Step 1: Testovi**

```python
def test_roundtrip_json(tmp_path):
    t = Transcript([Word("Hi.", 0.0, 0.3), Word("there", 0.4, 0.7)], "en", "test")
    t.save(tmp_path / "t.json"); assert Transcript.load(tmp_path / "t.json") == t

def test_sentence_ends():
    t = Transcript([Word("Hi.", 0, .3), Word("Go!", .4, .7), Word("now", .8, 1)], "en", "x")
    assert t.sentence_end_indices() == [0, 1]

def test_time_range_clamps():
    t = Transcript([Word("a", 0, 1), Word("b", 1, 2)], "en", "x")
    assert t.time_range(-5, 99) == (0.0, 2.0)
```

- [ ] **Step 2: Pad → implementiraj po uzoru na autoclip `transcript.py` (bez diarizacije) → prolaz.**
- [ ] **Step 3: Commit** — `git commit -m "C1: model prijepisa Word/Transcript"`.

### Task 4: Zvuk i tišine

**Files:**
- Create: `src/clipping/audio.py`, `tests/test_audio.py`

**Interfaces:**
- Consumes: `ffmpeg.run`.
- Produces: `extract_audio(source: Path, destination: Path) -> Path` (16 kHz mono pcm_s16le), `detect_silences(audio: Path, *, noise_db: float = -32.0, min_duration_s: float = 0.2) -> list[Silence]` (`Silence(start, end)`), `save_silences(path, silences)`, `load_silences(path)` (JSON lista `{"start","end"}`), `generate_thumbnails(source, dir, *, interval_s=15, width=320) -> list[Path]`.

- [ ] **Step 1: Testovi**

```python
def test_extract_audio_is_16k_mono(synthetic_video, tmp_path):
    wav = extract_audio(synthetic_video, tmp_path / "a.wav")
    info = probe(wav); assert info.has_audio and abs(info.duration_s - 8.0) < 0.2
    # ffprobe stream: sample_rate 16000, channels 1

def test_detect_silences_finds_gap(tmp_path):
    # lavfi: 2 s sine, 1 s anullsrc, 2 s sine → jedna tišina oko [2.0, 3.0]
    ...
    assert len(s) == 1 and abs(s[0].start - 2.0) < 0.15 and abs(s[0].end - 3.0) < 0.15

def test_thumbnails_every_15s(synthetic_video, tmp_path):
    assert len(generate_thumbnails(synthetic_video, tmp_path, interval_s=4)) == 2
```

- [ ] **Step 2: Pad → implementiraj (po uzoru na autoclip `prepare.py`) → prolaz → commit `C1: zvuk, tišine, sličice`.**

### Task 5: Parakeet kroz onnx-asr

**Files:**
- Create: `src/clipping/asr.py`, `tests/test_asr.py`
- Modify: `pyproject.toml` (dodaj `onnx-asr[cpu,hub]==0.12.0`, `onnxruntime==1.31.1`, `numpy==2.4.6`, `huggingface-hub==<razriješeno>`)

**Interfaces:**
- Produces: `transcribe(audio: Path, *, model_dir: Path = Path("models/parakeet-v3"), threads: int = 12) -> Transcript`; `tokens_to_words(segments: list[SegmentTokens]) -> list[Word]` gdje `SegmentTokens(start: float, end: float, tokens: list[str], timestamps: list[float])` (čisti ulaz, testabilan bez modela).

Pravila `tokens_to_words` (odluka; onnx-asr daje vremena početka tokena relativna na VAD segment, bez kraja): token koji počinje razmakom (onnx-asr zamjenjuje `▁` razmakom) otvara novu riječ; `word.start = segment.start + timestamps[i]` za prvi token riječi; `word.end = segment.start + timestamps[j]` gdje je `j` prvi token sljedeće riječi, a za zadnju riječ u segmentu `segment.end`; tekst riječi = spojeni tokeni bez vodećeg razmaka. Prazni tokeni se preskaču.

- [ ] **Step 1: Testovi (bez modela)**

```python
def test_tokens_to_words_basic():
    seg = SegmentTokens(10.0, 12.0, [" Hel", "lo", " world", "."], [0.0, 0.2, 0.6, 0.9])
    w = tokens_to_words([seg])
    assert [x.text for x in w] == ["Hello", "world."]
    assert w[0].start == 10.0 and w[0].end == 10.6 and w[1].end == 12.0

def test_words_absolute_across_segments():
    a = SegmentTokens(0.0, 1.0, [" a"], [0.1]); b = SegmentTokens(70.0, 71.0, [" b"], [0.2])
    w = tokens_to_words([a, b]); assert w[1].start == 70.2 and w[0].end == 1.0
```

- [ ] **Step 2: Pad → implementiraj `tokens_to_words` → prolaz.**
- [ ] **Step 3: Implementiraj `transcribe`**

```python
so = onnxruntime.SessionOptions(); so.intra_op_num_threads = threads
model = onnx_asr.load_model("nemo-parakeet-tdt-0.6b-v3", model_dir, asr_config={"sess_options": so})
model = model.with_vad(onnx_asr.load_vad("silero"), max_speech_duration_s=30, min_silence_duration_ms=300, speech_pad_ms=100).with_timestamps()
```
Iteriraj `model.recognize(str(audio))` → `SegmentTokens(res.start, res.end, res.tokens, res.timestamps)` → `tokens_to_words`. `Transcript(language="en", model="parakeet-tdt-0.6b-v3")`. Prvi poziv skida model u `model_dir` (hub).

- [ ] **Step 4: Dimni test s modelom (oznaka `golden`)** — na 30-sekundnom isječku `audio.wav` iz probe: vraća ≥ 50 riječi, sva vremena rastu, `end <= 30.5`.
- [ ] **Step 5: Commit** — `git commit -m "C1: Parakeet kroz onnx-asr, tokeni u riječi"`.

### Task 6: Mjerenje na zlatnom videu i licenca

**Files:**
- Create: `scripts/mjeri_prijepis.py`, `data/izvori/JvLklMRThYs/` (izvan gita; kopiraj `source.mp4`, `audio.wav` i Whisperov `transcript.json` kao `whisper_referenca.json` iz scratchpada probe, putanje u zaglavlju plana)
- Modify: `docs/records/DECISIONS.md` (ADR-008 status i licenca), `docs/plan/PLAN_V1.md` (C1 dokaz s brojkama), `docs/records/BACKLOG.md` (skini Parakeet provjere)

- [ ] **Step 1: `scripts/mjeri_prijepis.py`** — mjeri zidno vrijeme `transcribe(audio.wav)` za `threads` u (12, 6, zadano), sprema `transcript.json`, računa podudaranje riječi prema `whisper_referenca.json` na prvih 300 s (normalizacija: mala slova, bez interpunkcije; `difflib.SequenceMatcher.ratio()`), ispiše tablicu.
- [ ] **Step 2: Pokreni** — `uv run python scripts/mjeri_prijepis.py data/izvori/JvLklMRThYs/audio.wav`. Prolaz: najbolje vrijeme < 600 s, podudaranje ≥ 0.85. Ako padne vrijeme: zabilježi i pokreni rezervu (`faster-whisper` medium, 12 niti) istim skriptom prije nego se cigla proglasi gotovom; ADR-008 dobiva ishod.
- [ ] **Step 3: Licenca** — otvori `LICENSE`/README u `models/parakeet-v3` i karticu modela; zapiši točno ime licence i rečenicu o komercijalnoj uporabi u ADR-008 (status ✅ ili ❌ s rezervom). Ako nije CC-BY-4.0, ispravi CLAUDE.md pravilo 8 i dizajn §3.
- [ ] **Step 4: Dokumenti i commit** — `git add scripts/mjeri_prijepis.py docs && git commit -m "C1: mjerenje Parakeeta na zlatnom videu, ADR-008 potvrđen"`.

**Kraj C1:** STANI za Leonov OK s tablicom mjerenja u izvještaju.

---

# Cigla C2 — rezanje po profilu kampanje

**Dokaz cigle:** 9 isječaka iz probe (`candidates.json` iz `izlaz/proba-2026-11-04-caleb-hammer/radno/`) ponovno izrezano iz zlatnog videa s žigom i rotacijom stilova, prosjek < 120 s po isječku; automatska provjera pada kad žig nedostaje ili titl kasni; psovke u titlovima sa zvjezdicama.

### Task 7: Profil kampanje (YAML → model)

**Files:**
- Create: `src/clipping/profile.py`, `tests/test_profile.py`, `tests/fixtures/kampanja_test.yaml`, `kampanje/README.md` (kako se piše profil), `kampanje/caleb-hammer.yaml` (iz dizajna §5, računi prazni dok Leon ne otvori)

**Interfaces:**
- Produces: pydantic modeli s točnim ključevima iz dizajna §5: `CampaignProfile(slug, kreator, platforma_kampanje, url_kampanje, cijena_po_100k_usd, prag_kvalifikacije_pregleda, platforme: list[Literal["tiktok","instagram","x","youtube"]], racuni: dict[str,str], izvori: Sources(dopusteni_kanali: list[str], zapis_prava: str), isjecak: ClipRules(trajanje_s: Range(min,max), jezik), grafika: Graphics(zig: Watermark(datoteka, polozaj: Literal["centar","gore_lijevo","gore_desno","dolje_lijevo","dolje_desno"], neprozirnost) | None, obvezni_tekst: str | None, obvezni_zvuk: str | None, hashtagovi: list[str]), opis: Description(oznaka_placene_suradnje: bool, predlozak: str), pravila_sadrzaja: ContentRules(zabranjeno: list[str], stil_titlova: list[str], psovke: Profanity(titlovi: Literal["zvjezdice","puno"], zvuk: Literal["nista"])), raspored: Schedule(objava_dnevno_po_racunu, zagrijavanje_dana))`; `load_profile(path: Path) -> CampaignProfile` (diže `ProfileError` s porukom na hrvatskom); `profile.caption_style_for(index: int) -> str` (rotacija `index % len`).

Validacije: `zig.datoteka` mora postojati (relativno na korijen repozitorija); `stil_titlova` neprazan i svaki u `captions.PRESETS` (Task 11; do tada popis `{"bold_pop","clean_lower"}` u profile.py); `racuni` ključevi ⊆ `platforme`; `zvuk: beep` odbijen porukom „beep se ne gradi u V1“.

- [ ] **Step 1: Testovi** — `test_loads_fixture`, `test_profile_requires_watermark_file` (fixture s nepostojećim `zig.png` → `ProfileError`), `test_rejects_unknown_platform`, `test_style_rotation` (`["a","b"]`: index 2 → `"a"`), `test_rejects_beep`.
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C2: profil kampanje`.**

### Task 8: Kandidati i granice rezova

**Files:**
- Create: `src/clipping/candidates.py`, `src/clipping/boundaries.py`, `tests/test_candidates.py`, `tests/test_boundaries.py`

**Interfaces:**
- Consumes: `Transcript`, `Silence`.
- Produces: `Candidate(start_word_index: int, end_word_index: int, naslov: str, udica: str, ocjena: int, razlog: str, opis: str)` (pydantic, `ocjena` 0..100, `udica` ≤ 120 znakova); `CANDIDATES_JSON_SCHEMA: dict` (JSON Schema za `{"kandidati": [Candidate...]}`, šalje se Claudeu); `validate_candidates(raw: dict, transcript: Transcript, rules: ClipRules) -> tuple[list[Candidate], list[str]]` (vraća prihvaćene i razloge odbijanja: indeks izvan `[0, len)`, `end <= start`, preklapanje > 50 % s drugim prihvaćenim kandidatom višeg `ocjena`); `Boundary(start_s, end_s, start_word, end_word)`; `refine(transcript, start_word, end_word, *, silences, min_duration_s, max_duration_s) -> Boundary | None` (po uzoru na autoclip `boundaries.py`: snap na rečenicu, clamp trajanja, poravnanje na tišinu).

- [ ] **Step 1: Testovi** — `test_rejects_out_of_range` (indeks 10 u prijepisu od 5 riječi → odbijen s razlogom), `test_rejects_end_before_start`, `test_rejects_overlap_over_half` (dva kandidata 0–100 i 40–140 → ostaje viši `ocjena`), `test_refine_snaps_to_sentence` (prijepis s točkama; početak usred rečenice → pomaknut na prvu riječ rečenice), `test_refine_none_when_too_long_without_sentence`, `test_refine_aligns_into_silence`.
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C2: kandidati, provjera indeksa, granice rezova`.**

### Task 9: Psovke u titlovima

**Files:**
- Create: `src/clipping/profanity.py`, `tests/test_profanity.py`

**Interfaces:**
- Produces: `mask(text: str) -> str` (zadržava prvo slovo, ostatak `*`, čuva interpunkciju i velika slova: `"Fucking,"` → `"F******,"`); `PROFANITY: frozenset[str]` (engleski popis, bar 30 korijena, usporedba bez obzira na slova i s uobičajenim nastavcima `-ing`, `-ed`, `-s`, `-er`).

- [ ] **Step 1: Testovi** — `test_mask_keeps_first_letter_and_punct`, `test_mask_leaves_clean_words`, `test_mask_handles_suffix` (`"shitty"` → `"s*****"`).
- [ ] **Step 2: Pad → implementiraj → prolaz → commit.**

### Task 10: Kadar po licu (MediaPipe)

**Files:**
- Create: `src/clipping/reframe/__init__.py`, `croppath.py`, `faces.py`, `tracker.py`, `scenes.py`, `smoothing.py`, `speaker.py`, `tests/test_reframe.py`, `src/clipping/models_dl.py`
- Modify: `pyproject.toml` (mediapipe 1.2.2, opencv-contrib-python 5.0.0.93, scenedetect 0.7.2)

**Interfaces:**
- Produces: `build_crop_path(video: Path, *, start_s: float, end_s: float, config: ReframeConfig | None = None) -> CropPath`; `CropPath(source_width, source_height, segments: list[CropSegment])`, `CropSegment(start_s, end_s, width, height, keyframes, strategy, fit)`, `segment_crop_filter(segment) -> str`; `models_dl.ensure_face_landmarker(models_dir: Path = Path("models")) -> Path` (skida `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task`, 3 758 596 bajtova, provjera veličine).

Prepiši module po uzoru na autoclip `reframe/*` bez diarizacije (`speaker.py` koristi samo aktivnost usta `mar`): TRACK / WIDE / GENERAL strategije, `EYE_LINE_RATIO = 0.38`, `sample_fps = 5`, `fit` kad raspon lica > 0.95 širine kadra.

- [ ] **Step 1: Testovi (bez lica, sintetički video)** — `test_no_face_centre_crop` (segmenti pokrivaju `[0, 8]`, strategija GENERAL, `(width, height) == (404, 720)`, širina 405 zaokružena na parnu), `test_crop_filter_static_expression` (`crop=w=404:h=720:x='438.0':y='0.0'`), `test_wide_spread_uses_fit` (čisti test nad `_wide_segment` s dvije opažene glave na 5 % i 95 % širine → `fit=True`), `test_segments_tile_without_gaps`.
- [ ] **Step 2: Pad → implementiraj → prolaz.**
- [ ] **Step 3: Golden test (`golden`)** — isječak 1155.8–1209.7 s zlatnog videa: `build_crop_path` vraća ≥ 2 segmenta, bar jedan TRACK, nijedan keyframe izvan `[0, source_w - crop_w]`.
- [ ] **Step 4: Commit** — `C2: kadar po licu po uzoru na autoclip`.

### Task 11: Titlovi (ASS, stilovi, rotacija, psovke)

**Files:**
- Create: `src/clipping/captions.py`, `src/clipping/assets/fonts/Anton-Regular.ttf`, `Inter-Variable.ttf`, `src/clipping/assets/fonts/OFL.txt`, `tests/test_captions.py`

**Interfaces:**
- Consumes: `Word`, `profanity.mask`.
- Produces: `PRESETS: dict[str, CaptionStyle]` s bar `bold_pop` (kao proba: Anton, `size_ratio 0.062`, akcent `#FFE500`, scale 118, 4 riječi) i `clean_lower` (Inter, 0.034, bez akcenta, 8 riječi), plus `boxed`; `build_ass(words, style, *, width, height, time_offset_s, mask_profanity: bool, top_text: str | None) -> pysubs2.SSAFile`; `write_ass(path, ...) -> Path`. `top_text` je obvezni tekst kampanje: vlastiti stil `Gore` (`\an8`, Anton, `size_ratio 0.045`, `margin_v = 0.12 * height`), jedan event od 0 do kraja isječka.

- [ ] **Step 1: Testovi** — `test_events_follow_word_times` (prvi event start == `word.start - offset` na 10 ms), `test_profanity_masked_in_text` (riječ `"shit"` nigdje u tekstu eventa, `"s***"` jest), `test_top_text_event_spans_clip`, `test_style_rotation_uses_profile` (Task 7 helper), `test_clean_lower_has_no_per_word_events`.
- [ ] **Step 2: Pad → implementiraj (po uzoru na autoclip `captions.py`) → prolaz → commit `C2: ASS titlovi, stilovi, obvezni tekst, psovke`.**

### Task 12: Žig i izvoz

**Files:**
- Create: `src/clipping/export.py`, `tests/test_export.py`, `tests/fixtures/zig_test.png` (64×64, bijeli krug na prozirnom)

**Interfaces:**
- Consumes: `CropPath`, `segment_crop_filter`, `captions.write_ass`, `ffmpeg.run`.
- Produces: `ExportRequest(source, destination, start_s, end_s, crop_path, words, style, watermark: Watermark | None, top_text: str | None, mask_profanity: bool)`; `export_clip(request, *, work_dir: Path) -> Path`; `build_filtergraph(request, *, subtitle_name, fonts_name, watermark_input_index: int | None) -> str`; `watermark_position(polozaj) -> str` (`centar` → `(W-w)/2:(H-h)/2`, `dolje_desno` → `W-w-40:H-h-40` ...).

Žig: drugi `-i zig.png`, lanac `[1:v]format=rgba,colorchannelmixer=aa={neprozirnost}[wm]`, `[vcat][wm]overlay={pos}[vwm]`, pa `ass=` filter zadnji (titlovi iznad žiga). Encoder fiksno libx264 (nema NVENC-a). Fontovi i ASS se stavljaju u radnu mapu i referenciraju golim imenom (uzor `relative_filter_workspace`).

- [ ] **Step 1: Testovi** — `test_filtergraph_contains_overlay_and_ass`, `test_export_synthetic_clip_properties` (2 s iz sintetičkog videa: izlaz 1080×1920, 30 fps, ima zvuk, trajanje 2.0 ± 0.1), `test_export_without_watermark_has_no_overlay`.
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C2: izvoz s žigom i titlovima`.**

### Task 13: Automatska provjera isječka

**Files:**
- Create: `src/clipping/qa.py`, `tests/test_qa.py`

**Interfaces:**
- Produces: `check_clip(path: Path, *, expected: ClipExpectation) -> QaReport` gdje `ClipExpectation(min_s, max_s, watermark: Watermark | None, ass_path: Path, words: list[Word], start_s)`; `QaReport(ok: bool, nalazi: list[str])`. Provjere: trajanje u `[min, max]`; `loudnorm` izmjeren `ebur128` integrirano u `[-16, -12]` LUFS; nema crnih kadrova (`blackdetect d=0.5` prazno); žig prisutan: uzmi kadar na 1.0 s (`ffmpeg -ss 1 -frames:v 1`), izreži područje žiga po `watermark_position`, normalizirana korelacija luminancije s alfa-maskom žiga ≥ 0.5; titlovi: svaki ASS event ima `start == word.start - start_s` unutar 100 ms.

- [ ] **Step 1: Testovi** — `test_qa_passes_on_good_clip` (izvoz iz Task 12 s žigom), `test_qa_fails_when_watermark_missing` (isti izvoz bez žiga, očekivanje s žigom → `ok False`, nalaz sadrži „žig“), `test_qa_fails_on_duration`, `test_qa_fails_when_caption_shifted` (ASS pomaknut 0.5 s).
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C2: automatska provjera isječka`.**

### Task 14: Reprodukcija probe (dokaz C2)

**Files:**
- Create: `scripts/izrezi_probu.py`
- Modify: `docs/plan/PLAN_V1.md` (C2 ✅ s vremenima), `docs/records/SLJEDECA_SESIJA.md`

- [ ] **Step 1: Skripta** — učita `kampanje/caleb-hammer.yaml` (žig: privremeno `tests/fixtures/zig_test.png` ako pravi ne postoji, navesti u izvještaju), `data/izvori/JvLklMRThYs/transcript.json` (iz C1) i `izlaz/proba-2026-11-04-caleb-hammer/radno/candidates.json`; za svaki kandidat `validate` → `refine` → `build_crop_path` → `export_clip` (stil rotiran) → `check_clip`; ispiše tablicu (isječak, trajanje, sekunde rezanja, QA). Napomena: indeksi probe odnose se na Whisperov prijepis; skripta prevodi preko vremena (`time_range` na Whisperovu prijepisu → `indices_in_range` na Parakeetovu).
- [ ] **Step 2: Pokreni** — `uv run python scripts/izrezi_probu.py` → 9 MP4 u `izlaz/proba-c2/`, svi QA `ok`, prosjek < 120 s. Leon pogleda 2 isječka (žig, stil, zvjezdice).
- [ ] **Step 3: Dokumenti, commit `C2: reprodukcija probe s žigom`. STANI za Leonov OK.**

---

# Cigla C3 — baza, `kreni`, izbor, pregled, mobitel

**Dokaz cigle:** `clipping kreni --kampanja caleb-hammer --izvor <url zlatnog videa>` od nule do `izlaz/<posao>/PREGLED.md` bez ručnih koraka; prekid (`Ctrl+C`) usred rezanja pa ponovni `kreni` nastavlja bez ponovnog prijepisa i bez ponovnog rezanja gotovih isječaka; `clipping odobri` puni `mobitel/`.

### Task 15: Baza stanja (SQLite)

**Files:**
- Create: `src/clipping/db.py`, `src/clipping/schema.sql`, `tests/test_db.py`

**Interfaces:**
- Produces: `Database(path: Path)` s `connect()`, `migrate()` (izvršava `schema.sql`, tablica `migracija(verzija)`), i metodama: `upsert_kampanja(profile) -> int`, `get_or_create_izvor(kampanja_id, url, sha256, zapis_prava) -> int`, `create_posao(izvor_id) -> str` (id = `YYYYMMDD-<slug>-<4 hex>`), `set_korak(posao_id, korak: str, status: Literal["pocet","gotov","greska"], poruka="")`, `last_done_korak(posao_id) -> str | None`, `insert_isjecak(posao_id, candidate, boundary, path, stil) -> int`, `set_isjecak_status(id, status)`, `isjecci(posao_id) -> list[Row]`, `published_ranges(kampanja_id) -> list[(izvor_id, start_s, end_s)]`, `log_dogadjaj(posao_id, razina, poruka)`.
- Tablice (dizajn §8): `kampanja, izvor, posao, korak, isjecak, objava, pregledi, isplata, dogadjaj`. Statusi isječka točno: `izrezan, provjeren, odobren, izbacen, zakazan, objavljen, prijavljen, placen` (CHECK ograničenje).

- [ ] **Step 1: Testovi** — `test_migrate_idempotent`, `test_posao_korak_resume` (`set_korak(a,"prijepis","gotov")` → `last_done_korak == "prijepis"`), `test_isjecak_status_check_rejects_unknown` (`sqlite3.IntegrityError`), `test_published_ranges_only_published`.
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C3: SQLite baza stanja`.**

### Task 16: Izbor kroz `claude -p`

**Files:**
- Create: `src/clipping/select/window.py`, `src/clipping/select/claude_runner.py`, `src/clipping/select/prompt.md`, `tests/test_window.py`, `tests/test_claude_runner.py`, `tests/fixtures/fake_claude.py`

**Interfaces:**
- Consumes: `Transcript`, `CampaignProfile`, `CANDIDATES_JSON_SCHEMA`, `validate_candidates`.
- Produces: `write_window(transcript: Transcript, path: Path) -> Path` (jedna rečenica po retku, svaka riječ `[i]tekst`, razmak između; rečenica = do `ends_sentence`); `build_prompt(profile, window_path, *, min_n=6, max_n=10) -> str` (iz `prompt.md` s poljima: kreator, zabranjeno, trajanje, jezik, ton; traži `udica` ≤ 120 znakova, raznolike udice, bez istih tema); `run_claude(prompt: str, schema: dict, *, model: str = "opus", timeout_s: int = 900, exe: str | None = None) -> dict` (subprocess `claude -p --model <m> --output-format json --json-schema <json> --max-turns 1`, prompt na stdin, čita polje `structured_output` iz JSON izlaza; diže `SelectionError` na ne-nula izlaz ili neispravan JSON); `select_candidates(transcript, profile, work_dir, db, posao_id, *, runner=run_claude) -> list[Candidate]` (do 3 pokušaja; drugi i treći prompt dodaju razloge odbijanja; manje od `min_n` prihvaćenih nakon 3 pokušaja → `SelectionError`).

- [ ] **Step 1: Testovi** — `test_window_format` (`"[0]Men [1]are [2]just [3]like [4]this."` u prvom retku), `test_run_claude_parses_structured_output` (`exe` = `tests/fixtures/fake_claude.py` koji ispiše `{"structured_output": {...}}`), `test_rejects_out_of_range` (lažni runner vraća indeks 99999 → odbijen, drugi pokušaj), `test_retries_then_fails` (runner uvijek vraća 1 kandidat → `SelectionError` nakon 3 poziva).
- [ ] **Step 2: Pad → implementiraj → prolaz.**
- [ ] **Step 3: Stvarni poziv (ručno, jednom)** — `uv run python -c "..."` nad `window.txt` zlatnog videa; provjeri da `--json-schema` vraća `structured_output` (ako je polje drukčije nazvano, ispravi `claude_runner.py` i test). Zapiši trajanje u izvještaj.
- [ ] **Step 4: Commit** — `C3: prozor prijepisa i izbor kroz claude -p`.

### Task 17: Ulaz (yt-dlp) i prava

**Files:**
- Create: `src/clipping/ingest.py`, `tests/test_ingest.py`
- Modify: `pyproject.toml` (yt-dlp 2026.10.26)

**Interfaces:**
- Produces: `is_allowed_source(url: str, profile: CampaignProfile) -> bool` (kanal iz `dopusteni_kanali`: usporedba po `channel_url`/`uploader_url` iz yt-dlp metapodataka, ili po handle-u `@...` u URL-u); `list_channel_videos(channel_url: str, *, limit=20) -> list[VideoMeta(id, url, title, upload_date)]` (`yt-dlp --flat-playlist -J`); `download(url: str, dest_dir: Path) -> Path` (`-S "res:1080,vcodec:h264"`, `--merge-output-format mp4`, izlaz `source.mp4`; vraća i `sha256`); `pick_new_video(profile, db) -> VideoMeta | None` (najnoviji koji nije u `izvor`).

- [ ] **Step 1: Testovi (yt-dlp lažiran kroz `monkeypatch` na `_run_ytdlp`)** — `test_allowed_source_by_handle`, `test_rejects_foreign_channel`, `test_pick_new_skips_known`.
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C3: ulaz iz kampanje, provjera kanala`.**

### Task 18: Orkestrator posla s nastavkom

**Files:**
- Create: `src/clipping/job.py`, `tests/test_job.py`

**Interfaces:**
- Consumes: sve gore.
- Produces: `run_job(profile, source: Path | str, *, db, root: Path, services: Services) -> JobResult` gdje `Services(transcribe, select, build_crop_path, export_clip, check_clip, download)` (dataclass funkcija, radi zamjene u testovima); koraci redom s imenima: `ulaz, zvuk, prijepis, tisine, prozor, izbor, rezanje, provjera, pregled`. Svaki korak: ako `last_done_korak` ≥ korak i artefakt postoji (za `prijepis`: `transcript.json` i `izvor.sha256` se slaže), preskoči. `rezanje` ide po isječku: red u `isjecak` sa statusom `izrezan` upisuje se tek nakon što je MP4 potpun (izvoz piše u `*.part.mp4` pa preimenuje); nastavak reže samo isječke bez reda ili bez datoteke. Radna mapa `izlaz/<posao>/` s `radno/` (wav, transcript.json, silences.json, window.txt, candidates.json), `isjecci/`, `dnevnik.log`. Duplikati: prije rezanja `published_ranges` → preklapanje > 50 % odbija kandidat s nalazom.

- [ ] **Step 1: Testovi (lažni servisi, sintetički video)** — `test_full_job_produces_clips` (lažni `transcribe` vraća fiksni prijepis, lažni `select` 2 kandidata → 2 MP4, `PREGLED.md` postoji), `test_resume_skips_transcribe` (prvi prolaz, obriši `isjecci/`, drugi prolaz: `transcribe` pozvan 0 puta), `test_resume_skips_rendered_clips` (lažni `export_clip` diže nakon prvog isječka; drugi prolaz izvozi samo drugi), `test_partial_file_is_rerendered` (ostavi `x.part.mp4` → ponovno rezanje), `test_duplicate_over_half_rejected` (seed `published_ranges`).
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C3: orkestrator posla s nastavkom`.**

### Task 19: Neovisni Claude pregled i `PREGLED.md`

**Files:**
- Create: `src/clipping/review.py`, `src/clipping/select/review_prompt.md`, `tests/test_review.py`

**Interfaces:**
- Produces: `independent_review(clip_text: str, profile, thumbnails: list[Path], *, runner=run_claude) -> Review(ocjena: int, problemi: list[str])` (shema JSON; prompt: brief pravila, tekst isječka, putanje sličica; ne blokira, ide u izvještaj); `write_pregled(posao_dir: Path, rows: list[PregledRow]) -> Path` (`PREGLED.md`: tablica isječak | trajanje | stil | platforme | udica | ocjena Claudea | pregled | QA nalazi; na vrhu upute: „`clipping odobri <posao>` ili `clipping odobri <posao> --izbaci 3,7`“).

- [ ] **Step 1: Testovi** — `test_pregled_table_has_all_clips`, `test_review_parses_fake_runner`, `test_kreni_refuses_platform_not_in_profile` (u `cli`: `--platforma youtube` za profil bez youtube → exit 2, poruka).
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C3: neovisni pregled i PREGLED.md`.**

### Task 20: `clipping kreni` i `clipping odobri` + mobitel

**Files:**
- Modify: `src/clipping/cli.py`; Create: `src/clipping/approve.py`, `tests/test_approve.py`, `tests/test_cli_kreni.py`

**Interfaces:**
- `kreni(kampanja: str, izvor: str | None, root: Path = Path("."))`: učita `kampanje/<slug>.yaml`, `Database(root/"data"/"clipping.db")`, izvor = `--izvor` (provjera `is_allowed_source`) ili `pick_new_video`; `run_job`; ispiše putanju `PREGLED.md`.
- `approve(posao_id, *, izbaci: set[int], db, root) -> ApproveResult`: piše `izlaz/<posao>/ODOBRENO.txt` (izbačeni id-evi po retku, prazno = svi), statusi `odobren`/`izbacen`; za svaki odobren isječak i svaku platformu iz `profile.platforme`: `mobitel/<platforma>_<racun>/<YYYYMMDD>-<slug>.mp4` (kopija) + `<isti>.opis.txt` (iz `opis.predlozak`: `{udica}`, `{url_izvora}`, `{hashtagovi}`; uvijek sadrži „Paid partnership with <kreator>“ i `#ad` kad `oznaka_placene_suradnje`). Račun prazan u profilu → mapa `mobitel/<platforma>_NEPOZNAT/` i upozorenje.

- [ ] **Step 1: Testovi** — `test_odobri_writes_file_and_statuses`, `test_mobitel_has_file_per_platform` (profil s 3 platforme, 2 odobrena → 6 MP4 + 6 opis.txt), `test_opis_contains_paid_partnership`, `test_kreni_end_to_end_with_fakes` (CliRunner + lažni servisi kroz env `CLIPPING_FAKE_SERVICES=1` ili `monkeypatch`).
- [ ] **Step 2: Pad → implementiraj → prolaz → commit `C3: naredbe kreni i odobri, mapa mobitel`.**

### Task 21: Dokaz C3 na zlatnom videu

- [ ] **Step 1:** `uv run clipping kreni --kampanja caleb-hammer --izvor https://www.youtube.com/watch?v=JvLklMRThYs` (izvor već u `data/izvori/`, `download` preskače ako `source.mp4` sa sha postoji). Zabilježi trajanje po koraku iz `dnevnik.log`.
- [ ] **Step 2:** Ponovi s `Ctrl+C` tijekom `rezanje` nakon 2 isječka, pa ponovno `kreni`: dnevnik pokazuje `prijepis: preskočen`, rezanje samo preostalih.
- [ ] **Step 3:** `uv run clipping odobri <posao> --izbaci <jedan id>`; provjeri `mobitel/`.
- [ ] **Step 4:** Dokumenti: `PLAN_V1.md` (C3 ✅ s vremenima), `BACKLOG.md`, `SLJEDECA_SESIJA.md` (sljedeće: Leon otvara račune; plan za C4/C5), ADR ako je nešto odstupilo. Commit `C3: dokaz na zlatnom videu`. STANI za Leonov OK.

---

## Samopregled (napravljen 4. 11. 2026.)

- **Pokrivenost dizajna:** §5 profil → Task 7; §6 koraci 1–9 → Tasks 17, 4, 5, 4, 16, 16, 8+10+11+12, 13+19, 19+20; §8 baza i statusi → Task 15, 18; §9 `kreni`/`claude -p` → Task 16, 20 (Task Scheduler i `objavi`/`prati` su C4/C5); §10 mjerenja → Tasks 6, 14, 21; §11a 1 → Task 17, 3 → Task 9+11, 4 → Task 20, 6 → Task 7+11, 8 → Task 18. Korak 10–12 (objava, prijava, praćenje) namjerno izvan plana.
- **Tipovi:** `Candidate` polja (`start_word_index`, `end_word_index`, `naslov`, `udica`, `ocjena`, `razlog`, `opis`) ista u Tasks 8, 16, 18, 20; `Watermark` iz Task 7 koristi Task 12 i 13; `Services` u Task 18 nosi imena funkcija iz Tasks 5, 10, 12, 13, 16, 17.
- **Fokus pregleda:** svih pet ima test u zadatku vlasniku.
- **Proporcija:** plan ~330 redaka prema ~260 redaka dizajna; tijela funkcija su samo tamo gdje potpis ne određuje algoritam (tokeni u riječi, lanac filtera, pravila nastavka).
