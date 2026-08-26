from typing import List, Tuple, Optional, TypedDict


class _UserDictEntryRequired(TypedDict):
    word: str
    freq: int


class UserDictEntry(_UserDictEntryRequired, total=False):
    tag: str


class _CustomDictSpecRequired(TypedDict):
    slot: str
    pairs: List[Tuple[str, str]]


class CustomDictSpec(_CustomDictSpecRequired, total=False):
    mode: str


class _CustomDictFileSpecRequired(TypedDict):
    slot: str
    files: List[str]


class CustomDictFileSpec(_CustomDictFileSpecRequired, total=False):
    mode: str


class OpenCC:
    """
    Python binding for OpenCC and Jieba functionalities.

    Provides Chinese text conversion (Simplified/Traditional), segmentation, and keyword extraction.

    Args:
    config: Optional conversion config. Defaults to ``"s2t"``.
        See ``supported_configs()`` for the complete list.

    Attributes:
        config (str): Current OpenCC config string.
    """
    config: str

    def __init__(self, config: str = "s2t") -> None:
        """
        Initialize a new OpenCC instance.

        Args:
            config (str): Conversion config string.
        """
        ...

    def set_config(self, config: str) -> None:
        """
        Set the OpenCC conversion configuration.

        Invalid configuration values fall back to "s2t".
        """
        ...

    @staticmethod
    def is_valid_config(config: str) -> bool:
        """
        Check whether a string is a valid OpenCC configuration.

        This method performs a case-insensitive check against all supported
        OpenCC conversion configurations (e.g. "s2t", "t2s", "s2tw").

        Parameters
        ----------
        config : str
            The configuration string to validate.

        Returns
        -------
        bool
            True if the configuration is valid, False otherwise.
        """
        ...

    @staticmethod
    def supported_configs() -> List[str]:
        """
        Return all supported OpenCC configuration names (canonical lowercase).

        Returns
        -------
        List[str]
        """
        ...

    @staticmethod
    def canonicalise_config(config: str) -> str:
        """
        Return the canonical OpenCC configuration name.

        This method validates the given configuration string and returns its
        canonical lowercase form. Matching is case-insensitive.

        Parameters
        ----------
        config : str
            The configuration string to normalize.

        Returns
        -------
        str
            The canonical configuration name (e.g. "s2t", "t2s").

        Raises
        ------
        ValueError
            If the provided configuration is not supported.
        """
        ...

    def get_config(self) -> str:
        """
        Get the current OpenCC configuration.

        Returns the canonical configuration string (always lowercase),
        regardless of how it was originally provided.

        Returns
        -------
        str
            The current configuration (e.g. "s2t", "t2s").
        """
        ...

    def apply_config(self, config: str) -> None:
        """
        Apply a new OpenCC configuration.

        The input is case-insensitive and will be normalized to the canonical
        lowercase form if valid.

        Parameters
        ----------
        config : str
            The configuration string to apply (e.g. "s2t", "t2s").

        Raises
        ------
        ValueError
            If the provided configuration is not supported.
        """
        ...

    def convert(self, input_text: str, punctuation: bool = False) -> str:
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

    def normalize_compat(self, text: str) -> str:
        """
        Normalize CJK Compatibility Ideographs using the built-in Unicode table.

        This is an optional Unicode compatibility normalization pre-pass. It does
        not modify this OpenCC instance, its selected config, conversion
        dictionaries, segmentation behavior, script detection, or punctuation
        conversion.

        Use this before ``convert()`` when input may contain CJK Compatibility
        Ideographs such as ``金``. Unmapped compatibility ideographs remain
        unchanged.

        :param text: Input text.
        :return: Normalized text.
        """
        ...

    def normalize_compat_extended(self, text: str) -> str:
        """
        Normalize extended Unicode compatibility forms and CJK Compatibility
        Ideographs using the built-in Unicode tables.

        This is a superset of ``normalize_compat()``.

        :param text: Input text.
        :return: Extended-normalized text.
        """
        ...

    def normalize_unicode_compat(self, text: str) -> str:
        """
        Normalize extended Unicode compatibility/variant forms only.

        Unlike ``normalize_compat_extended()``, this does not apply the
        CJK Compatibility Ideograph table.

        :param text: Input text.
        :return: Unicode-normalized text.
        """
        ...

    def load_user_dict_entries(self, entries: List[UserDictEntry]) -> None:
        """
        Post-load structured Jieba user-dictionary entries onto this instance.

        Each entry contains required ``word`` and ``freq`` fields and an
        optional ``tag`` field.

        This affects Jieba segmentation only. It does not modify OpenCC
        conversion dictionary slots.

        Example:
            >>> cc = OpenCC("s2t")
            >>> cc.load_user_dict_entries([
            ...     {"word": "帕兰蒂尔", "freq": 100000, "tag": "nz"}
            ... ])
        """
        ...

    def load_user_dict(self, path: str) -> None:
        """
        Post-load one Jieba user-dictionary file onto this instance.

        The file must use Jieba user-dictionary format::

            word freq [tag]

        ``freq`` is required and ``tag`` is optional.
        """
        ...

    def load_user_dict_files(self, files: List[str]) -> None:
        """
        Post-load multiple Jieba user-dictionary files in the supplied order.

        This is the multi-file convenience wrapper over ``load_user_dict()``.
        """
        ...

    def load_custom_dicts(self, specs: List[CustomDictSpec]) -> None:
        """
        Post-load custom OpenCC conversion dictionary entries onto this instance.

        Each spec contains a required ``slot`` and ``pairs`` field plus an
        optional ``mode`` field: ``"append"`` (default) or ``"override"``.
        """
        ...

    def load_custom_dict_files(self, specs: List[CustomDictFileSpec]) -> None:
        """
        Post-load custom OpenCC conversion dictionary files onto this instance.

        Each spec contains a required ``slot`` and ``files`` field plus an
        optional ``mode`` field: ``"append"`` (default) or ``"override"``.
        """
        ...

    @staticmethod
    def available_slots() -> List[str]:
        """Return canonical custom dictionary slot names from the Rust SSOT."""
        ...

    def jieba_cut(self, input_text: str, hmm: bool = True) -> List[str]:
        """
        Segment Chinese text using Jieba.

        Args:
            input_text (str): Input text.
            hmm (bool): Whether to use HMM for new words.

        Returns:
            list[str]: List of segmented words.
        """
        ...

    def jieba_cut_for_search(self, input_text: str, hmm: bool = True) -> List[str]:
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

    def jieba_tag(self, input_text: str, hmm: bool = True) -> List[Tuple[str, str]]:
        """
        Perform Jieba part-of-speech tagging.

        Args:
            input_text (str): Input text.
            hmm (bool): Whether to use HMM for new words.

        Returns:
            list[tuple[str, str]]: List of (word, tag) tuples.

        Example:
            >>> OpenCC().jieba_tag("我来到北京清华大学", True)
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

    def jieba_segment_join(
            self,
            input_text: str,
            mode: str = "cut",
            delim: str = " ",
            hmm: bool = True,
            separator: str = "/",
    ) -> str:
        """
        Segment Chinese text and join the result into a string.

        Args:
            input_text (str): Input text.
            mode (str): One of "cut", "search", "full", or "tag".
            delim (str): Delimiter used to join segments or tagged tokens.
            hmm (bool): Whether to use HMM for cut, search, and tag modes.
            separator (str): Separator between word and POS tag in tag mode.

        Returns:
            str: Joined segmentation output.
        """
        ...

    def jieba_keyword_extract_textrank(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Extract top keywords using the TextRank algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :param allowed_pos: Optional list of allowed part-of-speech (POS) tags.
            Each item may contain one or more POS tags separated by whitespace.

        Examples:
            - ["n"]                  → only nouns
            - ["n", "nr"]            → nouns and person names
            - ["n ns nt nz"]         → all noun-related tags
            - ["v", "vn"]            → verbs
            - ["n nr", "ns"]         → equivalent to ["n", "nr", "ns"]

            Common POS tags:
            - n  : noun
            - nr : person name
            - ns : place name
            - nt : organization
            - nz : proper noun
            - v  : verb

        :return: A list of top keywords.
        """
        ...

    def jieba_keyword_extract_tfidf(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Extract top keywords using the TF-IDF algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :param allowed_pos: Optional list of allowed part-of-speech (POS) tags.
                            Each item may contain one or more POS tags separated by whitespace.

        Examples:
            - ["n"]                  → only nouns
            - ["n", "nr"]            → nouns and person names
            - ["n ns nt nz"]         → all noun-related tags
            - ["v", "vn"]            → verbs
            - ["n nr", "ns"]         → equivalent to ["n", "nr", "ns"]

        Common POS tags:
            - n  : noun
            - nr : person name
            - ns : place name
            - nt : organization
            - nz : proper noun
            - v  : verb

        :return: A list of top keywords.
        """
        ...

    def jieba_keyword_weight_textrank(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Extract keywords and their weights using TextRank.

        Args:
            input_text (str): Input text.
            top_k (int): Number of keywords to extract.
            allowed_pos (Optional[list[str]]): Optional list of allowed part-of-speech tags.
                Each item may contain one or more POS tags separated by whitespace.

        Returns:
            list[tuple[str, float]]: List of (keyword, weight) tuples.
        """
        ...

    def jieba_keyword_weight_tfidf(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Extract keywords and their weights using TF-IDF.

        Args:
            input_text (str): Input text.
            top_k (int): Number of keywords to extract.
            allowed_pos (Optional[list[str]]): Optional list of allowed part-of-speech tags.
                Each item may contain one or more POS tags separated by whitespace.

        Returns:
            list[tuple[str, float]]: List of (keyword, weight) tuples.
        """
        ...
