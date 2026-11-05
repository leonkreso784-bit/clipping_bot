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

Fontovi i `face_landmarker.task` dodaju se u C2.
