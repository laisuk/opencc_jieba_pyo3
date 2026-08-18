# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and uses
the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

---

## [0.8.0] - Unreleased

### Added

- Added post-load custom OpenCC conversion dictionaries with `CustomDictSpec` and `CustomDictFileSpec`, supporting
  per-slot `append` and `override` modes.
- Added `OpenCC.load_custom_dicts()` and `OpenCC.load_custom_dict_files()` for applying in-memory mappings and plaintext
  dictionary files to the current converter instance.
- Added `OpenCC.available_slots()` to expose canonical custom-dictionary slot names from the Rust core.
- Added `OpenCC.from_dicts()` and `OpenCC.from_dict_files()` convenience constructors for instances initialized with
  custom OpenCC conversion dictionaries.
- Added structured Jieba user-dictionary entries with `UserDictEntry`, requiring `word` and `freq` with an optional POS
  `tag`.
- Added `OpenCC.load_user_dict_entries()` and `OpenCC.load_user_dict_files()` for post-loading Jieba user dictionaries
  onto the current converter instance.
- Added `OpenCC.from_user_dict_entries()` and `OpenCC.from_user_dict_files()` convenience constructors for instances
  initialized with Jieba user dictionaries.
- Added Python type definitions for custom OpenCC dictionaries and Jieba user-dictionary entries.
- Added CLI `-D` / `--custom-dict <slot:mode:path>` for loading custom OpenCC dictionary files. The option may be
  repeated and supports Windows drive-letter paths.
- Added CLI `-U` / `--user-dict-file <file>` for loading Jieba user-dictionary files. The option may be repeated.
- Added custom OpenCC and Jieba user-dictionary support to the `convert`, `segment`, and `office` CLI subcommands.
- Added Python integration tests covering conversion, Jieba segmentation and tagging, keyword extraction, custom
  dictionaries, user dictionaries, config switching, and combined Jieba + OpenCC custom phrase conversion.

### Changed

- Updated `opencc-jieba-rs` from v0.7.6 to the v0.8.0 core API.
- Custom OpenCC dictionaries and Jieba user dictionaries now use the Rust core's post-load model, allowing both
  dictionary layers to compose on the same `OpenCC` instance.
- CLI converter initialization now loads Jieba user dictionaries before custom OpenCC dictionaries so phrase mappings
  can use the customized Jieba segmentation.
- Refactored shared CLI dictionary option parsing and converter construction across `convert`, `segment`, and `office`.
- Updated Python type stubs to expose custom dictionary, user dictionary, and available-slot APIs.

---

## [0.7.5] - 2026-05-08

### Changed

- Added `separator` argument in `jieba_segment_join()` for segment method `"tag"`.
- Changed `jieba_segment_join()` default `delim` from `"/"` to `" "` to avoid readability conflicts with the default POS
  `separator="/"`.
- Updated Python type stubs to match runtime defaults and expose `config`, `set_config()`, and `jieba_segment_join()`.
- Updated `requires-python` metadata to `>=3.8` to match the `abi3-py38` build target.
- Included `py.typed` in release packaging.
- Updated `opencc-jieba-rs` to v0.7.6.
- CLI: optimized subcommand `segment`.

### Fixed

- Fixed `segment --mode tag --no-hmm` so the CLI passes the HMM flag to `jieba_tag()`.
- Updated sample scripts to use the public `opencc_jieba_pyo3` import path and current `jieba_segment_join()` API.
- Removed tracked platform-specific native extension artifacts from the duplicate `python/` package tree.

---

## [0.7.4] - 2026-04-10

### Added

- Added `tag` mode in CLI subcommand `segment`.
- Added `jieba_segment_join()`

### Changed

- Update opencc-jieba-rs to v0.7.4
- Optimized office_helper for handling `XLSX`

### Fixed

- Fix CLI config handling to support case-insensitive OpenCC configs

---

## [0.7.3] - 2026-03-17

### Changed

- Update opencc-jieba-rs to v0.7.3

---

## [0.7.2] - 2025-11.07

### Changed

- Update opencc-jieba-rs to v0.7.2

---

## [0.7.1] - 2025-10-08

### Changed

- Update opencc-jieba-rs to v0.7.1

---

## [0.7.0] - 2025-08-22

### Changed

- Update opencc-jieba-rs to v0.7.0

---

## [0.6.0] 2025-07-12

### Added

- Add Office and Epub documents support in Chinese text conversion.

### Changed

- Update opencc-jieba-rs to v0.6.0

---

## [0.5.3] - 2025-06-27

### Changed

- Update opencc-jieba-rs to v0.5.3

---

## [0.5.2] – 2025-06-19

### Added

- Add set_config (), get_config () and supported_configs ()
- Add opencc_jieba_py03 executable script

### Changed

- Code optimized

### Fixed

- Fixed type runtimes warnings in Python 3.8

---

## [0.5.1] – 2025-06-13

### Added

- **Segment command**: CLI support for Chinese word segmentation using Jieba.
- **Customizable delimiters**: `--delim` (`-d`) option added to `segment` subcommand for setting output separator (e.g.,
  space, slash, etc.).
- Python API: `.segment(text: str, delim: str = " ")` method added to `OpenCC` class.

### Changed

- Improved CLI argument parsing, help message formatting, and file encoding handling.

---

## [0.5.0] – 2025-06-12

### Added

- Initial release of `opencc-jieba-pyo3` on PyPI.
- Python bindings for Rust-powered OpenCC conversion and Jieba segmentation using PyO3.
- Support for standard OpenCC conversion configs:
    - `s2t`, `s2tw`, `s2twp`, `s2hk`, `t2s`, `tw2s`, `tw2sp`, `hk2s`, `jp2t`, `t2jp`
- CLI tool: `python -m opencc_jieba_rs` with options for text conversion.
- Binary wheels for Linux, macOS, and Windows via `maturin`.
- UTF-8 encoding handling with fallback for BOM detection.

---
