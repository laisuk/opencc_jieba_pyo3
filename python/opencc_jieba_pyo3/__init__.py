from .opencc_jieba_pyo3 import *


class OpenCC(opencc_jieba_pyo3.OpenCC):
    _config_list = [
        "s2t", "t2s", "s2tw", "tw2s", "s2twp", "tw2sp", "s2hk", "hk2s", "t2tw", "tw2t", "t2twp", "tw2t", "tw2tp",
        "t2hk", "hk2t", "t2jp", "jp2t"
    ]
    def __init__(self, config="s2t"):
        self.config = config if config in self._config_list else "s2t"

    def zho_check(self, input_text):
        return super().zho_check(input_text)

    def convert(self, input_text, punctuation=False):
        return super().convert(input_text, punctuation)

    def jieba_cut(self, input_text: str, hmm: bool = True) -> list[str]:
        # Call the Rust function and return the result as a Python list of strings
        return super().jieba_cut(input_text, hmm)

    def jieba_cut_and_join(self, input_text: str, delimiter: str = "/") -> str:
        return super().jieba_cut_and_join(input_text, delimiter)

    def jieba_keyword_extract_textrank(self, input_text: str, top_k: int) -> list[str]:
        # Call the Rust function and return the result as a Python list of strings
        return super().jieba_keyword_extract_textrank(input_text, top_k)

    def jieba_keyword_extract_tfidf(self, input_text: str, top_k: int) -> list[str]:
        return super().jieba_keyword_extract_tfidf(input_text, top_k)

    def jieba_keyword_weight_textrank(self, input_text: str, top_k: int) -> list[tuple[str, float]]:
        # Call the Rust function and return the result as a list of tuples (String, f64)
        return super().jieba_keyword_weight_textrank(input_text, top_k)

    def jieba_keyword_weight_tfidf(self, input_text: str, top_k: int) -> list[tuple[str, float]]:
        return super().jieba_keyword_weight_tfidf(input_text, top_k)
