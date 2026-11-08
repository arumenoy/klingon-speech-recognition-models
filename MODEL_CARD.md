# Model card — v1.0.0

## Purpose and architecture

Offline Klingon speech-to-text for developer experiments and entertainment applications. Input is a bounded utterance of 16 kHz mono audio; output is Klingon text. The token vocabulary contains a CTC blank, 26 Klingon writing units and a space. Capitalization is significant. The recognizer is not a general conversational AI and does not translate text.

Two frozen pretrained encoders, SenseVoiceSmall's acoustic prefix and ZIPA Large, provide the acoustic representation. A locally trained bidirectional recurrent CTC reader maps the combined 722-dimensional frame features to 28 logits. A second reader was adapted using pronunciation variation. A separate character language model can rescore hypotheses. Optional dictionary and word-context statistics support the application decoder.

The files are the existing v23 acoustic-pair model revision used by the Android integration, packaged as the first public release on 2026-11-08. No new training occurred merely to produce this download. The large upstream encoders were not trained from scratch by this project.

## Training summary

The training set combines licensed synthesized syllable speech, phoneme-directed Kokoro synthesis, a small amount of human speech, and text-language-model training. The accent adaptation used 108 synthetic pronunciation examples, one developer recording with nine original/augmented views, and replay of 2,193 prior training examples. These counts are examples, not independent speakers. The two encoders remained frozen. See [ATTRIBUTION.md](ATTRIBUTION.md) for provenance and source-specific licensing qualifications.

## What was measured

The saved internal v23 Android evaluation used the application's complete feature, beam-search, language-model, dictionary and reader-selection pipeline:

| Evaluation subset | Exact transcripts | Qualification |
| --- | ---: | --- |
| Held human recordings | 25 / 38 | Separate recordings; includes previously encountered speakers. Not an entirely unseen-speaker benchmark. |
| Sentence development set | 65 / 67 | Existing material, including synthetic/edited speech. Not blind testing. |
| Additional Japanese-katakana SAPI synthesis | 14 / 32 | Synthetic voices not used for acoustic weight updates; not 32 humans. |
| One-word-change and other synthetic contrasts | 41 / 44 | Limited saved synthetic comparison set. |

The adapted reader also transcribed the supplied developer recording as `tlhIngan Hol vIjatlh`. That recording was used for adaptation and is explicitly **not** independent validation. The KLI target sentence `Heghlu'meH QaQ jajvam` was transcribed in six saved original/modified conditions; these are variations of one recording, not six independent speakers or a novel-sentence benchmark.

The v25 integration replayed 25 saved audio inputs on an Android API 30 x86_64 emulator with airplane mode enabled, with no differences from the recorded expected raw/corrected output and result status. That verifies the integration replay, not 100% speech-recognition accuracy. A prior 362-case Python/Android comparison had one differing, incorrect synthetic-speech output; it is not represented as perfect cross-platform agreement.

**The table is application-pipeline evidence, not a benchmark for simply running greedy CTC on the released readers.** A new decoder, feature implementation, device or speaker can change the result. Source recordings, private developer data and application source are outside this release, so this is a transparent summary of saved internal checks rather than a fully reproducible public benchmark dataset.

## Practical limits

- Limited human speech and limited speaker diversity; synthetic speech makes up much of the training material.
- Pronunciation variation, unfamiliar words, microphone conditions, clipping, noise and shouting can change recognition substantially.
- Language and dictionary priors can prefer a plausible but incorrect word. Keep the raw transcript when applying corrections.
- Speech segmentation and no-speech detection must be provided by the host. Do not force silent input through a decoder and treat its output as recognized speech.
- Process utterances up to 30 seconds using the documented pipeline. Batch-one acoustic readers use full-utterance context; this is not a streaming recognizer.
- The original Android API 30 x86_64 laboratory integration was measured around 887 MiB PSS when ready. That is one historical observation, not a memory ceiling or a measurement on every ARM64 phone.
- Physical smartphone performance across devices and broad native-speaker accuracy have not been established by these checks.

## 日本語での要点

モデルは、音声からクリンゴン語の文字列を推定するためのものです。固定フレーズの選択器ではありません。既存の2つの音声モデルを土台に、小規模なクリンゴン語用モデルを学習しました。

上の数値は辞書等を含めたアプリの内部検査です。学習に使った録音、別録音、合成声を区別しており、新しい話者や新しい実装で同じ精度を保証するものではありません。原音声とアプリ本体のソースは公開対象に含みません。実装時は入出力仕様を合わせ、実際の使用条件で評価してください。
