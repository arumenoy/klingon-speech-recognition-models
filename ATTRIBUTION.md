# Attribution and training provenance

## Distributed model components

- **ZIPA Large**: Jian Zhu, Farhan Samir, Eleanor Chodroff and David R. Mortensen. [Original project](https://github.com/lingjzhu/zipa), [paper](https://aclanthology.org/2025.acl-long.961/), [AnySpeech ONNX model](https://huggingface.co/anyspeech/zipa-large-crctc-500k). CC BY 4.0. The INT8 model is retained unchanged, renamed `zipa.onnx`. Source revision: `62c7a6e31f5035045de2538448a46b037948a206`.
- **SenseVoiceSmall**: FunAudioLLM / Alibaba Group. [Model](https://huggingface.co/FunAudioLLM/SenseVoiceSmall), [model license](https://github.com/modelscope/FunASR/blob/main/MODEL_LICENSE). The graph was cut to an acoustic encoder prefix (first seventeen encoder blocks); upstream weights were frozen. The metadata, CMVN parameters and original model identity remain present. File: `sensevoice-prefix.onnx`.
- **Klingon CTC readers and character language model**: learned for the Hitokoto project by Takahiro Yonemura with AI-assisted development. These are additional networks, not claims of authorship of ZIPA or SenseVoiceSmall.
- **boQwI' dictionary data**: Copyright (C) 2014 De'vID jonpIn (David Yonge-Mallo) and contributors. [Repository](https://github.com/De7vID/klingon-assistant-data), revision `0f6018ece74a3f5a4b61ddcd4c7a28b010bb7fd0`, Apache-2.0. Entry names, parts of speech and affixes from `mem-01` through `mem-26` were extracted for recognition. Definitions and example sentences were excluded. The optional extra section was not included. This is a vocabulary/morphology aid, not a complete Klingon grammar or a sentence whitelist.

## Training and evaluation sources — recordings are not included

- **Klingon TTS syllables**: Copyright (C) 2014 De'vID jonpIn (David Yonge-Mallo), Apache-2.0. [Source](https://github.com/De7vID/klingon-assistant-tts-android). Synthetic utterances and acoustic augmentation were generated from the licensed syllable bank.
- **Kokoro-82M**: hexgrad, Apache-2.0. [Model](https://huggingface.co/hexgrad/Kokoro-82M). Phoneme-directed synthetic examples approximate pronunciation; they are not recordings of native Klingon speakers. The Kokoro model and generated waveforms are not distributed here.
- **Tatoeba texts**: Tatoeba contributors, [CC BY 2.0 FR](licenses/CC-BY-2.0-FR.txt). [Klingon text export](https://downloads.tatoeba.org/exports/per_language/tlh/tlh_sentences_detailed.tsv.bz2). Punctuation was normalized for character-language-model learning and word statistics. Source sentence IDs, authors and links are in `text-source-attribution.json`, without the sentence texts. Contributors include Balamax, Choctaw_Irish, Eduzitos, IronBeagle, Katjo_Mencanto, Klingonteacher, NigerianSmiths, Tepan, Vortarulo, Ziggurat, allefy, bcmoney, chaDQI, cntrational, fergusq, jdmcowan, loghaD, payqagh, pne, polski_ren, qurgh, rul, shekitten, turklehceleri and zrajm; some source author fields are unspecified.
- **Tatoeba speech**: rul (Rívkala), CC BY 4.0. [Contributor profile](https://tatoeba.org/user/profile/rul). Audio was resampled for acoustic training or evaluation according to the local split records.
- **RhinoSpike speech/text**: jurcik, [request 4665](https://rhinospike.com/audio_requests/jurcik/4665/) for training and [request 4406](https://rhinospike.com/audio_requests/jurcik/4406/) for development, [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) under the [site terms](https://rhinospike.com/about/terms/). Processing included resampling, segmentation and training-only speed/channel/noise augmentation.
- **Klingon Language Institute**: six recordings from the [Klingon Phrases page](https://www.kli.org/about-klingon/klingon-phrases/) were used for local acoustic learning; other saved clips were used for checks. **No open-data license is asserted for these recordings.**
- **deznil speech/transcript corpus, published by dadap**: [source repository](https://github.com/dadap/tlhIngan-Hol-QIch-wab-tamey), revision `f4f863b950bacc18090a3a7ef11f286c5767a2d4`. 101 recordings were used for local acoustic learning. **No open-data license is asserted for this source.**
- **Developer-provided speech** was supplied for pronunciation adaptation. The original recordings, personal file names and recording paths are not published.
- **Microsoft SAPI voices** provided additional synthetic evaluation examples; those evaluation waveforms were not used for weight updates and are not published.

The locally developed models analyze sound-to-writing correspondences. They do not synthesize or play back the source speakers' recordings. Use of the two sources without declared open licenses was recorded as non-enjoyment information analysis in Japan, not as acquisition of an open-data license. [Agency for Cultural Affairs guidance](https://www.bunka.go.jp/seisaku/chosakuken/aiandcopyright.html) provides the relevant context; this notice does not claim that all conceivable uses in every jurisdiction are cleared. The release does not offer those source recordings or transcript corpora for redistribution.

## Runtime dependencies

The original integration uses ONNX Runtime (Microsoft, MIT) and kaldi-native-fbank (Apache-2.0, with its dependency notices). Their binaries and source code are not included in this model-only release. A consuming application must comply with the licenses of the runtime libraries it chooses.

## 日本語

元モデル、辞書、学習・検査に使った音声や文章の出典を上に記載しています。KLIとdeznilの録音について、オープンデータとしての許諾があるとは表明していません。国内での音響情報解析の学習元として記録したもので、原音声・書き起こしコーパスを再配布する公開物ではありません。元の作者や団体の公認・推薦を意味しません。
