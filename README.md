# opencc_jieba_pyo3

[![PyPI version](https://img.shields.io/pypi/v/opencc-jieba-pyo3.svg)](https://pypi.org/project/opencc-jieba-pyo3/)
[![Downloads](https://static.pepy.tech/personalized-badge/opencc-jieba-pyo3?period=month&units=international_system&left_color=gray&right_color=blue&left_text=PyPI%20Downloads)](https://pepy.tech/project/opencc-jieba-pyo3)
[![Python Versions](https://img.shields.io/pypi/pyversions/opencc-jieba-pyo3.svg)](https://pypi.org/project/opencc-jieba-pyo3/)
[![License](https://img.shields.io/github/license/laisuk/opencc_jieba_pyo3)](https://github.com/laisuk/opencc_jieba_pyo3/blob/main/LICENSE)
[![Build Status](https://github.com/laisuk/opencc_jieba_pyo3/actions/workflows/build.yml/badge.svg)](https://github.com/laisuk/opencc_jieba_pyo3/actions/workflows/build.yml)

`opencc_jieba_pyo3` is a Python extension module powered
by [Rust](https://www.rust-lang.org/), [Jieba](https://github.com/fxsjy/jieba) and [PyO3](https://pyo3.rs/), providing
fast and accurate conversion between different Chinese text variants
using [opencc-jieba-rs](https://github.com/laisuk/opencc-jieba-rs) and [OpenCC](https://github.com/BYVoid/OpenCC)
algorithms.

## Features

- Convert between Simplified, Traditional, Hong Kong, Taiwan, and Japanese Kanji Chinese text.
- Fast and memory-efficient, leveraging Rust's performance.
- Easy-to-use Python API.
- Supports punctuation conversion and automatic text code detection.
- Chinese word (Both Traditional and Simplified) segmentation (Jieba).
- Keyword extraction (TF-IDF, TextRank).
- Utility functions for punctuation handling and language detection.
- Custom OpenCC conversion dictionaries from in-memory mappings or UTF-8 files.
- Jieba user dictionaries from structured entries or UTF-8 files.

---

## 🔁 Supported Conversion Configs

| Code    | Description                                    |
|---------|------------------------------------------------|
| `s2t`   | Simplified → Traditional                       |
| `t2s`   | Traditional → Simplified                       |
| `s2tw`  | Simplified → Traditional (Taiwan)              |
| `tw2s`  | Traditional (Taiwan) → Simplified              |
| `s2twp` | Simplified → Traditional (Taiwan) with idioms  |
| `tw2sp` | Traditional (Taiwan)  → Simplified with idioms |
| `s2hk`  | Simplified → Traditional (Hong Kong)           |
| `hk2s`  | Traditional (Hong Kong) → Simplified           |
| `t2tw`  | Traditional → Traditional (Taiwan)             |
| `tw2t`  | Traditional (Taiwan) → Traditional             |
| `t2twp` | Traditional → Traditional (Taiwan) with idioms |
| `tw2tp` | Traditional (Taiwan) → Traditional with idioms |
| `t2hk`  | Traditional → Traditional (Hong Kong)          |
| `hk2t`  | Traditional (Hong Kong) → Traditional          |
| `t2jp`  | Japanese Kyujitai → Shinjitai                  |
| `jp2t`  | Japanese Shinjitai → Kyujitai                  |

---

## Installation

Build and install the Python wheel using [maturin](https://github.com/PyO3/maturin):

```sh
# In project root
maturin build --release
pip install ./target/wheels/opencc_jieba_pyo3-<version>-cp<pyver>-abi3-<platform>.whl
```

Or for development:

```sh
maturin develop -r
```

See [BUILD.md](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/BUILD.md) for detailed build and install
instructions.

---

## Usage

### Python

```python
from opencc_jieba_pyo3 import OpenCC

text = "“春眠不觉晓，处处闻啼鸟。”"
segment_text = "我独自来到无人海岸线"
opencc = OpenCC("s2t")
converted = opencc.convert(text, punctuation=True)
print(converted)  # 「春眠不覺曉，處處聞啼鳥。」

# Segmentation
words = opencc.jieba_cut(segment_text, hmm=True)
print(words)  # ['我', '独自', '来到', '无人', '海岸线']

# Segmentation and join
joined = opencc.jieba_segment_join(segment_text, mode="cut", delim="/")
print(joined)  # 我/独自/来到/无人/海岸线

joined = opencc.jieba_segment_join(segment_text, mode="search", delim="/")
print(joined)  # 我/独自/来到/无人/海岸/岸线/海岸线

joined = opencc.jieba_segment_join(segment_text, mode="full", delim="/")
print(joined)  # 我/独/独自/自/自来/来/来到/到/无/无人/人/人海/海/海岸/海岸线/岸/岸线/线

joined = opencc.jieba_segment_join(segment_text, mode="tag", delim=" ")
print(joined)  # 我/r 独自/d 来到/v 无人/n 海岸线/n

# Keyword extraction (TextRank)
keywords = opencc.jieba_keyword_extract_textrank(segment_text, top_k=3)
print(keywords)  # ['海岸线', '无人', '来到']

# Keyword extraction (TF-IDF)
keywords_tfidf = opencc.jieba_keyword_extract_tfidf(segment_text, top_k=3)
print(keywords_tfidf)  # ['海岸线', '独自', '无人']

# Keyword weights (TextRank)
kw_weights = opencc.jieba_keyword_weight_textrank(segment_text, top_k=3)
print(kw_weights)  # [('海岸线', 9987587364.22353), ('无人', 9986551019.39923), ('来到', 9985428148.988083)]

# Keyword weights (TF-IDF)
kw_weights_tfidf = opencc.jieba_keyword_weight_tfidf(segment_text, top_k=3)
print(kw_weights_tfidf)  # [('海岸线', 1.995445949425), ('独自', 1.8446462134525), ('无人', 1.7299179778125)]
```

---
## Custom dictionaries (v0.8.0, unreleased)

Version 0.8.0 adds two complementary dictionary layers:

- **Jieba user dictionaries** teach the tokenizer how to keep domain-specific words together and optionally assign a
  part-of-speech tag. They affect segmentation, tagging, and keyword extraction, but do not add OpenCC conversions.
- **Custom OpenCC dictionaries** add or replace mappings in a conversion-dictionary slot. They affect conversion, but
  do not change Jieba's tokenizer.

Both layers can be loaded into the same `OpenCC` instance. When a phrase needs custom segmentation and custom
conversion, load the Jieba entries first and the OpenCC mappings second.

### Public Python API

The package exports `UserDictEntry`, `CustomDictSpec`, and `CustomDictFileSpec` typed dictionaries:

```python
UserDictEntry = {"word": str, "freq": int, "tag": str}  # tag is optional
CustomDictSpec = {
    "slot": str,
    "pairs": list[tuple[str, str]],
    "mode": str,  # optional: "append" (default) or "override"
}
CustomDictFileSpec = {
    "slot": str,
    "files": list[str],
    "mode": str,  # optional: "append" (default) or "override"
}
```

`OpenCC` exposes these dictionary APIs:

- `OpenCC.from_user_dict_entries(config="s2t", entries=None) -> OpenCC`
- `OpenCC.from_user_dict_files(config="s2t", files=None) -> OpenCC`
- `OpenCC.from_dicts(config="s2t", specs=None) -> OpenCC`
- `OpenCC.from_dict_files(config="s2t", specs=None) -> OpenCC`
- `load_user_dict_entries(entries) -> None`
- `load_user_dict(path) -> None`
- `load_user_dict_files(files) -> None`
- `load_custom_dicts(specs) -> None`
- `load_custom_dict_files(specs) -> None`
- `OpenCC.available_slots() -> list[str]`

Use `OpenCC.available_slots()` to get the canonical OpenCC slot names accepted by `slot`. Slot matching is
case-insensitive; surrounding whitespace and an optional `.txt` suffix are accepted.

For a custom OpenCC dictionary, `append` merges entries into the selected slot and uses the last value when a source
key is duplicated. `override` clears the selected slot before inserting the supplied mappings. Custom mappings remain
attached to the instance when switching configs and take effect whenever the active config uses their slot.

### In-memory dictionaries

This example preserves a domain term as one Jieba token, gives it an `nz` tag, and adds a phrase conversion:

```python
from typing import List

from opencc_jieba_pyo3 import CustomDictSpec, OpenCC, UserDictEntry

user_dict: List[UserDictEntry] = [
  {"word": "帕兰蒂尔", "freq": 100_000, "tag": "nz"},
]
custom_dicts: List[CustomDictSpec] = [
  {
    "slot": "STPhrases",
    "pairs": [("帕兰蒂尔", "柏蘭蒂爾")],
    "mode": "append",
  }
]

cc = OpenCC.from_user_dict_entries(
  "s2t",
  user_dict,
)
cc.load_custom_dicts(custom_dicts)

print(cc.jieba_cut("帕兰蒂尔", hmm=False))
# ['帕兰蒂尔']
print(cc.jieba_tag("帕兰蒂尔", hmm=False))
# [('帕兰蒂尔', 'nz')]
print(cc.convert("帕兰蒂尔是一家公司"))
# 柏蘭蒂爾是一家公司
```

The equivalent post-load form is useful when the converter already exists:

```python
from typing import List

from opencc_jieba_pyo3 import CustomDictSpec, OpenCC, UserDictEntry

user_dict: List[UserDictEntry] = [
    {"word": "帕兰蒂尔", "freq": 100_000, "tag": "nz"},
]
custom_dicts: List[CustomDictSpec] = [
    {"slot": "STPhrases", "pairs": [("帕兰蒂尔", "柏蘭蒂爾")]},
]

cc = OpenCC("s2t")
cc.load_user_dict_entries(user_dict)
cc.load_custom_dicts(custom_dicts)
```

### Dictionary files

Jieba user-dictionary files are UTF-8 text using one entry per line. `freq` is required and `tag` is optional:

```text
word freq [tag]
帕兰蒂尔 100000 nz
```

Custom OpenCC dictionary files are UTF-8, tab-separated source/target mappings:

```text
帕兰蒂尔<TAB>柏蘭蒂爾
```

Load one or more files as follows:

```python
from typing import List

from opencc_jieba_pyo3 import CustomDictFileSpec, OpenCC

custom_dict_files: List[CustomDictFileSpec] = [
    {
        "slot": "STPhrases",
        "files": ["custom_st_phrases.txt"],
        "mode": "append",
    }
]

cc = OpenCC.from_user_dict_files("s2t", ["jieba_user_dict.txt"])
cc.load_custom_dict_files(custom_dict_files)

# A single Jieba file can also be loaded with:
cc.load_user_dict("another_user_dict.txt")
```

Multiple Jieba files are applied in the supplied order. Custom OpenCC files in a specification are parsed before that
specification is applied.

The same file-backed features are available to the `convert`, `segment`, and `office` commands. Repeat either option
to load multiple dictionaries:

```sh
opencc-jieba-pyo3 convert -c s2t \
  -U jieba_user_dict.txt \
  -D STPhrases:append:custom_st_phrases.txt \
  -i input.txt -o output.txt
```

On Windows, drive-letter paths are supported in `-D` values, for example
`STPhrases:append:R:\dicts\custom_st_phrases.txt`.

---

## CLI

You can also use the CLI interface via Python module or Python script:  
Features are:

- `convert`: Convert Chinese text using OpenCC + Jieba
- `segment`: Segment Chinese text using Jieba
- `office`: Convert Office document Chinese text using OpenCC + Jieba

#### convert

```
Module: python -m opencc_jieba_pyo3 convert --help
Script: opencc-jieba-pyo3 convert --help

usage: opencc-jieba-pyo3 convert [-h] [-i <file>] [-o <file>] [-c <conversion>] [-p] [--in-enc <encoding>] [--out-enc <encoding>] [-D <slot:mode:path>]
                                 [-U <file>]

optional arguments:
  -h, --help            show this help message and exit
  -i <file>, --input <file>
                        Read original text from <file>. (default: None)
  -o <file>, --output <file>
                        Write converted text to <file>. (default: None)
  -c <conversion>, --config <conversion>
                        Configuration: s2t|s2tw|s2twp|s2hk|s2hkp|t2s|t2tw|t2twp|t2hk|t2hkp|tw2s|tw2sp|tw2t|tw2tp|hk2s|hk2sp|hk2t|hk2tp|jp2t|t2jp (default: None)
  -p, --punct           Enable punctuation conversion. (default: False)
  --in-enc <encoding>   Encoding for input. (default: UTF-8)
  --out-enc <encoding>  Encoding for output. (default: UTF-8)
  -D <slot:mode:path>, --custom-dict <slot:mode:path>
                        Load custom OpenCC dictionary file. Format: slot:mode:path, e.g. STPhrases:append:custom.txt. Can be used multiple times. Available
                        slots: STCharacters|STPhrases|TSCharacters|TSPhrases|TWPhrases|TWPhrasesRev|HKPhrases|HKPhrasesRev|TWVariants|TWVariantsPhrases|TWVariant
                        sRev|TWVariantsRevPhrases|HKVariants|HKVariantsPhrases|HKVariantsRev|HKVariantsRevPhrases|JPSCharacters|JPSCharactersRev|JPSPhrases
                        (default: None)
  -U <file>, --user-dict-file <file>
                        Load Jieba user dictionary file using 'word freq [tag]' format. Can be used multiple times. (default: None)
```

#### segment

```
python -m opencc_jieba_pyo3 segment --help
opencc-jieba-pyo3 segment --help

usage: opencc-jieba-pyo3 segment [-h] [-i <file>] [-o <file>] [-d <char>] [-s <char>] [--no-hmm] [-m {cut,search,full,tag}] [--in-enc <encoding>]
                                 [--out-enc <encoding>] [-D <slot:mode:path>] [-U <file>]

optional arguments:
  -h, --help            show this help message and exit
  -i <file>, --input <file>
                        Read input text from <file>. (default: None)
  -o <file>, --output <file>
                        Write segmented text to <file>. (default: None)
  -d <char>, --delim <char>
                        Delimiter to join segments. (default: )
  -s <char>, --separator <char>
                        Separator for segment mode: tag. (default: /)
  --no-hmm              Disable HMM. (default: False)
  -m {cut,search,full,tag}, --mode {cut,search,full,tag}
                        Segmentation mode. (default: cut)
  --in-enc <encoding>   Encoding for input. (default: UTF-8)
  --out-enc <encoding>  Encoding for output. (default: UTF-8)
  -D <slot:mode:path>, --custom-dict <slot:mode:path>
                        Load custom OpenCC dictionary file. Format: slot:mode:path, e.g. STPhrases:append:custom.txt. Can be used multiple times. Available
                        slots: STCharacters|STPhrases|TSCharacters|TSPhrases|TWPhrases|TWPhrasesRev|HKPhrases|HKPhrasesRev|TWVariants|TWVariantsPhrases|TWVariant
                        sRev|TWVariantsRevPhrases|HKVariants|HKVariantsPhrases|HKVariantsRev|HKVariantsRevPhrases|JPSCharacters|JPSCharactersRev|JPSPhrases
                        (default: None)
  -U <file>, --user-dict-file <file>
                        Load Jieba user dictionary file using 'word freq [tag]' format. Can be used multiple times. (default: None)
```

#### office

```
python -m opencc_jieba_pyo3 office --help                                                     
usage: opencc-jieba-pyo3 office [-h] [-i <file>] [-o <file>] [-c <conversion>] [-p] [-f <format>] [--auto-ext] [--keep-font] [-D <slot:mode:path>] [-U <file>]

optional arguments:
  -h, --help            show this help message and exit
  -i <file>, --input <file>
                        Input Office document from <file>. (default: None)
  -o <file>, --output <file>
                        Output Office document to <file>. (default: None)
  -c <conversion>, --config <conversion>
                        Configuration: s2t|s2tw|s2twp|s2hk|s2hkp|t2s|t2tw|t2twp|t2hk|t2hkp|tw2s|tw2sp|tw2t|tw2tp|hk2s|hk2sp|hk2t|hk2tp|jp2t|t2jp (default: None)
  -p, --punct           Enable punctuation conversion. (default: False)
  -f <format>, --format <format>
                        Target Office format (e.g. docx, xlsx, pptx, odt, ods, odp, epub). (default: None)
  --auto-ext            Auto-append extension to output file. (default: False)
  --keep-font           Preserve font-family information in Office content. (default: False)
  -D <slot:mode:path>, --custom-dict <slot:mode:path>
                        Load custom OpenCC dictionary file. Format: slot:mode:path, e.g. STPhrases:append:custom.txt. Can be used multiple times. Available
                        slots: STCharacters|STPhrases|TSCharacters|TSPhrases|TWPhrases|TWPhrasesRev|HKPhrases|HKPhrasesRev|TWVariants|TWVariantsPhrases|TWVariant
                        sRev|TWVariantsRevPhrases|HKVariants|HKVariantsPhrases|HKVariantsRev|HKVariantsRevPhrases|JPSCharacters|JPSCharactersRev|JPSPhrases
                        (default: None)
  -U <file>, --user-dict-file <file>
                        Load Jieba user dictionary file using 'word freq [tag]' format. Can be used multiple times. (default: None)
```

```sh
python -m opencc_jieba_pyo3 convert -i input.txt -o output.txt -c s2t --punct
opencc-jieba-pyo3 convert -i input.txt -o output.txt -c s2t --punct

python -m opencc_jieba_pyo3 segment -i input.txt -o output.txt --delim "/"
opencc-jieba-pyo3 segment -i input.txt -o output.txt --delim "/" --mode search

python -m opencc_jieba_pyo3 office -i input.docx -o output.docx -c s2t --punct --keep-font
opencc-jieba-pyo3 office -i input.epub -o output.epub -c s2tw --punct
```

---

## API

### Class: `OpenCC`

Unified Python interface for OpenCC and Jieba functionalities.

#### Constructor

- `OpenCC(config: str = "s2t")`
    - `config`: Conversion configuration (see above). Defaults to `"s2t"`.

#### Attributes

- `config: str`
    - Current OpenCC conversion configuration.

#### Methods

- `is_valid_config(config: str) -> bool`
    - Check whether `config` is a supported OpenCC conversion name.

- `supported_configs() -> list[str]`
    - Return all supported OpenCC conversion names in canonical lowercase form.

- `canonicalise_config(config: str) -> str`
    - Normalize a valid config name to its canonical lowercase form.

- `set_config(config: str) -> None`
    - Update the active OpenCC conversion configuration.

- `get_config() -> str`
    - Return the current OpenCC conversion configuration.

- `convert(input: str, punctuation: bool = False) -> str`
    - Convert Chinese text using the current OpenCC config.
    - `input`: Input text.
    - `punctuation`: Whether to convert Chinese/Japanese punctuation to the target variant.
    - Returns: Converted text as a string.

- `zho_check(input: str) -> int`
    - Detect the type of Chinese in the input text.
    - Returns: Integer code (1: Traditional, 2: Simplified, 0: Others).

- `jieba_cut(input: str, hmm: bool = True) -> list[str]`
    - Segment Chinese text using Jieba accurate mode.
    - `input`: Input text.
    - `hmm`: Whether to use HMM for new words.
    - Returns: List of segmented words.

- `jieba_cut_for_search(input: str, hmm: bool = True) -> list[str]`
    - Segment Chinese text in Jieba search mode.
    - Produces finer-grained tokens suitable for search indexing.

- `jieba_cut_all(input: str) -> list[str]`
    - Segment Chinese text in Jieba full mode.
    - Returns all possible token matches without disambiguation.

- `jieba_tag(input: str, hmm: bool = True) -> list[tuple[str, str]]`
    - Perform Jieba part-of-speech tagging.
    - Returns `(word, tag)` tuples.

- `jieba_segment_join(input: str, mode: str = "cut", delim: str = " ", hmm: bool = True, separator: str = "/") -> str`
    - Segment text and join the result into a single string.
    - `mode`: One of `"cut"`, `"search"`, `"full"`, or `"tag"`.
    - `delim`: Delimiter used to join segments or tagged tokens.
    - `hmm`: Used by `"cut"`, `"search"`, and `"tag"` modes.
    - `separator`: Separator between word and POS tag in `"tag"` mode.

- `jieba_cut_and_join(input: str, delimiter: str = "/") -> str`
    - Deprecated compatibility wrapper for `jieba_segment_join(input, mode="cut", delim=delimiter)`.
    - `input`: Input text.
    - `delimiter`: Delimiter for joining words.
    - Returns: Joined segmented string.

- `jieba_keyword_extract_textrank(input: str, top_k: int = 10, allowed_pos: list[str] | None = None) -> list[str]`
    - Extract keywords using the TextRank algorithm.
    - `input`: Input text.
    - `top_k`: Number of keywords to extract.
    - `allowed_pos`: Optional POS filter list. Each item may contain one or more POS tags separated by whitespace.
    - Returns: List of keywords.

- `jieba_keyword_extract_tfidf(input: str, top_k: int = 10, allowed_pos: list[str] | None = None) -> list[str]`
    - Extract keywords using the TF-IDF algorithm.
    - `input`: Input text.
    - `top_k`: Number of keywords to extract.
    - `allowed_pos`: Optional POS filter list. Each item may contain one or more POS tags separated by whitespace.
    - Returns: List of keywords.

-

`jieba_keyword_weight_textrank(input: str, top_k: int = 10, allowed_pos: list[str] | None = None) -> list[tuple[str, float]]`

- Extract keywords and their weights using TextRank.
- `input`: Input text.
- `top_k`: Number of keywords to extract.
- `allowed_pos`: Optional POS filter list. Each item may contain one or more POS tags separated by whitespace.
- Returns: List of (keyword, weight) tuples.

-

`jieba_keyword_weight_tfidf(input: str, top_k: int = 10, allowed_pos: list[str] | None = None) -> list[tuple[str, float]]`

- Extract keywords and their weights using TF-IDF.
- `input`: Input text.
- `top_k`: Number of keywords to extract.
- `allowed_pos`: Optional POS filter list. Each item may contain one or more POS tags separated by whitespace.
- Returns: List of (keyword, weight) tuples.

---

## Development

- Rust source: [src/lib.rs](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/src/lib.rs)
- Python bindings: [/opencc_jieba_pyo3/__init
  __.py](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/__init__.py), [opencc_jieba_pyo3/opencc_jieba_pyo3.pyi](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/opencc_jieba_pyo3.pyi)
- CLI: [opencc_jieba_pyo3/__main
  __.py](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/__main__.py)

## Rust Module Required

[opencc-jieba-rs](https://github.com/laisuk/opencc-jieba-rs) : A Rust implementation of Jieba + OpenCC

---

## Benchmarks

```
Package: opencc_jieba_pyo3
Python 3.13.4 (tags/v3.13.4:8a526ec, Jun  3 2025, 17:46:04) [MSC v.1943 64 bit (AMD64)]
Platform: Windows-11-10.0.26100-SP0
Processor: Intel64 Family 6 Model 191 Stepping 2, GenuineIntel
```

### BENCHMARK RESULTS

| Method         | Config | TextSize |      Mean |   StdDev |       Min |       Max | Ops/sec |  Chars/sec |
|:---------------|--------|---------:|----------:|---------:|----------:|----------:|--------:|-----------:|
| Convert_Small  | s2t    |      100 |  0.161 ms | 0.109 ms |  0.080 ms |  0.794 ms |   6,217 |    621,740 |
| Convert_Medium | s2t    |    1,000 |  0.389 ms | 0.092 ms |  0.286 ms |  0.829 ms |   2,571 |  2,571,236 |
| Convert_Large  | s2t    |   10,000 |  1.261 ms | 0.314 ms |  1.072 ms |  2.580 ms |     793 |  7,932,120 |
| Convert_XLarge | s2t    |  100,000 |  7.290 ms | 0.464 ms |  6.864 ms |  9.848 ms |     137 | 13,716,798 |
| Convert_Small  | s2tw   |      100 |  0.189 ms | 0.104 ms |  0.103 ms |  0.620 ms |   5,285 |    528,519 |
| Convert_Medium | s2tw   |    1,000 |  0.442 ms | 0.152 ms |  0.322 ms |  1.084 ms |   2,264 |  2,264,206 |
| Convert_Large  | s2tw   |   10,000 |  1.508 ms | 0.200 ms |  1.367 ms |  2.371 ms |     663 |  6,631,682 |
| Convert_XLarge | s2tw   |  100,000 |  9.403 ms | 0.585 ms |  9.009 ms | 13.320 ms |     106 | 10,635,363 |
| Convert_Small  | s2twp  |      100 |  0.235 ms | 0.113 ms |  0.129 ms |  0.648 ms |   4,256 |    425,586 |
| Convert_Medium | s2twp  |    1,000 |  0.518 ms | 0.112 ms |  0.363 ms |  0.913 ms |   1,932 |  1,932,266 |
| Convert_Large  | s2twp  |   10,000 |  1.786 ms | 0.209 ms |  1.590 ms |  2.739 ms |     560 |  5,598,571 |
| Convert_XLarge | s2twp  |  100,000 | 11.644 ms | 0.979 ms | 10.892 ms | 17.130 ms |      86 |  8,588,034 |

### Throughput VS Size

![ThroughputSizeChart](https://raw.githubusercontent.com/laisuk/opencc_jieba_pyo3/master/assets/throughput_vs_size.png)

---

## License

[MIT](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/LICENSE)

---

Powered by **Rust**, **Jieba**, **PyO3**, **OpenCC** and **opencc-jieba-rs**.
