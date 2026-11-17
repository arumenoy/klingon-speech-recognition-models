# Windows integration — Hitokoto Translate Klingon 0.1.4

This is documentation for the Windows application runtime, not a claim that the five public ONNX files form a standalone WAV-to-text API. The public model release and application versions must be distinguished. This runtime ports Android 1.3.5 (33); its configuration and routing can differ from model-only release 1.0.0.

[日本語](WINDOWS-ja.md) · [Windows application](https://inazuma7.itch.io/hitokoto-translate-klingon)

## Offline components

- Recognition: SenseVoice features, ZIPA phonetic features, learned Klingon CTC readers and language rescoring. CPU inference through bundled ONNX Runtime.
- Automatic selection: Japanese/Klingon with Japanese UI; English/Klingon with English UI. Forced recognition modes remain available.
- Translation: bundled translation models; no phrase-to-translation lookup substitute.
- Japanese/English speech: bundled MagpieTTS v2607 Q8 + NanoCodec, Sofia speaker 4, the Guardian Beast Windows engine. No Windows system voices or cloud TTS.
- Klingon speech: the existing bundled syllable synthesis. Magpie is not presented as a Klingon TTS model.

## Calling the bundled executable

Extract the entire Windows package. Keep `Hitokoto-Klingon.exe`, `runtime`, `lib`, `native`, `assets` and `magpie` together. No separate Java or Python installation is needed to run the GUI. The optional Python sample needs Python 3.

Call the executable with `--engine` and an absolute UTF-8 JSON request path. Capture stdout as UTF-8; it contains one JSON event per line. Read through the final `result` or `error` event and inspect the exit code.

```json
{"audio":"C:/audio/utterance.wav","mode":"tlh","ui":"en","recognitionOnly":true}
```

Use a mono 16-bit PCM WAV at 16,000 Hz, up to 10 seconds. No expected transcript is supplied. `mode: auto` enables selection against the language in `ui` (`en` or `ja`). `mode: tlh` forces Klingon recognition. A withheld utterance returns `unclear: true`; do not treat this as an empty successful transcription.

For translation and speech, omit `recognitionOnly` and supply an absolute writable `output` WAV path. Use `noVoice: true` for translation without speech. Text input uses `text`, `language` (`tlh`, `ja`, `en`) and `ui` instead of `audio`.

```python
subprocess.run([exe, "--engine", request_json], capture_output=True,
               encoding="utf-8", timeout=240)
```

The `recognize_windows.py` example validates WAV format, uses a private temporary request, and reports the result. It depends on the application package; it does not download models or expose proprietary application source. For a separate ONNX implementation, follow the public repository's INFERENCE.md and model-manifest.json.

## Lifecycle and privacy

Keep inference off the UI thread. Stop must terminate the inference process and its descendants (speech generation is a native worker). Discard late events from cancelled turns. The GUI uses an epoch counter and a bounded worker timeout. Store temporary recordings in a private session directory; normal exit removes them. A forced termination can leave temporary files.

Microphone privacy denial, endpoint mute/zero volume, and absent default capture endpoint are distinguished. An unknown device state is not labelled muted. Hardware-only mute switches may not expose their state to Windows. The app does not change microphone permissions.

## Validation boundary — 2026-11-16

Earlier recognition parity: 36 recorded cases matched Android routing/transcripts; this is parity, not 100% recognition accuracy. On this build, three fresh end-to-end recorded cases (Qapla', Japanese hello, English hello) completed recognition, routing, translation and WAV generation through the bundled EXE/runtime. Two additional typed Klingon cases produced Japanese and English Magpie audio. Generation of those short Magpie examples took approximately 2.3–3.0 seconds on the development PC; full recorded turns took approximately 12–16 seconds. These are examples, not universal latency promises.

Headless UI checks cover English default, Japanese switching, routing labels, microphone warning states and Stop. UI previews are rendered controls with fixture text, not microphone recognition evidence. These headless checks do not measure live microphone performance.

## Distribution boundary

Public integration documentation and the small caller sample do not grant redistribution rights to all app components. Preserve the per-component license documents. Never include private recordings, training programs, signing keys, QA fixtures or proprietary application sources in the public model repository. The Windows application is a separate binary package; the public ONNX model bundle remains model-only.


## 0.1.4 portability and automatic operation

The EXE embeds its icon and initializes the bundled JVM directly through the Unicode Windows APIs. It does not invoke the stock java.exe launcher. SentencePiece model files are opened through wide filesystem paths and loaded from serialized bytes. The UI starts listening automatically; silence and playback return to listening. A pause control remains available.

Japanese, Korean, accented Latin letters, spaces and punctuation were tested in the installation path. A 186-character application directory, with bundled resource paths up to 284 characters, and a multilingual temporary directory completed recognition, translation and speech generation. Test aliases were NTFS junctions to avoid copying large models; requests used the alias paths. OS-level restrictions on launching executables still apply. The UI worker pipeline was tested headlessly with actual inference and generated audio, replacing microphone capture and speaker playback with test doubles. This is not a live microphone test.

