//! # opencc_jieba_pyo3
//!
//! This module provides Python bindings for OpenCC and Jieba functionalities using PyO3.
//! It exposes Chinese text conversion (Simplified/Traditional), segmentation, keyword extraction,
//! and post-load custom OpenCC conversion dictionaries through a unified `OpenCC` class.
//!
//! ## Features
//! - Chinese conversion (OpenCC) with multiple config modes
//! - Chinese text segmentation (Jieba)
//! - Keyword extraction (TF-IDF, TextRank)
//! - Post-load custom OpenCC conversion dictionaries (pairs and files)
//! - Utility functions for punctuation handling and language detection

use opencc_jieba_rs;
use opencc_jieba_rs::{
    CustomDictFileSpec, CustomDictMode, CustomDictSpec, DictSlot, OpenCC as _OpenCC, OpenccConfig,
    UserDictEntry,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::path::PathBuf;

/// Python-exposed OpenCC class, wrapping OpenCC and Jieba functionalities.
///
/// ## Parameters
/// - `config`: Optional conversion config (default: "s2t")
#[pyclass]
#[pyo3(subclass)]
struct OpenCC {
    /// Internal OpenCC instance.
    opencc: _OpenCC,
    /// Current OpenCC config string.
    #[pyo3(get)]
    config: String,
}

/// Python mapping accepted by `OpenCC.load_custom_dicts()`.
///
/// Expected Python shape:
///
/// ```text
/// {
///     "slot": "STPhrases",
///     "pairs": [("帕兰蒂尔", "柏蘭蒂爾")],
///     "mode": "append",
/// }
/// ```
#[derive(FromPyObject)]
struct PyCustomDictSpec {
    #[pyo3(item)]
    slot: String,

    #[pyo3(item)]
    pairs: Vec<(String, String)>,

    #[pyo3(item, default)]
    mode: Option<String>,
}

/// Python mapping accepted by `OpenCC.load_custom_dict_files()`.
///
/// Expected Python shape:
///
/// ```text
/// {
///     "slot": "STPhrases",
///     "files": ["custom_st_phrases.txt"],
///     "mode": "append",
/// }
/// ```
#[derive(FromPyObject)]
struct PyCustomDictFileSpec {
    #[pyo3(item)]
    slot: String,

    #[pyo3(item)]
    files: Vec<String>,

    #[pyo3(item, default)]
    mode: Option<String>,
}

/// Python mapping accepted by `OpenCC.load_user_dict_entries()`.
///
/// Expected Python shape:
///
/// ```text
/// {
///     "word": "帕兰蒂尔",
///     "freq": 100000,
///     "tag": "nz",
/// }
/// ```
///
/// `tag` is optional. `freq` is required, matching the `opencc-jieba-rs`
/// `UserDictEntry` contract.
#[derive(FromPyObject)]
struct PyUserDictEntry {
    #[pyo3(item)]
    word: String,

    #[pyo3(item)]
    freq: usize,

    #[pyo3(item, default)]
    tag: Option<String>,
}

impl OpenCC {
    #[inline]
    fn normalize_top_k(top_k: i32) -> usize {
        if top_k <= 0 {
            0
        } else {
            top_k as usize
        }
    }

    #[inline]
    fn build_allowed_pos<'a>(allowed_pos: Option<&'a [String]>) -> Option<Vec<&'a str>> {
        let pos = allowed_pos?
            .iter()
            .flat_map(|s| s.split_whitespace())
            .filter(|s| !s.is_empty())
            .collect::<Vec<&'a str>>();

        if pos.is_empty() {
            None
        } else {
            Some(pos)
        }
    }
}

#[pymethods]
impl OpenCC {
    /// Create a new OpenCC instance.
    ///
    /// Initializes the converter with the given configuration. The input
    /// configuration string is case-insensitive and will be normalized to
    /// the canonical lowercase form.
    ///
    /// If no configuration is provided, or if the provided value is invalid,
    /// the default configuration `"s2t"` is used.
    ///
    /// # Arguments
    ///
    /// * `config` - Optional configuration string (e.g. `"s2t"`, `"t2s"`).
    ///
    /// # Behavior
    ///
    /// - Case-insensitive input is accepted (e.g. `"T2S"` → `"t2s"`).
    /// - Invalid or unknown values fall back to `"s2t"`.
    #[new]
    #[pyo3(signature = (config=None))]
    fn new(config: Option<&str>) -> Self {
        let opencc = _OpenCC::new();

        let config = config
            .and_then(|c| OpenccConfig::try_from(c).ok())
            .unwrap_or(OpenccConfig::S2t);

        OpenCC {
            opencc,
            config: config.as_str().to_string(),
        }
    }

    /// Set the OpenCC conversion configuration.
    ///
    /// This setter validates the provided configuration string and updates the
    /// internal configuration if valid. The input is case-insensitive and will
    /// be normalized to the canonical lowercase form.
    ///
    /// # Arguments
    ///
    /// * `config` - A configuration string (e.g. `"s2t"`, `"t2s"`, `"s2twp"`).
    ///
    /// # Errors
    ///
    /// Returns a `ValueError` if the provided configuration is not supported.
    #[setter]
    fn set_config(&mut self, config: &str) -> PyResult<()> {
        let cfg = OpenccConfig::try_from(config)
            .map_err(|_| PyValueError::new_err(format!("invalid OpenCC config: {config}")))?;

        self.config = cfg.as_str().to_owned();
        Ok(())
    }

    /// Get the current OpenCC configuration.
    ///
    /// Returns the canonical configuration string (always lowercase),
    /// regardless of how it was originally provided.
    fn get_config(&self) -> &str {
        &self.config
    }

    /// Apply a new OpenCC configuration.
    ///
    /// This method validates and applies the provided configuration string.
    /// The input is case-insensitive and will be normalized to the canonical
    /// lowercase form.
    ///
    /// # Errors
    ///
    /// Returns a `ValueError` if the provided configuration is not supported.
    fn apply_config(&mut self, config: &str) -> PyResult<()> {
        let cfg = OpenccConfig::try_from(config)
            .map_err(|_| PyValueError::new_err(format!("invalid OpenCC config: {config}")))?;

        self.config = cfg.as_str().to_owned();
        Ok(())
    }

    /// Check whether a string is a valid OpenCC configuration.
    #[staticmethod]
    fn is_valid_config(config: &str) -> bool {
        OpenccConfig::is_valid_config(config)
    }

    /// Return all supported OpenCC configuration names.
    #[staticmethod]
    fn supported_configs() -> Vec<&'static str> {
        OpenccConfig::ALL.iter().map(|c| c.as_str()).collect()
    }

    /// Return canonical custom conversion-dictionary slot names.
    ///
    /// The list comes directly from `opencc-jieba-rs::DictSlot::ALL`, so the
    /// Python binding does not maintain a second slot-name list.
    #[staticmethod]
    fn available_slots() -> Vec<&'static str> {
        DictSlot::ALL
            .iter()
            .map(|slot| slot.canonical_name())
            .collect()
    }

    /// Return the canonical OpenCC configuration name.
    ///
    /// Matching is case-insensitive.
    ///
    /// # Errors
    ///
    /// Returns a `ValueError` if the provided configuration is not supported.
    #[staticmethod]
    fn canonicalise_config(config: &str) -> PyResult<&'static str> {
        let cfg = OpenccConfig::try_from(config)
            .map_err(|_| PyValueError::new_err(format!("invalid OpenCC config: {config}")))?;
        Ok(cfg.as_str())
    }

    /// Convert Chinese text using the current OpenCC config.
    fn convert(&self, input_text: &str, punctuation: bool) -> String {
        self.opencc.convert(input_text, &self.config, punctuation)
    }

    /// Detect the type of Chinese in the input text.
    fn zho_check(&self, input_text: &str) -> i32 {
        self.opencc.zho_check(input_text)
    }

    // CJK Compatibility Ideograph Normalization and Unicode Compat Normalization

    /// Normalizes CJK Compatibility Ideographs with the built-in Unicode table.
    ///
    /// This is a convenience wrapper around the underlying `opencc-jieba-rs`
    /// compatibility ideograph normalizer. It performs an optional Unicode
    /// compatibility normalization pre-pass and does not modify this
    /// [`OpenCC`] instance, its selected config, conversion dictionaries,
    /// segmentation behavior, script detection, or punctuation conversion.
    ///
    /// Use this before [`OpenCC::convert`] when input may contain CJK
    /// Compatibility Ideographs such as `金` and you want OpenCC-compatible
    /// behavior. Unmapped compatibility ideographs remain unchanged.
    fn normalize_compat(&self, text: &str) -> String {
        self.opencc.normalize_compat(text)
    }

    /// Normalizes extended Unicode compatibility forms with the built-in tables.
    ///
    /// This is a convenience wrapper around the underlying `opencc-jieba-rs`
    /// extended compatibility normalizer. It applies the extended Unicode
    /// compatibility mappings together with CJK Compatibility Ideograph
    /// normalization.
    ///
    /// This is an optional pre-processing step and does not modify this
    /// [`OpenCC`] instance, its selected config, conversion dictionaries,
    /// segmentation behavior, script detection, or punctuation conversion.
    ///
    /// Use this before [`OpenCC::convert`] when input may contain extended
    /// Unicode compatibility forms. This is a superset of
    /// [`OpenCC::normalize_compat`].
    fn normalize_compat_extended(&self, text: &str) -> String {
        self.opencc.normalize_compat_extended(text)
    }

    /// Normalize extended Unicode compatibility/variant forms only.
    ///
    /// Unlike `normalize_compat_extended()`, this does not apply the
    /// CJK Compatibility Ideograph table.
    fn normalize_unicode_compat(&self, text: &str) -> String {
        self.opencc.normalize_unicode_compat(text)
    }

    /// Apply in-memory custom OpenCC conversion dictionaries to this existing
    /// converter instance.
    ///
    /// This is a post-load API. It modifies the conversion dictionary already
    /// owned by this `OpenCC` instance and therefore composes with the current
    /// backend dictionary state. It does not replace or rebuild the Jieba
    /// tokenizer.
    ///
    /// Each Python specification is a mapping containing:
    ///
    /// - `slot`: canonical dictionary slot name, e.g. `"STPhrases"`
    /// - `pairs`: list of `(source, target)` string pairs
    /// - `mode`: `"append"` or `"override"`
    ///
    /// `append` merges mappings into the selected slot. Duplicate source keys
    /// use last-wins semantics. `override` clears that slot before inserting
    /// the supplied mappings.
    ///
    /// # Python example
    ///
    /// ```python
    /// cc = OpenCC("s2t")
    /// cc.load_custom_dicts([
    ///     {
    ///         "slot": "STPhrases",
    ///         "pairs": [("帕兰蒂尔", "柏蘭蒂爾")],
    ///         "mode": "append",
    ///     }
    /// ])
    /// ```
    fn load_custom_dicts(&mut self, specs: Vec<PyCustomDictSpec>) -> PyResult<()> {
        let rust_specs = specs
            .into_iter()
            .map(|spec| {
                Ok(CustomDictSpec {
                    slot: parse_slot(&spec.slot)?,
                    pairs: spec.pairs,
                    mode: parse_mode(spec.mode.as_deref())?,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;

        self.opencc
            .load_custom_dicts(&rust_specs)
            .map_err(to_py_value_error)
    }

    /// Apply custom OpenCC conversion dictionary files to this existing
    /// converter instance.
    ///
    /// This is the file-backed counterpart of `load_custom_dicts()` and uses
    /// the same post-load append/override semantics.
    ///
    /// Each Python specification is a mapping containing:
    ///
    /// - `slot`: canonical dictionary slot name
    /// - `files`: list of UTF-8 OpenCC text dictionary paths
    /// - `mode`: `"append"` or `"override"`
    ///
    /// Files use standard OpenCC text mappings:
    ///
    /// ```text
    /// source<TAB>target
    /// ```
    ///
    /// All files are parsed before changes are applied by the Rust core.
    ///
    /// # Python example
    ///
    /// ```python
    /// cc = OpenCC("s2t")
    /// cc.load_custom_dict_files([
    ///     {
    ///         "slot": "STPhrases",
    ///         "files": ["custom_st_phrases.txt"],
    ///         "mode": "append",
    ///     }
    /// ])
    /// ```
    fn load_custom_dict_files(&mut self, specs: Vec<PyCustomDictFileSpec>) -> PyResult<()> {
        let rust_specs = specs
            .into_iter()
            .map(|spec| {
                Ok(CustomDictFileSpec {
                    slot: parse_slot(&spec.slot)?,
                    files: spec.files.into_iter().map(PathBuf::from).collect(),
                    mode: parse_mode(spec.mode.as_deref())?,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;

        self.opencc
            .load_custom_dict_files(&rust_specs)
            .map_err(to_py_value_error)
    }

    /// Load structured in-memory Jieba user-dictionary entries into this
    /// existing converter instance.
    ///
    /// Each entry is a Python mapping with:
    ///
    /// - `word`: required word or phrase
    /// - `freq`: required Jieba frequency
    /// - `tag`: optional POS tag
    ///
    /// This modifies Jieba segmentation only. It does not modify OpenCC
    /// conversion dictionary slots.
    ///
    /// # Python example
    ///
    /// ```python
    /// cc.load_user_dict_entries([
    ///     {
    ///         "word": "帕兰蒂尔",
    ///         "freq": 100000,
    ///         "tag": "nz",
    ///     }
    /// ])
    /// ```
    fn load_user_dict_entries(&mut self, entries: Vec<PyUserDictEntry>) -> PyResult<()> {
        let rust_entries = entries
            .into_iter()
            .map(|entry| UserDictEntry {
                word: entry.word,
                freq: entry.freq,
                tag: entry.tag,
            })
            .collect::<Vec<_>>();

        self.opencc
            .load_user_dict_entries(&rust_entries)
            .map_err(to_py_value_error)
    }

    /// Load one Jieba user-dictionary file into this existing converter.
    ///
    /// The file must follow the `jieba-rs` user-dictionary format:
    ///
    /// ```text
    /// word freq [tag]
    /// ```
    ///
    /// `freq` is required and `tag` is optional.
    fn load_user_dict(&mut self, path: &str) -> PyResult<()> {
        self.opencc.load_user_dict(path).map_err(to_py_value_error)
    }

    /// Load several Jieba user-dictionary files in the supplied order.
    ///
    /// This is a Python convenience wrapper around the Rust core's
    /// single-file `load_user_dict()` API.
    ///
    /// Each file is loaded transactionally by the Rust core. If a later file
    /// fails, earlier files that were already loaded remain applied.
    fn load_user_dict_files(&mut self, files: Vec<String>) -> PyResult<()> {
        for path in files {
            self.opencc
                .load_user_dict(&path)
                .map_err(to_py_value_error)?;
        }

        Ok(())
    }

    /// Segment Chinese text using Jieba.
    fn jieba_cut(&self, input_text: &str, hmm: bool) -> Vec<String> {
        self.opencc.jieba_cut(input_text, hmm)
    }

    /// Segment Chinese text using Jieba search mode.
    fn jieba_cut_for_search(&self, input_text: &str, hmm: bool) -> Vec<String> {
        self.opencc.jieba_cut_for_search(input_text, hmm)
    }

    /// Segment Chinese text using Jieba full mode.
    fn jieba_cut_all(&self, input_text: &str) -> Vec<String> {
        self.opencc.jieba_cut_all(input_text)
    }

    /// Perform Jieba part-of-speech tagging.
    fn jieba_tag(&self, input_text: &str, hmm: bool) -> Vec<(String, String)> {
        self.opencc.jieba_tag(input_text, hmm)
    }

    /// Segment and join Chinese text using Jieba.
    fn jieba_cut_and_join(&self, input_text: &str, delimiter: &str) -> String {
        self.opencc.jieba_cut_and_join(input_text, true, delimiter)
    }

    /// Extract keywords using TextRank algorithm.
    #[pyo3(signature = (input_text, top_k=10, allowed_pos=None))]
    fn jieba_keyword_extract_textrank(
        &self,
        input_text: &str,
        top_k: i32,
        allowed_pos: Option<Vec<String>>,
    ) -> Vec<String> {
        let allowed_pos_buf = Self::build_allowed_pos(allowed_pos.as_deref());
        self.opencc.keyword_extract_textrank_pos(
            input_text,
            Self::normalize_top_k(top_k),
            allowed_pos_buf.as_deref(),
        )
    }

    /// Extract keywords using TF-IDF algorithm.
    #[pyo3(signature = (input_text, top_k=10, allowed_pos=None))]
    fn jieba_keyword_extract_tfidf(
        &self,
        input_text: &str,
        top_k: i32,
        allowed_pos: Option<Vec<String>>,
    ) -> Vec<String> {
        let allowed_pos_buf = Self::build_allowed_pos(allowed_pos.as_deref());
        self.opencc.keyword_extract_tfidf_pos(
            input_text,
            Self::normalize_top_k(top_k),
            allowed_pos_buf.as_deref(),
        )
    }

    /// Extract keywords and their weights using TextRank.
    #[pyo3(signature = (input_text, top_k=10, allowed_pos=None))]
    fn jieba_keyword_weight_textrank(
        &self,
        input_text: &str,
        top_k: i32,
        allowed_pos: Option<Vec<String>>,
    ) -> Vec<(String, f64)> {
        let allowed_pos_buf = Self::build_allowed_pos(allowed_pos.as_deref());
        self.opencc
            .keyword_weight_textrank_pos(
                input_text,
                Self::normalize_top_k(top_k),
                allowed_pos_buf.as_deref(),
            )
            .into_iter()
            .map(|keyword| (keyword.keyword, keyword.weight))
            .collect()
    }

    /// Extract keywords and their weights using TF-IDF.
    #[pyo3(signature = (input_text, top_k=10, allowed_pos=None))]
    fn jieba_keyword_weight_tfidf(
        &self,
        input_text: &str,
        top_k: i32,
        allowed_pos: Option<Vec<String>>,
    ) -> Vec<(String, f64)> {
        let allowed_pos_buf = Self::build_allowed_pos(allowed_pos.as_deref());
        self.opencc
            .keyword_weight_tfidf_pos(
                input_text,
                Self::normalize_top_k(top_k),
                allowed_pos_buf.as_deref(),
            )
            .into_iter()
            .map(|keyword| (keyword.keyword, keyword.weight))
            .collect()
    }
}

#[inline]
fn to_py_value_error<E: std::fmt::Display>(err: E) -> PyErr {
    PyValueError::new_err(err.to_string())
}

/// Parse a Python custom-dictionary merge mode.
///
/// Missing/`None` mode defaults to `append`.
fn parse_mode(mode: Option<&str>) -> PyResult<CustomDictMode> {
    match mode
        .unwrap_or("append")
        .trim()
        .to_ascii_lowercase()
        .as_str()
    {
        "append" => Ok(CustomDictMode::Append),
        "override" => Ok(CustomDictMode::Override),
        other => Err(PyValueError::new_err(format!(
            "invalid custom dict mode: {other}. Expected: append|override"
        ))),
    }
}

/// Parse a custom conversion-dictionary slot using the Rust core SSOT.
///
/// Matching is ASCII case-insensitive. Surrounding whitespace and an optional
/// `.txt` suffix are accepted at the Python boundary.
fn parse_slot(slot: &str) -> PyResult<DictSlot> {
    let trimmed = slot.trim();

    let name = if trimmed.to_ascii_lowercase().ends_with(".txt") {
        &trimmed[..trimmed.len() - 4]
    } else {
        trimmed
    };

    DictSlot::from_name_ignore_ascii_case(name).ok_or_else(|| {
        PyValueError::new_err(format!(
            "invalid custom dictionary slot: {slot}. \
             Expected a canonical slot name such as 'STPhrases', \
             'TWPhrasesRev', or 'HKVariantsRevPhrases'."
        ))
    })
}

/// Python module definition for opencc_jieba_pyo3.
#[pymodule]
fn opencc_jieba_pyo3(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<OpenCC>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_zho_check() {
        let opencc = OpenCC::new(Option::from(""));
        let text = "春眠不觉晓，处处闻啼鸟";
        let text_code = opencc.zho_check(text);
        let expected = 2;
        assert_eq!(text_code, expected);
    }

    #[test]
    fn test_parse_slot_uses_core_ssot() {
        assert_eq!(parse_slot("STPhrases").unwrap(), DictSlot::STPhrases);
        assert_eq!(parse_slot("  stphrases  ").unwrap(), DictSlot::STPhrases);
        assert_eq!(parse_slot("STPhrases.txt").unwrap(), DictSlot::STPhrases);
        assert!(parse_slot("NotASlot").is_err());
    }

    #[test]
    fn test_available_slots_mirrors_core() {
        let expected: Vec<_> = DictSlot::ALL
            .iter()
            .map(|slot| slot.canonical_name())
            .collect();

        assert_eq!(OpenCC::available_slots(), expected);
    }

    #[test]
    fn test_post_load_custom_pairs() {
        let mut cc = OpenCC::new(Some("s2t"));

        cc.load_custom_dicts(vec![PyCustomDictSpec {
            slot: "STCharacters".to_string(),
            pairs: vec![("龙".to_string(), "龍龍".to_string())],
            mode: Some("append".to_string()),
        }])
        .expect("custom pair load should succeed");

        assert_eq!(cc.convert("龙", false), "龍龍");
    }

    #[test]
    fn test_post_load_custom_files() {
        let path = std::env::temp_dir().join("opencc_jieba_pyo3_custom_st_characters.txt");
        std::fs::write(&path, "龙\t龍龍\n")
            .expect("failed to write temporary custom dictionary file");

        let mut cc = OpenCC::new(Some("s2t"));
        cc.load_custom_dict_files(vec![PyCustomDictFileSpec {
            slot: "STCharacters".to_string(),
            files: vec![path.to_string_lossy().to_string()],
            mode: Some("append".to_string()),
        }])
        .expect("custom file load should succeed");

        assert_eq!(cc.convert("龙", false), "龍龍");

        let _ = std::fs::remove_file(path);
    }

    #[test]
    fn test_custom_pairs_survive_config_switch() {
        let mut cc = OpenCC::new(Some("s2t"));

        cc.load_custom_dicts(vec![PyCustomDictSpec {
            slot: "STCharacters".to_string(),
            pairs: vec![("龙".to_string(), "龖".to_string())],
            mode: Some("append".to_string()),
        }])
        .expect("custom pair load should succeed");

        assert_eq!(cc.convert("龙", false), "龖");

        cc.apply_config("t2s").unwrap();
        assert_eq!(cc.convert("龍", false), "龙");

        cc.apply_config("s2t").unwrap();
        assert_eq!(cc.convert("龙", false), "龖");
    }

    #[test]
    fn test_user_dict_entries_preserve_domain_term() {
        let mut cc = OpenCC::new(Some("s2t"));

        cc.load_user_dict_entries(vec![PyUserDictEntry {
            word: "帕兰蒂尔".to_string(),
            freq: 100_000,
            tag: Some("nz".to_string()),
        }])
        .expect("user dictionary entries should load");

        assert_eq!(
            cc.jieba_cut("帕兰蒂尔", false),
            vec!["帕兰蒂尔".to_string()]
        );
    }

    #[test]
    fn test_user_dict_file_preserves_domain_term() {
        let path = std::env::temp_dir().join("opencc_jieba_pyo3_user_dict.txt");
        std::fs::write(&path, "帕兰蒂尔 100000 nz\n")
            .expect("failed to write temporary Jieba user dictionary");

        let mut cc = OpenCC::new(Some("s2t"));
        cc.load_user_dict(&path.to_string_lossy())
            .expect("user dictionary file should load");

        assert_eq!(
            cc.jieba_cut("帕兰蒂尔", false),
            vec!["帕兰蒂尔".to_string()]
        );

        let _ = std::fs::remove_file(path);
    }

    #[test]
    fn test_user_dict_files_load_in_order() {
        let path1 = std::env::temp_dir().join("opencc_jieba_pyo3_user_dict_1.txt");
        let path2 = std::env::temp_dir().join("opencc_jieba_pyo3_user_dict_2.txt");

        std::fs::write(&path1, "帕兰蒂尔 100000 nz\n")
            .expect("failed to write first temporary Jieba user dictionary");
        std::fs::write(&path2, "云计算 100000 n\n")
            .expect("failed to write second temporary Jieba user dictionary");

        let mut cc = OpenCC::new(Some("s2t"));
        cc.load_user_dict_files(vec![
            path1.to_string_lossy().to_string(),
            path2.to_string_lossy().to_string(),
        ])
        .expect("user dictionary files should load");

        assert_eq!(
            cc.jieba_cut("帕兰蒂尔", false),
            vec!["帕兰蒂尔".to_string()]
        );
        assert_eq!(cc.jieba_cut("云计算", false), vec!["云计算".to_string()]);

        let _ = std::fs::remove_file(path1);
        let _ = std::fs::remove_file(path2);
    }

    #[test]
    fn test_user_dict_entries_compose_with_custom_phrase() {
        let mut cc = OpenCC::new(Some("s2t"));

        cc.load_user_dict_entries(vec![PyUserDictEntry {
            word: "帕兰蒂尔".to_string(),
            freq: 100_000,
            tag: Some("nz".to_string()),
        }])
        .expect("user dictionary entries should load");

        cc.load_custom_dicts(vec![PyCustomDictSpec {
            slot: "STPhrases".to_string(),
            pairs: vec![("帕兰蒂尔".to_string(), "柏蘭蒂爾".to_string())],
            mode: Some("append".to_string()),
        }])
        .expect("custom phrase dictionary should load");

        assert_eq!(
            cc.jieba_cut("帕兰蒂尔", false),
            vec!["帕兰蒂尔".to_string()]
        );
        assert_eq!(
            cc.convert("帕兰蒂尔是一家公司", false),
            "柏蘭蒂爾是一家公司"
        );
    }

    #[test]
    fn test_user_dict_file_composes_with_custom_phrase_file() {
        let jieba_path = std::env::temp_dir().join("opencc_jieba_pyo3_user_palantir.txt");
        let opencc_path = std::env::temp_dir().join("opencc_jieba_pyo3_custom_palantir.txt");

        std::fs::write(&jieba_path, "帕兰蒂尔 100000 nz\n")
            .expect("failed to write temporary Jieba user dictionary");
        std::fs::write(&opencc_path, "帕兰蒂尔\t柏蘭蒂爾\n")
            .expect("failed to write temporary OpenCC custom dictionary");

        let mut cc = OpenCC::new(Some("s2t"));

        cc.load_user_dict(&jieba_path.to_string_lossy())
            .expect("Jieba user dictionary should load");

        cc.load_custom_dict_files(vec![PyCustomDictFileSpec {
            slot: "STPhrases".to_string(),
            files: vec![opencc_path.to_string_lossy().to_string()],
            mode: Some("append".to_string()),
        }])
        .expect("OpenCC custom phrase file should load");

        assert_eq!(
            cc.convert("帕兰蒂尔是一家公司", false),
            "柏蘭蒂爾是一家公司"
        );

        let _ = std::fs::remove_file(jieba_path);
        let _ = std::fs::remove_file(opencc_path);
    }
}
