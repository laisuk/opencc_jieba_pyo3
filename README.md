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

- Convert between Simplified Chinese, Traditional Chinese, Taiwan and Hong Kong variants, and Japanese
  Shinjitai/Kyujitai forms.
- Fast and memory-efficient, leveraging Rust's performance.
- Easy-to-use Python API.
- Chinese word (Both Traditional and Simplified) segmentation (Jieba).
- Keyword extraction (TF-IDF, TextRank).
- Optional punctuation conversion and Chinese script detection.
- Custom OpenCC conversion dictionaries from in-memory mappings or UTF-8 files.
- Jieba user dictionaries from structured entries or UTF-8 files.
- Add or update individual Jieba words with optional automatic frequency selection.
- Explicit Unicode compatibility normalization and DeTofu display fallback replacement.
- CLI conversion for text, Office documents, and EPUB packages.

The v0.8.1 additions described below are unreleased; see [CHANGELOG.md](CHANGELOG.md) for changes since v0.8.0.

---

## 🔁 Supported Conversion Configs

| Code    | Description                                       |
|---------|---------------------------------------------------|
| `s2t`   | Simplified → Traditional                          |
| `t2s`   | Traditional → Simplified                          |
| `s2tw`  | Simplified → Traditional (Taiwan)                 |
| `tw2s`  | Traditional (Taiwan) → Simplified                 |
| `s2twp` | Simplified → Traditional (Taiwan) with idioms     |
| `tw2sp` | Traditional (Taiwan)  → Simplified with idioms    |
| `s2hk`  | Simplified → Traditional (Hong Kong)              |
| `s2hkp` | Simplified → Traditional (Hong Kong) with idioms  |
| `hk2s`  | Traditional (Hong Kong) → Simplified              |
| `hk2sp` | Traditional (Hong Kong) → Simplified with idioms  |
| `t2tw`  | Traditional → Traditional (Taiwan)                |
| `tw2t`  | Traditional (Taiwan) → Traditional                |
| `t2twp` | Traditional → Traditional (Taiwan) with idioms    |
| `tw2tp` | Traditional (Taiwan) → Traditional with idioms    |
| `t2hk`  | Traditional → Traditional (Hong Kong)             |
| `t2hkp` | Traditional → Traditional (Hong Kong) with idioms |
| `hk2t`  | Traditional (Hong Kong) → Traditional             |
| `hk2tp` | Traditional (Hong Kong) → Traditional with idioms |
| `t2jp`  | Japanese Kyujitai → Shinjitai                     |
| `jp2t`  | Japanese Shinjitai → Kyujitai                     |

---

## Installation

Build and install the Python wheel using [maturin](https://github.com/PyO3/maturin):

```sh
# In project root
maturin build --release
pip install ./target/wheels/opencc_jieba_pyo3-<version>-cp<pyver>-abi3-<platform>.whl
```

### Install from source distribution

Source distributions (`.tar.gz`) can be installed directly with `pip`. A Rust toolchain is required because the native
extension is compiled locally.

```sh
pip install opencc_jieba_pyo3-0.8.0.tar.gz
```

To force a source build from PyPI instead of using a prebuilt wheel:

```sh
pip install --no-binary opencc-jieba-pyo3 opencc-jieba-pyo3
```

The package uses the Python Stable ABI (`abi3`) with Python 3.8 as the minimum supported version. A source build
therefore produces a platform-specific `cp38-abi3` wheel, for example:

```text
opencc_jieba_pyo3-0.8.0-cp38-abi3-win_amd64.whl
```

> **Windows:** Some RAM disks or non-standard temporary filesystems may cause `pip` to fail with `WinError 1` during a
> source build. If this occurs, set `TEMP` and `TMP` to a normal local filesystem and retry.

Or for development:

```sh
maturin develop -r
```

See [BUILD.md](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/BUILD.md) for detailed build and install
instructions.

---

## Usage

### Basic conversion

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC("s2t")

print(cc.convert("八千里路云和月"))
# 八千里路雲和月

print(cc.convert("“春眠不觉晓，处处闻啼鸟。”", punctuation=True))
# 「春眠不覺曉，處處聞啼鳥。」
```

The active configuration can be inspected or changed without creating a new instance:

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC()

print(cc.get_config())  # s2t

cc.set_config("t2s")
print(cc.convert("八千里路雲和月"))
# 八千里路云和月
```

Use `OpenCC.supported_configs()` to enumerate the canonical configuration names and
`OpenCC.is_valid_config()` to validate a name.

Configuration names are case-insensitive and stored in lowercase. `OpenCC(config)` and `set_config(config)`
fall back to `"s2t"` for unsupported names. For strict validation, use `apply_config(config)` or assign
`cc.config = config`: these raise `ValueError` for an unsupported name. `canonicalise_config(config)` validates
and returns a lowercase name without changing an instance.

`convert()` follows the selected configuration; it does not automatically detect the input script and select a
direction. `zho_check(text)` provides a separate heuristic: `1` means Traditional, `2` Simplified, and `0`
undetermined, including text without distinguishing Chinese forms.

### Unicode compatibility normalization

v0.8.0 exposes three normalization APIs. Normalization is explicit and does not run automatically during
`convert()`:

- `normalize_compat()` normalizes CJK Compatibility Ideographs.
- `normalize_unicode_compat()` normalizes the extended Unicode compatibility/variant table.
- `normalize_compat_extended()` applies the extended table and CJK Compatibility Ideograph normalization together.

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC("t2s")

text = "天龍八部書裡的喬峰是契丹人"
normalized = cc.normalize_compat(text)

print(normalized)
# 天龍八部書裡的喬峰是契丹人

print(cc.convert(normalized))
# 天龙八部书里的乔峰是契丹人
```

For broader compatibility/variant normalization:

```python
from opencc_jieba_pyo3 import OpenCC

text = "聼聼竒羙⽟䂖甁噐⾳"
cc = OpenCC("t2s")
normalized = cc.normalize_compat_extended(text)
print(normalized)
# 聽聽奇美玉石瓶器音

print(cc.convert(normalized))
# 听听奇美玉石瓶器音
```

`normalize_unicode_compat()` is also available when only the extended Unicode table is wanted.

### DeTofu fallback replacement

v0.8.1 exposes DeTofu APIs for replacing selected CJK Extension characters with display-compatible fallback
characters. DeTofu is explicit and does not run automatically during `convert()`.

* `detofu()` uses the built-in fallback table.
* `detofu_with_custom_file()` uses the built-in table together with a custom UTF-8 fallback file.
* The level controls the minimum CJK extension to replace: `ExtB`, `ExtC`, `ExtD`, `ExtE`, `ExtF`, `ExtG`, `ExtH`, or
  `ExtI`.
* `all` is accepted as an alias for `ExtB`, which applies Extension B and all supported later extension mappings.

DeTofu is normally applied **after** OpenCC conversion:

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC("t2s")

text = "儼驂𬴂於上路，訪風景於崇阿"
converted = cc.convert(text, False)
safe = cc.detofu(converted, "ExtB")

print(safe)
# 俨骖騑于上路，访风景于崇阿
```

A custom fallback file can be supplied when additional mappings are needed:

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC("t2s")

converted = cc.convert("𣭲毛", False)
safe = cc.detofu_with_custom_file(
    converted,
    "ExtB",
    "custom_tofu.txt",
)

print(safe)
```

The custom file is combined with the built-in DeTofu mappings, with custom mappings taking precedence for the
same source character.

For example, `custom_tofu.txt` can contain:

```text
# source<TAB>fallback<TAB>extension
𣭲<TAB>氂<TAB>B
𬴂<TAB>騑<TAB>ExtC
```

Replace `<TAB>` with an actual tab. Blank lines and comment lines are ignored. This format differs from both
OpenCC conversion dictionaries and Jieba user dictionaries. Unmapped characters remain unchanged, and fallback
replacement does not guarantee that every character can be displayed by a particular font.

Pass `level` explicitly to both Python DeTofu methods, for example `cc.detofu(text, "ExtB")`. Level names are
case-insensitive; `B` and `ext-b` are also accepted spellings of `ExtB`.

When compatibility normalization and DeTofu are both needed, the recommended processing order is:

```text
Normalize -> Convert -> DeTofu
```

For example:

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC("t2s")

text = "天龍八部書裡的喬峰是契丹人"
text = cc.normalize_compat_extended(text)
text = cc.convert(text, False)
text = cc.detofu(text, "ExtB")

print(text)
# 天龙八部书里的乔峰是契丹人
```

### Jieba segmentation and tagging

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC()
text = "我独自来到无人海岸线"

print(cc.jieba_cut(text, hmm=True))
# ['我', '独自', '来到', '无人', '海岸线']

print(cc.jieba_cut_for_search(text, hmm=True))
# ['我', '独自', '来到', '无人', '海岸', '岸线', '海岸线']

print(cc.jieba_segment_join(text, mode="cut", delim="/"))
# 我/独自/来到/无人/海岸线

print(cc.jieba_segment_join(text, mode="tag", delim=" ", separator=":"))
# 我:r 独自:d 来到:v 无人:n 海岸线:n
```

The `jieba_*` methods analyze the supplied text without first applying the selected OpenCC conversion.

| Mode     | Behavior                                                                                     | HMM option |
|----------|----------------------------------------------------------------------------------------------|------------|
| `cut`    | Choose an accurate-mode word segmentation.                                                   | Supported  |
| `search` | Add shorter dictionary matches within accurate-mode tokens for indexing. Tokens can overlap. | Supported  |
| `full`   | Return dictionary word candidates without disambiguation. Tokens can overlap.                | Ignored    |
| `tag`    | Segment and attach Jieba POS tags; format each token as `word/tag` by default.               | Supported  |

`hmm=True` enables Hidden Markov Model recognition of words beyond dictionary matches. In `jieba_segment_join()`,
`delim` defaults to a space in every mode, while `separator` defaults to `/` and applies only in tag mode.
Empty strings are accepted for either separator. Joining search/full tokens may repeat text because tokens overlap.

### Keyword extraction

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC()
text = "我独自来到无人海岸线"

keywords = cc.jieba_keyword_extract_textrank(text, top_k=3)
print(keywords)

keywords_tfidf = cc.jieba_keyword_extract_tfidf(text, top_k=3)
print(keywords_tfidf)

weighted = cc.jieba_keyword_weight_textrank(text, top_k=3)
print(weighted)

weighted_tfidf = cc.jieba_keyword_weight_tfidf(text, top_k=3)
print(weighted_tfidf)
```

TextRank ranks words by co-occurrence relationships. TF-IDF combines input word frequencies with Jieba's built-in
inverse document frequency data. The `extract` methods return ranked strings; the `weight` methods return
`(keyword, weight)` tuples. Weights are algorithm scores, not occurrence counts or probabilities.

`top_k` is a maximum: filtering may return fewer results, and zero or negative values return an empty list.
All four methods accept an optional `allowed_pos` list of exact Jieba POS tags:

```python
keywords = cc.jieba_keyword_extract_tfidf(
    text, top_k=5, allowed_pos=["n nr", "ns", "nt", "nz"]
)
```

Each item is split on whitespace, so `["n nr", "ns"]` equals `["n", "nr", "ns"]`. `"n"` alone does not include
all noun subtypes. `None`, an empty list, or whitespace-only items apply no explicit POS restriction; the
algorithm's other filtering still applies. Keyword analysis uses the supplied text without automatic OpenCC conversion.

---

## Custom dictionaries

v0.8.0 provides two complementary dictionary layers:

- **Jieba user dictionaries** teach the tokenizer how to keep domain-specific words together and can optionally assign
  POS tags. They affect segmentation, tagging, keyword extraction, and the token boundaries seen by conversion.
- **Custom OpenCC dictionaries** add or replace mappings in a conversion-dictionary slot. They affect conversion but do
  not modify the Jieba dictionary.

Both layers can be loaded into the same `OpenCC` instance. For a custom phrase that Jieba would otherwise split, add the
phrase to the Jieba user dictionary as well as the appropriate OpenCC conversion slot.

### Typed dictionary specifications

The package exports `UserDictEntry`, `CustomDictSpec`, and `CustomDictFileSpec` for typed Python code:

```python
from typing import List

from opencc_jieba_pyo3 import CustomDictSpec, UserDictEntry

user_dict: List[UserDictEntry] = [
    {
        "word": "細路哥",
        "freq": 3,
    }
]

custom_specs: List[CustomDictSpec] = [
    {
        "slot": "HKPhrasesRev",
        "pairs": [("細路哥", "小男孩")],
        "mode": "append",
    }
]
```

`mode` is optional and defaults to `append`. `append` merges mappings into the selected slot; `override` replaces the
contents of that slot. Use `OpenCC.available_slots()` to obtain the canonical slot names. Slot matching is
case-insensitive; surrounding whitespace and an optional `.txt` suffix are accepted.

### In-memory dictionaries

For a single word, v0.8.1 adds `add_word()`:

```python
from opencc_jieba_pyo3 import OpenCC

cc = OpenCC("s2t")
cc.add_word("帕兰蒂尔", freq=100000, tag="nz")
print(cc.jieba_cut("帕兰蒂尔", hmm=False))
# ['帕兰蒂尔']

cc.add_word("自定义词语")  # Let Jieba choose the frequency.
```

The word must be nonempty and contain no whitespace. Explicit frequencies must be non-negative integers that fit
the platform's Rust `usize`; `tag` is optional. `add_word()` updates this instance's Jieba dictionary without defining
an OpenCC replacement. Use `load_user_dict_entries()` for batches with required frequencies, and
`load_custom_dicts()` to define conversion mappings.

To combine the dictionary layers:

```python
from typing import List

from opencc_jieba_pyo3 import CustomDictSpec, OpenCC, UserDictEntry

user_dict: List[UserDictEntry] = [
    {
        "word": "細路哥",
        "freq": 3,
    }
]

custom_specs: List[CustomDictSpec] = [
    {
        "slot": "HKPhrasesRev",
        "pairs": [("細路哥", "小男孩")],
        "mode": "append",
    }
]

cc = OpenCC("hk2sp")
cc.load_user_dict_entries(user_dict)
cc.load_custom_dicts(custom_specs)

print(cc.jieba_cut("這個細路哥很靈活"))
# ['這個', '細路哥', '很', '靈活']

print(cc.convert("這個細路哥很靈活"))
# 这个小男孩很灵活
```

Convenience constructors are also available when the dictionaries are known at construction time:

```python
from typing import List

from opencc_jieba_pyo3 import CustomDictSpec, OpenCC, UserDictEntry

user_dict: List[UserDictEntry] = [
    {
        "word": "細路哥",
        "freq": 3,
    }
]

custom_specs: List[CustomDictSpec] = [
    {
        "slot": "HKPhrasesRev",
        "pairs": [("細路哥", "小男孩")],
        "mode": "append",
    }
]

cc1 = OpenCC.from_user_dict_entries("hk2sp", user_dict)
cc2 = OpenCC.from_dicts("hk2sp", custom_specs)
```

### Dictionary files

Jieba user-dictionary files are UTF-8 text with one entry per line. `freq` is required and `tag` is optional:

```text
word freq [tag]
細路哥 3
帕兰蒂尔 100000 nz
```

Custom OpenCC dictionary files are UTF-8 tab-separated source/target mappings:

```text
細路哥<TAB>小男孩
```

Use `CustomDictFileSpec` for strict typing:

```python
from typing import List

from opencc_jieba_pyo3 import CustomDictFileSpec, OpenCC

custom_files: List[CustomDictFileSpec] = [
    {
        "slot": "HKPhrasesRev",
        "mode": "append",
        "files": ["tests/data/my_hk_dict.txt"],
    }
]

cc = OpenCC("hk2sp")
cc.load_user_dict_files(["tests/data/user_dict.txt"])
cc.load_custom_dict_files(custom_files)

print(cc.convert("這個細路哥很靈活"))
# 这个小男孩很灵活
```

File-based convenience constructors are also available:

```python
from opencc_jieba_pyo3 import OpenCC

custom_specs = [
    {
        "slot": "STPhrases",
        "files": ["a.txt", "b.txt"],
        "mode": "append",
    }
]

cc1 = OpenCC.from_user_dict_files("s2t", ["jieba_user_dict.txt"])
cc2 = OpenCC.from_dict_files("s2t", custom_specs)
```

A single Jieba dictionary file can be loaded with `load_user_dict(path)`. Multiple files are applied in the supplied
order. If a later Jieba file fails, earlier successfully loaded files remain applied. For custom OpenCC dictionary
files, all files are parsed before mappings are applied. Duplicate source keys use the last supplied value.
Custom OpenCC mappings remain available when switching configurations, but affect only configurations using their slot.

### Why Jieba and OpenCC dictionaries sometimes need each other

OpenCC phrase conversion operates on Jieba-tokenized text. If Jieba splits a custom phrase, a phrase mapping cannot
match the complete source text.

For example, without a Jieba user entry:

```text
這個 細路 哥 很 靈活
```

Adding `細路哥 3` to a Jieba user dictionary keeps the phrase together:

```text
這個 細路哥 很 靈活
```

The `HKPhrasesRev` mapping `細路哥 → 小男孩` can then produce:

```text
这个小男孩很灵活
```

This is why `convert` supports both `-U` and `-D`, while `segment` only needs `-U`.

## CLI

The package can be invoked either as a module or through the installed `opencc-jieba-pyo3` script:

```sh
python -m opencc_jieba_pyo3 <command> [options]
opencc-jieba-pyo3 <command> [options]
```

Available commands:

- `convert` — convert text with OpenCC + Jieba.
- `segment` — segment/tag text with Jieba.
- `office` — convert supported Office/document formats.

Run `opencc-jieba-pyo3 <command> --help` for the complete option list.

For `convert` and `segment`, omit `-i` to read stdin and omit `-o` to write stdout. Text encodings default to UTF-8;
use `--in-enc` and `--out-enc` for files and redirected byte streams. Diagnostics go to stderr. The CLI rejects input
and output paths referring to the same file, including existing symbolic-link and hard-link aliases.

Unlike the Python constructor's fallback behavior, `convert` and `office` reject unsupported `--config` names.
Omitting the configuration uses `s2t`.

### Text conversion

```sh
opencc-jieba-pyo3 convert -i input.txt -o output.txt -c s2t --punct
```

Standard input and output are supported:

```sh
echo "這個細路哥很靈活" | opencc-jieba-pyo3 convert -c hk2sp
```

Compatibility normalization can be enabled before conversion:

```sh
opencc-jieba-pyo3 convert -c t2s -E -i input.txt -o output.txt
```

- `-n`, `--norm-compat` — normalize CJK Compatibility Ideographs.
- `-E`, `--norm-compat-extended` — apply extended compatibility normalization; takes precedence over `-n`.

DeTofu fallback replacement can be applied after conversion:

```sh
opencc-jieba-pyo3 convert -c t2s -E --detofu ExtB -i input.txt -o output.txt
```

`--detofu` accepts `all`, `ExtB`, `ExtC`, `ExtD`, `ExtE`, `ExtF`, `ExtG`, `ExtH`, or `ExtI`. When specified without
a level, it defaults to `all` (`ExtB`).

A custom DeTofu mapping file can also be supplied:

```sh
opencc-jieba-pyo3 convert -c t2s --detofu ExtB \
  --detofu-file custom_tofu.txt \
  -i input.txt -o output.txt
```

`--detofu-file` requires `--detofu`.

When normalization and DeTofu are both enabled, the processing order is:

```text
Normalize -> Convert -> DeTofu
```

Custom Jieba and OpenCC dictionaries can be composed:

```sh
opencc-jieba-pyo3 convert -c hk2sp \
  -U tests/data/user_dict.txt \
  -D HKPhrasesRev:append:tests/data/my_hk_dict.txt
```

`-U` and `-D` may each be repeated. Windows drive-letter paths are supported in `-D` specifications, for example
`STPhrases:append:R:\dicts\custom_st_phrases.txt`.

### Segmentation

```sh
opencc-jieba-pyo3 segment -i input.txt -o output.txt --delim "/" --mode search
```

The modes are `cut`, `search`, `full`, and `tag`, as described in the segmentation table above. Use `--no-hmm`
to disable HMM in cut, search, or tag mode; it is ignored in full mode.

`--delim` inserts text between tokens and defaults to a space. In tag mode, `--separator` inserts text between
each word and POS tag and defaults to `/`. Values are used as supplied, including `/`, identical separators,
and empty strings:

```sh
opencc-jieba-pyo3 segment -i input.txt --mode tag --delim " | " --separator ":"
opencc-jieba-pyo3 segment -i input.txt --mode cut --delim ""
```

Jieba user dictionaries are supported with `-U`:

```sh
echo "這個細路哥很靈活" | opencc-jieba-pyo3 segment -U tests/data/user_dict.txt
```

Compatibility normalization is available with `-n` and `-E` before segmentation. Custom OpenCC `-D` mappings,
OpenCC conversion, punctuation conversion, and DeTofu are not used by segmentation.

### Office/document conversion

```sh
opencc-jieba-pyo3 office -i input.docx -o output.docx -c s2t --punct --keep-font
opencc-jieba-pyo3 office -i input.epub -o output.epub -c s2tw --punct
```

Supported package formats are `docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp`, and `epub`. The format is inferred from
the input extension; `-f` / `--format` overrides that inference. It does not convert a document from one package
format to another, such as DOCX to EPUB.

Office/document conversion supports the same normalization and DeTofu pipeline as text conversion:

```sh
opencc-jieba-pyo3 office \
  -i input.docx -o output.docx \
  -c t2s -E --detofu ExtB
```

The processing order is:

```text
Normalize -> Convert -> DeTofu
```

The Office command supports:

- `-c`, `--config` for the conversion configuration.
- `-p`, `--punct` for punctuation conversion.
- `-n`, `--norm-compat` for CJK Compatibility Ideograph normalization.
- `-E`, `--norm-compat-extended` for extended compatibility normalization; takes precedence over `-n`.
- `--detofu [level]` for DeTofu fallback replacement after conversion.
- `--detofu-file <file>` for additional custom DeTofu mappings; requires `--detofu`.
- `-D`, `--custom-dict` for custom OpenCC dictionary files.
- `-U`, `--user-dict-file` for Jieba user dictionaries.
- `-F`, `--convert-filename` to convert the input filename stem using the same conversion pipeline when generating the
  default output filename; ignored when `-o` is specified.
- `--keep-font` to preserve font-family information.

When `-o`, `--output` is omitted, the output file is automatically named `<input_stem>_converted.<format>`. With `-F`,
the input filename stem is converted before the suffix is appended. If an explicit output filename has no extension, the
target format extension is appended automatically.

```sh
# Generate a converted filename stem and apply normalization to document contents.
opencc-jieba-pyo3 office -i "汉语.docx" -c s2t -n --convert-filename
# Output: 漢語_converted.docx
```

The former `--auto-ext` option has been removed; omit it from existing scripts. Converted filename stems must
remain a single filename component. Office/EPUB output is built in a temporary archive beside the destination,
checked for ZIP integrity, and then replaces the destination. An existing output file is preserved if conversion
or archive validation fails. PPTX conversion targets slides, notes, masters, layouts, and comment parts;
XLSX conversion targets shared strings and inline-string cell text. EPUB output keeps `mimetype` first and uncompressed.

## API

### `OpenCC`

```
OpenCC(config: str = "s2t")
```

The class combines OpenCC conversion dictionaries with a Jieba tokenizer.

### Configuration

- `OpenCC.supported_configs() -> list[str]`
- `OpenCC.is_valid_config(config: str) -> bool`
- `OpenCC.canonicalise_config(config: str) -> str`
- `get_config() -> str`
- `set_config(config: str) -> None`
- `apply_config(config: str) -> None` — strict configuration setter; raises `ValueError` on unsupported names.

### Conversion, normalization, and DeTofu

- `convert(input: str, punctuation: bool = False) -> str`
- `normalize_compat(input: str) -> str`
- `normalize_unicode_compat(input: str) -> str`
- `normalize_compat_extended(input: str) -> str`
- `detofu(text: str, level: str) -> str`
- `detofu_with_custom_file(text: str, level: str, path: str) -> str`
- `zho_check(input: str) -> int`

Normalization APIs are explicit pre-processing operations, while DeTofu is an explicit post-processing operation.
Neither runs automatically during `convert()`.

When all three stages are required, use:

```text
Normalize -> Convert -> DeTofu
```

`zho_check()` returns `1` for Traditional Chinese, `2` for Simplified Chinese, and `0` for other/undetermined text.

### Jieba segmentation and tagging

- `jieba_cut(input: str, hmm: bool = True) -> list[str]`
- `jieba_cut_for_search(input: str, hmm: bool = True) -> list[str]`
- `jieba_cut_all(input: str) -> list[str]`
- `jieba_tag(input: str, hmm: bool = True) -> list[tuple[str, str]]`
- `jieba_segment_join(input: str, mode: str = "cut", delim: str = " ", hmm: bool = True, separator: str = "/") -> str`
- `jieba_cut_and_join(input: str, delimiter: str = "/") -> str` — deprecated compatibility wrapper.

### Keyword extraction

- `jieba_keyword_extract_textrank(input: str, top_k: int = 10, allowed_pos: list[str] | None = None) -> list[str]`
- `jieba_keyword_extract_tfidf(input: str, top_k: int = 10, allowed_pos: list[str] | None = None) -> list[str]`
-
`jieba_keyword_weight_textrank(input: str, top_k: int = 10, allowed_pos: list[str] | None = None) -> list[tuple[str, float]]`
-
`jieba_keyword_weight_tfidf(input: str, top_k: int = 10, allowed_pos: list[str] | None = None) -> list[tuple[str, float]]`

### Jieba user dictionaries

- `OpenCC.from_user_dict_entries(config="s2t", entries=None) -> OpenCC`
- `OpenCC.from_user_dict_files(config="s2t", files=None) -> OpenCC`
- `load_user_dict_entries(entries) -> None`
- `load_user_dict(path) -> None`
- `load_user_dict_files(files) -> None`
- `add_word(word: str, freq: int | None = None, tag: str | None = None) -> None`

### Custom OpenCC dictionaries

- `OpenCC.from_dicts(config="s2t", specs=None) -> OpenCC`
- `OpenCC.from_dict_files(config="s2t", specs=None) -> OpenCC`
- `load_custom_dicts(specs) -> None`
- `load_custom_dict_files(specs) -> None`
- `OpenCC.available_slots() -> list[str]`

The exported typing helpers are `UserDictEntry`, `CustomDictSpec`, and `CustomDictFileSpec`.

## Development

- Rust source: [src/lib.rs](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/src/lib.rs)
- Python bindings: [opencc_jieba_pyo3/
  __init__.py](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/__init__.py), [opencc_jieba_pyo3/opencc_jieba_pyo3.pyi](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/opencc_jieba_pyo3.pyi)
- CLI: [opencc_jieba_pyo3/
  __main__.py](https://github.com/laisuk/opencc_jieba_pyo3/blob/master/opencc_jieba_pyo3/__main__.py)

Run the Python API and CLI regression tests from the project root after building/installing the native extension:

```sh
python -m unittest discover -s tests -v
```

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
