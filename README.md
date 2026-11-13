# Klingon Speech Recognition Models

**Learned models for turning spoken Klingon into written Klingon, offline.**

[日本語](README-ja.md) · [Download models](https://github.com/arumenoy/klingon-speech-recognition-models/releases/latest) · [Model card](MODEL_CARD.md) · [Input/output specification](INFERENCE.md) · [Licenses](LICENSE.md)

Klingon is a small language community with an unusually interesting sound system. This release shares the recognition models developed for the **Hitokoto Alien Talk / ひとこと異星人語** Android translator, so other developers and enthusiasts can explore their own applications.

The recognizer predicts a sequence of Klingon writing units. It does not select from a fixed list of permitted sentences, and inference does not take an expected transcript. It is a speech-recognition model bundle, not an LLM or a text-to-speech model.

## Try it on Android

These models power on-device Klingon speech recognition in **Hitokoto Translate Klingon**, a free offline Android translation app. You can speak Klingon into the app and see what it transcribes.

[Try Hitokoto Translate Klingon on Google Play](https://play.google.com/store/apps/details?id=jp.co.inazuma.hitokoto.alien&hl=en)

## Download

Open **[Releases](https://github.com/arumenoy/klingon-speech-recognition-models/releases/latest)** and download `klingon-asr-models-v1.0.0.zip`. Verify its SHA-256 against the accompanying `SHA256SUMS.txt` and extract the archive.

The archive contains five ONNX models, token/configuration files, optional dictionary data, documentation and third-party notices. The five models total **376,791,520 bytes** before compression. The models are byte-for-byte identical to those packaged in the translator's version 1.3.2 update.

This is a **model-only release**. The translator application's source, training programs, microphone UI, translation models, speech-synthesis models, source recordings and signing keys are not part of this repository or its releases.

## What developers receive

| File | Role |
| --- | --- |
| `sensevoice-prefix.onnx` | Frozen SenseVoiceSmall acoustic encoder prefix |
| `zipa.onnx` | Frozen ZIPA Large INT8 phonetic encoder |
| `reader.onnx` | Learned Klingon CTC character reader |
| `accent-reader.onnx` | Additional reader adapted with pronunciation variation |
| `language.onnx` | Klingon character language model for candidate rescoring |

The waveform front end, feature alignment and token decoding are specified in **[INFERENCE.md](INFERENCE.md)**. ONNX input names, tensor shapes, model hashes and per-file licenses are in **[model-manifest.json](model-manifest.json)**. A developer must implement that pipeline or connect an equivalent runtime; these five files are not a single raw-WAV-to-text API.

The original integration runs on Android using ONNX Runtime and on-device audio features. This release has no cloud-service dependency. Acquisition of the files requires a download; inference can subsequently run offline.

## Recognition quality

The models were developed from a small mixture of human recordings and synthetic pronunciation examples. Accuracy varies with speaker, pronunciation, recording conditions and sentence. Klingon letter case and apostrophes are significant. Unfamiliar speech can produce incorrect words, including plausible-looking ones.

Our model card separates previously used recordings, held recordings and synthetic examples. Application-level measurements include decoding and dictionary assistance; they are not an accuracy promise for a new implementation or an unseen speaker. Please report recognition examples and recording conditions rather than assuming every error is the speaker's fault.

## Credits and reuse

The Klingon readers, character language model and release documentation are offered under **CC BY 4.0** for the publisher's contributions. ZIPA, SenseVoiceSmall and dictionary material retain their respective terms. **[LICENSE.md](LICENSE.md)** and **[ATTRIBUTION.md](ATTRIBUTION.md)** explain the component boundaries and training provenance.

Developed and published by **Takahiro Yonemura / arumenoy**, for the Hitokoto project. An application of these models is introduced on the [Hitokoto Translate project page](https://inazuma7.co.jp/hitokoto/index.html).

Independent, unofficial project. Klingon, Star Trek and related marks belong to their respective owners. No affiliation or endorsement by the franchise owners, the Klingon Language Institute, or the upstream model/data authors is claimed.
