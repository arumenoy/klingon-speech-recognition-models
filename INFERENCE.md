# Inference specification

This specification describes how to feed the released ONNX networks. It is intended for developers who are implementing a recognizer. No application source or executable runtime is included. **Read the tensor schemas in `model-manifest.json`; these are not five interchangeable raw-audio models.**

## 1. Audio and trimming

Decode/resample audio to **16,000 Hz, mono, signed int16**. Preserve amplitude; do not independently normalize each spectral frame. The reference accepts 400 to 480,000 samples (25 ms to 30 seconds) before trimming. A host microphone/VAD layer may impose its own stricter speech checks.

For reference trimming, calculate RMS over each complete 160-sample block. Let `peak` be the largest RMS and `threshold = max(45, 0.035 * peak)`. Find the first and last blocks whose RMS reaches the threshold. Retain samples from `max(0, (first - 3) * 160)` through `min(length, (last + 4) * 160)`, end exclusive. If there is no qualifying block, return no speech. If fewer than 400 samples remain, do not decode a transcript.

## 2. Filterbanks

Use Kaldi-compatible **log-power filterbank** features. The tested implementation uses `kaldi-native-fbank`. Both branches use 16 kHz, 25 ms windows, 10 ms shifts, 80 mel bins, zero dither, pre-emphasis 0.97, DC removal, power-of-two FFT sizing (512), low frequency 20 Hz, no appended energy, and the library's standard Kaldi mel implementation. Do not substitute a default librosa mel spectrogram: windowing, scaling and frame edges differ. Preserve the library's standard options except the branch overrides below.

| Option | SenseVoice branch | ZIPA branch |
| --- | --- | --- |
| Input float waveform | int16 values converted to float, unchanged scale | int16 converted to float and divided by 32768 |
| Zero padding | none | 1440 samples left, 1920 right |
| Window | `hamming` | `povey` |
| `snip_edges` | true | false |
| High frequency | 0 (Nyquist, 8000 Hz) | -400 (Nyquist minus 400 = 7600 Hz) |

For SenseVoice, let `M` be the unstacked frame count, `N = ceil(M / 6)`, and `F` the `[M,80]` matrix. Form `L[N,560]` by concatenating seven frames for each row `i`: `F[clip(6*i + c - 3, 0, M-1)]` for `c = 0..6`. Read the 560-element comma-separated `neg_mean` and `inv_stddev` values from `sensevoice-prefix.onnx` metadata. Normalize `L = (L + neg_mean) * inv_stddev` in float32.

## 3. Frozen encoder inference

**SenseVoiceSmall prefix:** feed `x = L[None,:,:]` (float32), `x_length = [N]` (int32), `language = [0]` (int32), and `text_norm = [14]` (int32). The output is `[1,N+4,512]`. Discard its first four frames. The remaining matrix is `H[N,512]`.

**ZIPA Large:** feed its padded 80-bin features as `x[1,P,80]` (float32) and `x_lens = [P]` (int64). Use the first output, `[1,Q,127]`, as phonetic logits `Z[Q,127]`. Softmax over the last dimension, then take the square root: `R = sqrt(softmax(Z))`. Compute the softmax stably; the reference uses double-precision arithmetic for the probabilities.

## 4. The 722-dimensional reader input

Build `X[3*N,722]`. For each SenseVoice frame `i` and phase `p in {0,1,2}`:

1. `X[3*i+p,0:512] = H[i] / sqrt(mean(H[i]^2) + 1e-6)`.
2. `X[3*i+p,512:592] = 0.25 * L[i,(1+2*p)*80:(2+2*p)*80]`.
3. `X[3*i+p,592:595]` is the three-element one-hot vector for phase `p`.
4. For the 127 phonetic dimensions, compute `m = clip(6*i - 2 + 2*p, 0, M-1)`, `position = (0.01*m + 0.0125 + 0.045) / 0.02`, `left = clip(floor(position), 0, Q-1)`, `right = min(Q-1,left+1)`, and `mix = clip(position-left,0,1)`. Set `X[3*i+p,595:722] = (1-mix)*R[left] + mix*R[right]`.
5. Round every feature to IEEE float16 (nearest, ties-to-even), then convert back to float32. This matches the feature precision used during training.

This timing uses the trimmed utterance, not its original position in a larger recording. **Do not multiply the phonetic dimensions by 8 yourself:** that scaling is already inside the exported reader graphs.

## 5. CTC readers and text

Feed `frames = X[None,:,:]` to `reader.onnx` or `accent-reader.onnx`. Each returns logits of shape `[1,3*N,28]`. Both accept a variable number of frames but have an acoustic batch size of one. They use full-utterance bidirectional context.

The 28 output IDs are specified in `tokens.json`. ID 0 is CTC blank. The remaining IDs are:

`1 a`, `2 b`, `3 ch`, `4 D`, `5 e`, `6 gh`, `7 H`, `8 I`, `9 j`, `10 l`, `11 m`, `12 n`, `13 ng`, `14 o`, `15 p`, `16 q`, `17 Q`, `18 r`, `19 S`, `20 t`, `21 tlh`, `22 u`, `23 v`, `24 w`, `25 y`, `26 '`, `27 space`.

A minimal baseline is CTC greedy decoding: take argmax at every frame, collapse adjacent identical IDs **before** removing blank IDs, join the symbols, remove leading/trailing spaces and collapse repeated spaces. A blank between two identical nonblank IDs allows both symbols to survive. Do not lowercase the result, strip apostrophes, or split `tlh/ch/gh/ng` into Latin characters when passing token IDs to the language model.

The two readers are distinct model choices; the adapted reader is not universally superior. A minimal implementation can expose both transcripts. Averaging their logits was not the final application selection method.

## 6. Optional learned language-model rescoring

Use conventional CTC prefix beam search to generate candidate token sequences. The reference baseline keeps 48 prefixes per frame, considers the best eight nonblank labels, discards nonblank labels more than 11 log-probability units below the best frame label, and sums alternative CTC paths in log space.

For candidate token IDs `y[0:n]` (already CTC-collapsed), feed `[28] + y` as `ids` (int64) to `language.onnx`. ID 28 is BOS, 29 is EOS. Its output logits have 30 classes. Score each next token at its corresponding position, including EOS at position `n`:

`LM(y) = sum(t=0..n-1, logsoftmax(output[t])[y[t]]) + logsoftmax(output[n])[29]`.

The reference score is `CTC_log_probability(y) + 1.0 * (LM(y) + 2.0 * n)`. If batching different lengths, right-pad with 0 and ignore padded positions when calculating the score. The model is causal, so right-padding does not change the earlier valid positions.

Language rescoring is optional; it can improve plausible text and can also bias the output toward a wrong but familiar word. Greedy decoding and language rescoring are different operating points.

## 7. Optional dictionary and application-style selection

`models/lexicon.tsv` is provided as data for developers who want dictionary/morphology assistance. It is not a lookup table of allowed sentences. The first field identifies a record type:

| Type | Fields following type |
| --- | --- |
| `CONFIG` | unknown-word penalty, context weight, word reward, maximum acoustic-score drop |
| `TOTAL` | normalization count for unigram smoothing |
| `B` | dictionary word, bit flags (noun=1, verb=2, adverb=4, stative=8) |
| `W` | observed word form |
| `P` | verb prefix (an empty field represents the empty prefix) |
| `N`, `V` | noun/verb suffix, type/category identifier |
| `F` | word, count |
| `G` | previous word, next word, pair count |
| `C` | previous word, context count |

Morphological validation must respect Klingon affix ordering and lexical categories; not every concatenation of listed pieces is valid. Implementing the application's morphology validator and its UI repair rules is outside this model-only distribution.

The application's general approach was to preserve a baseline candidate composed of valid words, seek alternatives when unknown words occurred, and limit acoustic-score degradation to 8.0. The auxiliary lexical search used width 64 and an unknown-word potential of -6.0. After separate decoding of both acoustic readers, it preferred fewer unknown words; if both had zero unknown words, it selected the adapted result only when its word-context score exceeded the original by the `accent.tsv` margin (0.0).

For a sequence of words with `<s>` and `</s>` boundaries, its context score sums the log of `(pair_count(previous, word) + 4*u(word)) / (context_count(previous) + 4)`. Here `u(</s>) = 0.12`, otherwise `u(word) = (word_count(word)+1)/TOTAL`. Dictionary evidence is `-2*unknown_words + 0.25*(context_score + 11*word_count)`. `decoder.tsv` contains LM weight, length reward and the application's greedy-mode flag.

These notes identify the operating point of the saved application evaluations. A consumer's decoder and morphology implementation may differ. The application also preserves raw text when applying a narrow terminal-apostrophe repair; that UI/postprocessing implementation is not an extra neural model and is not shipped here.

## 8. Runtime notes

ONNX Runtime CPU 1.31.x was used for integration. The exported graphs use standard ONNX and Microsoft quantization operators supported by that runtime. No external tensor-data files or custom native operator libraries are required by the five models. The acoustic front end is a separate computation.

Use the model metadata and manifest rather than guessed tensor names. Two intra-op threads, one inter-op thread and disabled spinning were used in the mobile integration. Different implementations and numeric kernels can change close decisions. Validate with your own microphones and speakers.

For silence, very short or overlong input, return an explicit no-speech/invalid-input state before inference. For long recordings, segment into utterances and recognize each segment. This bundle does not provide a continuous microphone loop, VAD model, or streaming state.

## 日本語

16kHzモノラル音声から2種類の音響特徴を作り、SenseVoiceSmallとZIPAを通し、位置合わせした722次元の特徴を読取りモデルへ渡します。読取りモデルの出力は28種類の文字単位のスコアです。CTC方式で重複と空白記号を処理し、クリンゴン語の文字列へ戻してください。必要に応じて文字言語モデルや辞書を利用できます。大文字・小文字とアポストロフィは維持します。

上記はモデルを利用するための仕様書です。アプリ本体のコードは含まれません。貪欲復号だけでも文字出力は可能ですが、アプリの辞書補助等を含む検査結果と同一の精度を意味しません。
