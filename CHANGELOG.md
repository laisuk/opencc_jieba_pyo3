# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and uses the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

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
- Add set_config(), get_config() and supported_configs()
- Add opencc_jieba_py03 executable script

### Changed
- Code optimized

### Fixed
- Fixed type runtimes warnings in Python 3.8

---

## [0.5.1] – 2025-06-13

### Added
- **Segment command**: CLI support for Chinese word segmentation using Jieba.
- **Customizable delimiters**: `--delim` (`-d`) option added to `segment` subcommand for setting output separator (e.g., space, slash, etc.).
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
