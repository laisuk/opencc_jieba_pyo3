from .opencc_jieba_pyo3 import OpenCC as _OpenCC
from typing import List, Tuple


class OpenCC(_OpenCC):
    def __init__(self, config="s2t"):
        self.config = super().config if super().is_valid_config(config) else "s2t"

    def set_config(self, config):
        """
        Set the OpenCC conversion configuration.

        The input is case-insensitive. If the configuration is valid,
        it will be normalized to the canonical lowercase form.
        If invalid, the configuration falls back to "s2t".

        Parameters
        ----------
        config : str
            The configuration string (e.g. "s2t", "t2s").

        See Also
        --------
        is_valid_config : Validate a configuration string
        supported_configs : List all supported configurations
        """
        if super().is_valid_config(config):
            super().apply_config(config)
        else:
            self.config = "s2t"

    def get_config(self):
        """
        Get the current conversion config.

        :return: Current config string
        """
        return self.config

    @classmethod
    def supported_configs(cls):
        """
        Return a list of supported conversion config strings.

        :return: List of config names
        """
        return super().supported_configs()

    def zho_check(self, input_text):
        """
        Heuristically determine whether input text is Simplified or Traditional Chinese.

        :param input_text: Input string
        :return: 0 = unknown, 2 = simplified, 1 = traditional
        """
        return super().zho_check(input_text)

    def convert(self, input_text, punctuation=False):
        """
        Automatically dispatch to the appropriate conversion method based on `self.config`.

        :param input_text: The string to convert
        :param punctuation: Whether to apply punctuation conversion
        :return: Converted string or error message
        """
        return super().convert(input_text, punctuation)

    def jieba_cut(self, input_text: str, hmm: bool = True) -> List[str]:
        """
        Perform word segmentation on the input text using Jieba.

        :param input_text: The input string to segment.
        :param hmm: Whether to enable the Hidden Markov Model (HMM) for new word discovery.
        :return: A list of segmented words.
        """
        return super().jieba_cut(input_text, hmm)

    def jieba_cut_for_search(self, input_text: str, hmm: bool = True) -> List[str]:
        """
        Perform search-mode segmentation on the input text using Jieba.

        Search mode generates finer-grained tokens suitable for search indexing.

        :param input_text: The input string to segment.
        :param hmm: Whether to enable the Hidden Markov Model (HMM) for new word discovery.
        :return: A list of segmented words.
        """
        return super().jieba_cut_for_search(input_text, hmm)

    def jieba_cut_all(self, input_text: str) -> List[str]:
        """
        Perform full-mode segmentation on the input text using Jieba.

        Full mode returns all possible word segments without disambiguation.

        :param input_text: The input string to segment.
        :return: A list of segmented words.
        """
        return super().jieba_cut_all(input_text)

    def jieba_tag(self, input_text: str, hmm: bool = True) -> List[tuple[str, str]]:
        """
        Perform part-of-speech tagging on the input text using Jieba.

        :param input_text: The input string to analyze.
        :param hmm: Whether to enable the Hidden Markov Model (HMM) for new word discovery.
        :return: A list of (word, tag) tuples.
        """
        return super().jieba_tag(input_text, hmm)

    def jieba_cut_and_join(self, input_text: str, delimiter: str = "/") -> str:
        """
        Perform word segmentation and join the words with a custom delimiter.

        :param input_text: The input string to segment.
        :param delimiter: Delimiter to use between segmented words.
        :return: A single string with segmented words joined by the delimiter.
        """
        return super().jieba_cut_and_join(input_text, delimiter)

    def jieba_keyword_extract_textrank(self, input_text: str, top_k: int = 10) -> List[str]:
        """
        Extract top keywords using the TextRank algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :return: A list of top keywords.
        """
        return super().jieba_keyword_extract_textrank(input_text, top_k)

    def jieba_keyword_extract_tfidf(self, input_text: str, top_k: int = 10) -> List[str]:
        """
        Extract top keywords using the TF-IDF algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :return: A list of top keywords.
        """
        return super().jieba_keyword_extract_tfidf(input_text, top_k)

    def jieba_keyword_weight_textrank(self, input_text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Extract top keywords with their weights using the TextRank algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :return: A list of (keyword, weight) tuples.
        """
        return super().jieba_keyword_weight_textrank(input_text, top_k)

    def jieba_keyword_weight_tfidf(self, input_text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Extract top keywords with their weights using the TF-IDF algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :return: A list of (keyword, weight) tuples.
        """
        return super().jieba_keyword_weight_tfidf(input_text, top_k)
