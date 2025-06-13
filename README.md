# opencc_jieba_pyo3

[![PyPI version](https://img.shields.io/pypi/v/opencc-jieba-pyo3.svg)](https://pypi.org/project/opencc-jieba-pyo3/)
[![Downloads](https://pepy.tech/badge/opencc-jieba-pyo3)](https://pepy.tech/project/opencc-jieba-pyo3)
[![Python Versions](https://img.shields.io/pypi/pyversions/opencc-jieba-pyo3.svg)](https://pypi.org/project/opencc-jieba-pyo3/)
[![License](https://img.shields.io/github/license/laisuk/opencc_jieba_pyo3)](https://github.com/laisuk/opencc_jieba_pyo3/blob/main/LICENSE)
[![Build Status](https://github.com/laisuk/opencc_jieba_pyo3/actions/workflows/build.yml/badge.svg)](https://github.com/laisuk/opencc_jieba_pyo3/actions/workflows/build.yml)

`opencc_jieba_pyo3` is a Python extension module powered by [Rust](https://www.rust-lang.org/) Jieba and [PyO3](https://pyo3.rs/), providing fast and accurate conversion between different Chinese text variants using [opencc-jieba-rs](https://github.com/laisuk/opencc-jieba-rs) and [OpenCC](https://github.com/BYVoid/OpenCC) algorithms.

## Features

- Convert between Simplified, Traditional, Hong Kong, Taiwan, and Japanese Kanji Chinese text.
- Fast and memory-efficient, leveraging Rust's performance.
- Easy-to-use Python API.
- Supports punctuation conversion and automatic text code detection.
- Chinese word segmentation (Jieba).
- Keyword extraction (TF-IDF, TextRank).
- Utility functions for punctuation handling and language detection.

## Supported Conversion Configurations

- `s2t`, `t2s`, `s2tw`, `tw2s`, `s2twp`, `tw2sp`, `s2hk`, `hk2s`, `t2tw`, `tw2t`, `t2twp`, `tw2tp`, `t2hk`, `hk2t`, `t2jp`, `jp2t`

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

See [BUILD.md](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/BUILD.md) for detailed build and install instructions.

## Usage

### Python

```python
from opencc_jieba_pyo3 import OpenCC

text = "“春眠不觉晓，处处闻啼鸟。”"
opencc = OpenCC("s2t")
converted = opencc.convert(text, punctuation=True)
print(converted)  # 「春眠不覺曉，處處聞啼鳥。」

# Segmentation
words = opencc.jieba_cut(text, hmm=True)
print(words)  # ['春眠', '不觉', '晓', '，', '处处', '闻', '啼鸟', '。']

# Segmentation and join
joined = opencc.jieba_cut_and_join(text, delimiter="/")
print(joined)  # 春眠/不觉/晓/，/处处/闻/啼鸟/。

# Keyword extraction (TextRank)
keywords = opencc.jieba_keyword_extract_textrank(text, top_k=3)
print(keywords)  # ['春眠', '啼鸟', '处处']

# Keyword extraction (TF-IDF)
keywords_tfidf = opencc.jieba_keyword_extract_tfidf(text, top_k=3)
print(keywords_tfidf)  # ['春眠', '啼鸟', '处处']

# Keyword weights (TextRank)
kw_weights = opencc.jieba_keyword_weight_textrank(text, top_k=3)
print(kw_weights)  # [('春眠', 1.23), ('啼鸟', 0.98), ('处处', 0.75)]

# Keyword weights (TF-IDF)
kw_weights_tfidf = opencc.jieba_keyword_weight_tfidf(text, top_k=3)
print(kw_weights_tfidf)  # [('春眠', 2.34), ('啼鸟', 1.56), ('处处', 1.12)]
```

### CLI

You can also use the CLI interface:

#### convert

```
python -m opencc_jieba_pyo3 convert --help
usage: opencc_jieba_pyo3 convert [-h] [-i <file>] [-o <file>] [-c <conversion>] [-p] [--in-enc <encoding>] [--out-enc <encoding>]

options:
  -h, --help            show this help message and exit
  -i, --input <file>    Read original text from <file>.
  -o, --output <file>   Write converted text to <file>.
  -c, --config <conversion>
                        Conversion configuration: [s2t|s2tw|s2twp|s2hk|t2s|tw2s|tw2sp|hk2s|jp2t|t2jp]
  -p, --punct           Punctuation conversion
  --in-enc <encoding>   Encoding for input
  --out-enc <encoding>  Encoding for output
```

#### segment

```
python -m opencc_jieba_pyo3 segment --help
usage: opencc_jieba_pyo3 segment [-h] [-i <file>] [-o <file>] [-d <char>] [--in-enc <encoding>] [--out-enc <encoding>]

options:
  -h, --help            show this help message and exit
  -i, --input <file>    Read input text from <file>.
  -o, --output <file>   Write segmented text to <file>.
  -d, --delim <char>    Delimiter to join segments
  --in-enc <encoding>   Encoding for input
  --out-enc <encoding>  Encoding for output
```

```sh
python -m opencc_jieba_pyo3 convert -i input.txt -o output.txt -c s2t --punct
python -m opencc_jieba_pyo3 segment -i input.txt -o output.txt --delim "/"
```

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

- `convert(input: str, punctuation: bool = False) -> str`
    - Convert Chinese text using the current OpenCC config.
    - `input`: Input text.
    - `punctuation`: Whether to convert Chinese/Japanese punctuation to the target variant.
    - Returns: Converted text as a string.

- `zho_check(input: str) -> int`
    - Detect the type of Chinese in the input text.
    - Returns: Integer code (1: Traditional, 2: Simplified, 0: Others).

- `jieba_cut(input: str, hmm: bool = True) -> list[str]`
    - Segment Chinese text using Jieba.
    - `input`: Input text.
    - `hmm`: Whether to use HMM for new words.
    - Returns: List of segmented words.

- `jieba_cut_and_join(input: str, delimiter: str = "/") -> str`
    - Segment and join Chinese text using Jieba.
    - `input`: Input text.
    - `delimiter`: Delimiter for joining words.
    - Returns: Joined segmented string.

- `jieba_keyword_extract_textrank(input: str, top_k: int) -> list[str]`
    - Extract keywords using the TextRank algorithm.
    - `input`: Input text.
    - `top_k`: Number of keywords to extract.
    - Returns: List of keywords.

- `jieba_keyword_extract_tfidf(input: str, top_k: int) -> list[str]`
    - Extract keywords using the TF-IDF algorithm.
    - `input`: Input text.
    - `top_k`: Number of keywords to extract.
    - Returns: List of keywords.

- `jieba_keyword_weight_textrank(input: str, top_k: int) -> list[tuple[str, float]]`
    - Extract keywords and their weights using TextRank.
    - `input`: Input text.
    - `top_k`: Number of keywords to extract.
    - Returns: List of (keyword, weight) tuples.

- `jieba_keyword_weight_tfidf(input: str, top_k: int) -> list[tuple[str, float]]`
    - Extract keywords and their weights using TF-IDF.
    - `input`: Input text.
    - `top_k`: Number of keywords to extract.
    - Returns: List of (keyword, weight) tuples.

## Development

- Rust source: [src/lib.rs](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/src/lib.rs)
- Python bindings: [/opencc_jieba_pyo3/__init__.py](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/__init__.py), [opencc_jieba_pyo3/opencc_jieba_pyo3.pyi](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/opencc_jieba_pyo3.pyi)
- CLI: [opencc_jieba_pyo3/__main__.py](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/__main__.py)

## Rust Module Required

[opencc-jieba-rs](https://github.com/laisuk/opencc-jieba-rs) : A Rust implementation of Jieba + OpenCC

## Benchmarks

```
=====
Package: opencc_jieba_pyo3
Python 3.13.4 (tags/v3.13.4:8a526ec, Jun  3 2025, 17:46:04) [MSC v.1943 64 bit (AMD64)]
Platform: Windows-11-10.0.26100-SP0
Processor: Intel64 Family 6 Model 191 Stepping 2, GenuineIntel
=====
```

### BENCHMARK RESULTS

| Method           | Config |  TextSize |        Mean |      StdDev |         Min |         Max |     Ops/sec |   Chars/sec |
|:-----------------|--------|----------:|------------:|------------:|------------:|------------:|------------:|------------:|
| Convert_Small    | s2t    |       100 |    0.161 ms |    0.109 ms |    0.080 ms |    0.794 ms |        6217 |      621740 |
| Convert_Medium   | s2t    |      1000 |    0.389 ms |    0.092 ms |    0.286 ms |    0.829 ms |        2571 |     2571236 |
| Convert_Large    | s2t    |     10000 |    1.261 ms |    0.314 ms |    1.072 ms |    2.580 ms |         793 |     7932120 |
| Convert_XLarge   | s2t    |    100000 |    7.290 ms |    0.464 ms |    6.864 ms |    9.848 ms |         137 |    13716798 |
| Convert_Small    | s2tw   |       100 |    0.189 ms |    0.104 ms |    0.103 ms |    0.620 ms |        5285 |      528519 |
| Convert_Medium   | s2tw   |      1000 |    0.442 ms |    0.152 ms |    0.322 ms |    1.084 ms |        2264 |     2264206 |
| Convert_Large    | s2tw   |     10000 |    1.508 ms |    0.200 ms |    1.367 ms |    2.371 ms |         663 |     6631682 |
| Convert_XLarge   | s2tw   |    100000 |    9.403 ms |    0.585 ms |    9.009 ms |   13.320 ms |         106 |    10635363 |
| Convert_Small    | s2twp  |       100 |    0.235 ms |    0.113 ms |    0.129 ms |    0.648 ms |        4256 |      425586 |
| Convert_Medium   | s2twp  |      1000 |    0.518 ms |    0.112 ms |    0.363 ms |    0.913 ms |        1932 |     1932266 |
| Convert_Large    | s2twp  |     10000 |    1.786 ms |    0.209 ms |    1.590 ms |    2.739 ms |         560 |     5598571 |
| Convert_XLarge   | s2twp  |    100000 |   11.644 ms |    0.979 ms |   10.892 ms |   17.130 ms |          86 |     8588034 |

### Throughput VS Size

![ThroughputSizeChart](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/assets/throughput_vs_size.png)

## License

[MIT](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/LICENSE)

---

Powered by Rust, Jieba, PyO3, opencc-jieba-rs and OpenCC.