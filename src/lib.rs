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

// /// Supported OpenCC conversion configurations.
// const CONFIG_LIST: [&str; 16] = [
//     "s2t", "t2s", "s2tw", "tw2s", "s2twp", "tw2sp", "s2hk", "hk2s", "t2tw", "tw2t", "t2twp",
//     "tw2tp", "t2hk", "hk2t", "t2jp", "jp2t",
// ];

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
    /// # Arguments
    /// * `config` - Optional config string (must be in CONFIG_LIST, defaults to "s2t")
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

    #[setter]
    fn set_config(&mut self, config: &str) -> PyResult<()> {
        let cfg = OpenccConfig::try_from(config)
            .map_err(|_| PyValueError::new_err(format!(
                "invalid OpenCC config: {config}"
            )))?;

        self.config = cfg.as_str().to_owned();
        Ok(())
    }

    /// Returns the current canonical config string.
    fn get_config(&self) -> &str {
        &self.config
    }

    /// Applies a config string (case-insensitive).
    /// Raises ValueError if invalid.
    fn apply_config(&mut self, config: &str) -> PyResult<()> {
        let cfg = OpenccConfig::try_from(config)
            .map_err(|_| PyValueError::new_err(format!(
                "invalid OpenCC config: {config}"
            )))?;

        self.config = cfg.as_str().to_owned();
        Ok(())
    }

    /// Returns True if the given string is a valid OpenCC config.
    #[staticmethod]
    fn is_valid_config(config: &str) -> bool {
        OpenccConfig::is_valid_config(config)
    }

    #[staticmethod]
    fn supported_configs() -> Vec<&'static str> {
        OpenccConfig::ALL.iter().map(|c| c.as_str()).collect()
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
