from typing import List, Tuple
class OpenCC:
    """
    Python binding for OpenCC and Jieba functionalities.

    Provides Chinese text conversion (Simplified/Traditional), segmentation, and keyword extraction.

    Args:
        config (str): Optional conversion config (default: "s2t"). Must be one of:
            "s2t", "t2s", "s2tw", "tw2s", "s2twp", "tw2sp", "s2hk", "hk2s",
            "t2tw", "tw2t", "t2twp", "tw2tp", "t2hk", "hk2t", "t2jp", "jp2t".

    Attributes:
        config (str): Current OpenCC config string.
    """
    def __init__(self, config: str) -> None:
        """
        Initialize a new OpenCC instance.

        Args:
            config (str): Conversion config string.
        """
        self.config = config
        ...

    def convert(self, input_text: str, punctuation: bool) -> str:
        """
        Convert Chinese text using the current OpenCC config.

        Args:
            input_text (str): Input text.
            punctuation (bool): Whether to convert punctuation.

        Returns:
            str: Converted text.
        """
        ...

    def zho_check(self, input_text: str) -> int:
        """
        Detect the type of Chinese in the input text.

        Args:
            input_text (str): Input text.

        Returns:
            int: Integer code representing detected Chinese type.
            (1: Traditional, 2: Simplified, 0: Others)
        """
        ...

    def jieba_cut(self, input_text: str, hmm: bool) -> List[str]:
        """
        Segment Chinese text using Jieba.

        Args:
            input_text (str): Input text.
            hmm (bool): Whether to use HMM for new words.

        Returns:
            list[str]: List of segmented words.
        """
        ...

    def jieba_cut_for_search(self, input_text: str, hmm: bool) -> List[str]:
        """
        Segment Chinese text using Jieba search mode.

        This mode is suitable for search indexing and may return
        finer-grained tokens than normal cut mode.

        Args:
            input_text (str): Input text.
            hmm (bool): Whether to use HMM for new words.

        Returns:
            list[str]: List of segmented words.
        """
        ...

    def jieba_cut_all(self, input_text: str) -> List[str]:
        """
        Segment Chinese text using Jieba full mode.

        This mode attempts to cut out all possible words in the sentence.

        Args:
            input_text (str): Input text.

        Returns:
            list[str]: List of segmented words.
        """
        ...

    def jieba_tag(self, input_text: str, hmm: bool) -> List[Tuple[str, str]]:
        """
        Perform Jieba part-of-speech tagging.

        Args:
            input_text (str): Input text.
            hmm (bool): Whether to use HMM for new words.

        Returns:
            list[tuple[str, str]]: List of (word, tag) tuples.

        Example:
            >>> OpenCC.jieba_tag("我来到北京清华大学", True)
            [('我', 'r'), ('来到', 'v'), ('北京', 'ns'), ('清华大学', 'nt')]
        """
        ...

    def jieba_cut_and_join(self, input_text: str, delimiter: str = "/") -> str:
        """
        Segment and join Chinese text using Jieba.

        Args:
            input_text (str): Input text.
            delimiter (str): Delimiter for joining words.

        Returns:
            str: Joined segmented string.
        """
        ...

    def jieba_keyword_extract_textrank(self, input_text: str, top_k: int) -> List[str]:
        """
        Extract keywords using the TextRank algorithm.

        Args:
            input_text (str): Input text.
            top_k (int): Number of keywords to extract.

        Returns:
            list[str]: List of keywords.
        """
        ...

    def jieba_keyword_extract_tfidf(self, input_text: str, top_k: int) -> List[str]:
        """
        Extract keywords using the TF-IDF algorithm.

        Args:
            input_text (str): Input text.
            top_k (int): Number of keywords to extract.

        Returns:
            list[str]: List of keywords.
        """
        ...

    def jieba_keyword_weight_textrank(self, input_text: str, top_k: int) -> List[Tuple[str, float]]:
        """
        Extract keywords and their weights using TextRank.

        Args:
            input_text (str): Input text.
            top_k (int): Number of keywords to extract.

        Returns:
            list[tuple[str, float]]: List of (keyword, weight) tuples.
        """
        ...

    def jieba_keyword_weight_tfidf(self, input_text: str, top_k: int) -> List[Tuple[str, float]]:
        """
        Extract keywords and their weights using TF-IDF.

        Args:
            input_text (str): Input text.
            top_k (int): Number of keywords to extract.

        Returns:
            list[tuple[str, float]]: List of (keyword, weight) tuples.
        """
        ...