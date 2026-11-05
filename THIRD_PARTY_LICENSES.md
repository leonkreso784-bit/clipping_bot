# Licence trećih strana

## artbyjazi/autoclip (MIT) — uzor, ne ovisnost (ADR-009)

Moduli za kadriranje po licu, granice rezova, ASS titlove i izvoz pišu se po uzoru na
<https://github.com/artbyjazi/autoclip>. Svaka takva datoteka nosi zaglavlje
`# Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi)`.

```text
MIT License

Copyright (c) 2026 Jad Ghazi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## NVIDIA Parakeet TDT 0.6B v3 (CC-BY-4.0) — težine modela za prijepis (ADR-008)

Model: <https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3> (NVIDIA Corporation), ONNX pretvorba
<https://huggingface.co/istupakov/parakeet-tdt-0.6b-v3-onnx> (Ilya Stupakov), licenca CC-BY-4.0
<https://creativecommons.org/licenses/by/4.0/>. Koristi se nepromijenjen, lokalno, za prijepis govora.
Silero VAD kroz `istupakov/silero-vad-onnx` (MIT, Silero Team).

## Fontovi Anton i Inter (SIL Open Font License 1.1) — titlovi (C2)

`src/clipping/assets/fonts/Anton-Regular.ttf` (Copyright 2020 The Anton Project Authors,
<https://github.com/googlefonts/AntonFont.git>) i `Inter-Variable.ttf` (Copyright (c) 2016 The Inter Project
Authors, <https://github.com/rsms/inter>). Puni tekst licence: `OFL-Anton.txt` i `OFL-Inter.txt` u istoj mapi.
OFL dopušta ugradnju u video i komercijalnu uporabu; fontovi se ne prodaju zasebno.

## MediaPipe `face_landmarker.task` (Apache-2.0) — kadriranje po licu (C2)

Model Google LLC, <https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task>,
licenca Apache-2.0 (kartica modela MediaPipe Face Landmarker). Skida ga `clipping.models_dl` u `models/`
(izvan gita), 3 758 596 bajtova.

## autoclip moduli prepisani u C2

Po uzoru na artbyjazi/autoclip (MIT, gore): `boundaries.py`, `captions.py`, `export.py`, `reframe/*`
(croppath, faces, tracker, scenes, smoothing, speaker). Svaki nosi zaglavlje s izvorom; diarizacija,
LLM sloj, baza i web sučelje nisu preuzeti.

## tqdm 4.70.1 (MPL-2.0 AND MIT) i certifi 2026.10.23 (MPL-2.0) — posredne ovisnosti

`tqdm` dolazi kroz `huggingface-hub` samo za traku napretka pri skidanju modela; `certifi` je snop CA
certifikata za HTTPS. Ne mijenjaju se i ne uključuju u naš kod. MPL-2.0 nije na popisu u pravilu 8
(MIT, Apache-2.0, BSD): **Leon odlučuje** ostaju li (zapis u `docs/records/BACKLOG.md`, „Čeka Leona").

Fontovi i `face_landmarker.task` dodaju se u C2.
