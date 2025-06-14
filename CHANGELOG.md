# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and uses the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

---

## [0.5.1] – 2025-06-13

### Added
- **Segment command**: CLI support for Chinese word segmentation using Jieba.
- **Customizable delimiters**: `--delim` (`-d`) option added to `segment` subcommand for setting output separator (e.g., space, slash, etc.).
- Python API: `.segment(text: str, delim: str = " ")` method added to `OpenCC` class.
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
