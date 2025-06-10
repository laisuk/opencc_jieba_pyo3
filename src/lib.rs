use opencc_jieba_rs;
use opencc_jieba_rs::OpenCC as _OpenCC;
use pyo3::prelude::*;

const CONFIG_LIST: [&str; 16] = [
    "s2t", "t2s", "s2tw", "tw2s", "s2twp", "tw2sp", "s2hk", "hk2s", "t2tw", "tw2t", "t2twp",
    "tw2tp", "t2hk", "hk2t", "t2jp", "jp2t",
];
// Wrap the OpenCC struct in PyO3
#[pyclass]
#[pyo3(subclass)]
struct OpenCC {
    opencc: _OpenCC,
    #[pyo3(get, set)]
    config: String,
}

// Implement methods for the OpenCCWrapper struct
#[pymethods]
impl OpenCC {
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

    fn convert(&self, input: &str, punctuation: bool) -> String {
        self.opencc.convert(input, &self.config, punctuation)
    }

    fn zho_check(&self, input: &str) -> i32 {
        self.opencc.zho_check(input)
    }

    // Expose jieba_cut to Python, returning Vec<String>
    fn jieba_cut(&self, input: &str) -> Vec<String> {
        // Use jieba.cut and convert Vec<&str> to Vec<String>
        self.opencc.jieba_cut(input, true)
    }

    fn jieba_cut_and_join(&self, input: &str, delimiter: &str) -> String {
        // self.opencc.jieba_cut(input, true).join(delimiter)
        self.opencc.jieba_cut_and_join(input, true, delimiter)
    }

    fn jieba_keyword_extract_textrank(&self, input: &str, top_k: i32) -> Vec<String> {
        self.opencc.keyword_extract_textrank(input, top_k as usize)
    }

    fn jieba_keyword_extract_tfidf(&self, input: &str, top_k: i32) -> Vec<String> {
        self.opencc.keyword_extract_tfidf(input, top_k as usize)
    }

    fn jieba_keyword_weight_textrank(&self, input: &str, top_k: i32) -> Vec<(String, f64)> {
        // Assume that the return type of keyword_weight_textrank is Vec<Keyword>
        let keywords = self.opencc.keyword_weight_textrank(input, top_k as usize);
        // Manually transform the Vec<Keyword> into Vec<(String, usize)>
        keywords.into_iter()
            .map(|keyword| {
                // Assume keyword has fields `word: String` and `weight: f64`
                (keyword.keyword, keyword.weight)
            })
            .collect()
    }

    fn jieba_keyword_weight_tfidf(&self, input: &str, top_k: i32) -> Vec<(String, f64)> {
        // Assume that the return type of keyword_weight_textrank is Vec<Keyword>
        let keywords = self.opencc.keyword_weight_tfidf(input, top_k as usize);
        // Manually transform the Vec<Keyword> into Vec<(String, usize)>
        keywords.into_iter()
            .map(|keyword| {
                // Assume keyword has fields `word: String` and `weight: f64`
                (keyword.keyword, keyword.weight)
            })
            .collect()
    }
}

#[pymodule]
fn opencc_jieba_pyo3(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<OpenCC>()?;

    // Optionally add functions:
    // m.add_function(wrap_pyfunction!(some_func, m)?)?;

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
