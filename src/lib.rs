//! # opencc_jieba_pyo3
//!
//! This module provides Python bindings for OpenCC and Jieba functionalities using PyO3.
//! It exposes Chinese text conversion (Simplified/Traditional), segmentation, and keyword extraction
//! to Python via a unified `OpenCC` class.
//!
//! ## Features
//! - Chinese conversion (OpenCC) with multiple config modes
//! - Chinese text segmentation (Jieba)
//! - Keyword extraction (TF-IDF, TextRank)
//! - Utility functions for punctuation handling and language detection

use opencc_jieba_rs;
use opencc_jieba_rs::{OpenCC as _OpenCC, OpenccConfig};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

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
    ///
    /// # Returns
    ///
    /// The current configuration (e.g. `"s2t"`, `"t2s"`).
    fn get_config(&self) -> &str {
        &self.config
    }

    /// Apply a new OpenCC configuration.
    ///
    /// This method validates and applies the provided configuration string.
    /// The input is case-insensitive and will be normalized to the canonical
    /// lowercase form.
    ///
    /// # Arguments
    ///
    /// * `config` - A configuration string (e.g. `"s2t"`, `"t2s"`).
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
    ///
    /// This performs a case-insensitive validation against all supported
    /// configuration names.
    ///
    /// # Arguments
    ///
    /// * `config` - The configuration string to validate.
    ///
    /// # Returns
    ///
    /// `true` if the configuration is valid, otherwise `false`.
    #[staticmethod]
    fn is_valid_config(config: &str) -> bool {
        OpenccConfig::is_valid_config(config)
    }

    /// Return all supported OpenCC configuration names.
    ///
    /// The returned list contains canonical configuration identifiers
    /// (all lowercase), such as `"s2t"`, `"t2s"`, `"s2tw"`, etc.
    ///
    /// # Returns
    ///
    /// A vector of all supported configuration names.
    #[staticmethod]
    fn supported_configs() -> Vec<&'static str> {
        OpenccConfig::ALL.iter().map(|c| c.as_str()).collect()
    }

    /// Return the canonical OpenCC configuration name.
    ///
    /// This method validates the provided configuration string and returns its
    /// canonical lowercase form if valid. Matching is case-insensitive.
    ///
    /// # Arguments
    ///
    /// * `config` - A configuration string (e.g. `"s2t"`, `"T2S"`, `"S2TWP"`).
    ///
    /// # Returns
    ///
    /// The canonical configuration name (e.g. `"s2t"`, `"t2s"`, `"s2twp"`).
    ///
    /// # Errors
    ///
    /// Returns a `ValueError` if the provided configuration is not supported.
    #[staticmethod]
    fn canonicalise_config(config: &str) -> PyResult<&'static str> {
        let cfg = OpenccConfig::try_from(config)
            .map_err(|_| PyValueError::new_err(format!(
                "invalid OpenCC config: {config}"
            )))?;
        Ok(cfg.as_str())
    }

    /// Convert Chinese text using the current OpenCC config.
    ///
    /// # Arguments
    /// * `input` - Input text
    /// * `punctuation` - Whether to convert punctuation
    ///
    /// # Returns
    /// Converted text as String.
    fn convert(&self, input_text: &str, punctuation: bool) -> String {
        self.opencc.convert(input_text, &self.config, punctuation)
    }

    /// Detect the type of Chinese in the input text.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    ///
    /// # Returns
    /// Integer code representing detected Chinese type.
    fn zho_check(&self, input_text: &str) -> i32 {
        self.opencc.zho_check(input_text)
    }

    /// Segment Chinese text using Jieba.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    /// * `hmm` - Whether to use HMM for new words
    ///
    /// # Returns
    /// List of segmented words.
    fn jieba_cut(&self, input_text: &str, hmm: bool) -> Vec<String> {
        self.opencc.jieba_cut(input_text, hmm)
    }

    /// Segment Chinese text using Jieba search mode.
    ///
    /// This mode is suitable for search engine indexing and may return
    /// finer-grained tokens than normal cut mode.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    /// * `hmm` - Whether to use HMM for new words
    ///
    /// # Returns
    /// List of segmented words.
    fn jieba_cut_for_search(&self, input_text: &str, hmm: bool) -> Vec<String> {
        self.opencc.jieba_cut_for_search(input_text, hmm)
    }

    /// Segment Chinese text using Jieba full mode.
    ///
    /// This mode attempts to cut out all possible words in the sentence.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    ///
    /// # Returns
    /// List of segmented words.
    fn jieba_cut_all(&self, input_text: &str) -> Vec<String> {
        self.opencc.jieba_cut_all(input_text)
    }

    /// Perform Jieba part-of-speech tagging.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    /// * `hmm` - Whether to use HMM for new words
    ///
    /// # Returns
    /// A list of `(word, tag)` tuples.
    fn jieba_tag(&self, input_text: &str, hmm: bool) -> Vec<(String, String)> {
        self.opencc.jieba_tag(input_text, hmm)
    }

    /// Segment and join Chinese text using Jieba.
    ///
    /// # Arguments
    /// * `input_text` - input text
    /// * `delimiter` - Delimiter for joining words
    ///
    /// # Returns
    /// Joined segmented string.
    fn jieba_cut_and_join(&self, input_text: &str, delimiter: &str) -> String {
        self.opencc.jieba_cut_and_join(input_text, true, delimiter)
    }

    /// Extract keywords using TextRank algorithm.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    /// * `top_k` - Number of keywords to extract
    ///
    /// # Returns
    /// List of keywords.
    fn jieba_keyword_extract_textrank(&self, input_text: &str, top_k: i32) -> Vec<String> {
        self.opencc
            .keyword_extract_textrank(input_text, top_k as usize)
    }

    /// Extract keywords using TF-IDF algorithm.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    /// * `top_k` - Number of keywords to extract
    ///
    /// # Returns
    /// List of keywords.
    fn jieba_keyword_extract_tfidf(&self, input_text: &str, top_k: i32) -> Vec<String> {
        self.opencc
            .keyword_extract_tfidf(input_text, top_k as usize)
    }

    /// Extract keywords and their weights using TextRank.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    /// * `top_k` - Number of keywords to extract
    ///
    /// # Returns
    /// List of (keyword, weight) tuples.
    fn jieba_keyword_weight_textrank(&self, input_text: &str, top_k: i32) -> Vec<(String, f64)> {
        let keywords = self
            .opencc
            .keyword_weight_textrank(input_text, top_k as usize);
        keywords
            .into_iter()
            .map(|keyword| (keyword.keyword, keyword.weight))
            .collect()
    }

    /// Extract keywords and their weights using TF-IDF.
    ///
    /// # Arguments
    /// * `input_text` - Input text
    /// * `top_k` - Number of keywords to extract
    ///
    /// # Returns
    /// List of (keyword, weight) tuples.
    fn jieba_keyword_weight_tfidf(&self, input_text: &str, top_k: i32) -> Vec<(String, f64)> {
        let keywords = self.opencc.keyword_weight_tfidf(input_text, top_k as usize);
        keywords
            .into_iter()
            .map(|keyword| (keyword.keyword, keyword.weight))
            .collect()
    }
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
}
