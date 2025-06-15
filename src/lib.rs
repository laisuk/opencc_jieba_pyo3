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
use opencc_jieba_rs::OpenCC as _OpenCC;
use pyo3::prelude::*;

/// Supported OpenCC conversion configurations.
const CONFIG_LIST: [&str; 16] = [
    "s2t", "t2s", "s2tw", "tw2s", "s2twp", "tw2sp", "s2hk", "hk2s", "t2tw", "tw2t", "t2twp",
    "tw2tp", "t2hk", "hk2t", "t2jp", "jp2t",
];

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
    #[pyo3(get, set)]
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
        let config_str = match config {
            Some(c) if CONFIG_LIST.contains(&c) => c.to_string(),
            _ => "s2t".to_string(),
        };
        OpenCC {
            opencc,
            config: config_str,
        }
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
        self.opencc.keyword_extract_textrank(input_text, top_k as usize)
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
        self.opencc.keyword_extract_tfidf(input_text, top_k as usize)
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
        let keywords = self.opencc.keyword_weight_textrank(input_text, top_k as usize);
        keywords.into_iter()
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
        keywords.into_iter()
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