from .opencc_jieba_pyo3 import OpenCC as _OpenCC
from typing import List, Tuple, Optional, TypedDict

_CustomDictPair = Tuple[str, str]


class _CustomDictSpecRequired(TypedDict):
    slot: str
    pairs: List[_CustomDictPair]


class CustomDictSpec(_CustomDictSpecRequired, total=False):
    mode: str


class _CustomDictFileSpecRequired(TypedDict):
    slot: str
    files: List[str]


class CustomDictFileSpec(_CustomDictFileSpecRequired, total=False):
    mode: str


class _UserDictEntryRequired(TypedDict):
    word: str
    freq: int


class UserDictEntry(_UserDictEntryRequired, total=False):
    tag: str


class OpenCC(_OpenCC):
    def __init__(self, config: str = "s2t") -> None:
        """
        Initialize a converter with the selected OpenCC configuration.

        The native PyO3 base instance is created by ``__new__`` before this
        Python ``__init__`` runs, so this wrapper must not call
        ``super().__init__()``.

        Invalid configurations fall back to ``"s2t"`` for compatibility with
        the existing Python wrapper behavior.
        """
        if super().is_valid_config(config):
            super().apply_config(config)
        else:
            self.config = "s2t"

    @classmethod
    def from_dicts(
            cls,
            config: str = "s2t",
            specs: Optional[List[CustomDictSpec]] = None,
    ) -> "OpenCC":
        """Create a converter with in-memory OpenCC custom dictionaries."""
        cc = cls(config)
        if specs:
            cc.load_custom_dicts(specs)
        return cc

    @classmethod
    def from_dict_files(
            cls,
            config: str = "s2t",
            specs: Optional[List[CustomDictFileSpec]] = None,
    ) -> "OpenCC":
        """Create a converter with OpenCC custom dictionary files."""
        cc = cls(config)
        if specs:
            cc.load_custom_dict_files(specs)
        return cc

    @classmethod
    def from_user_dict_entries(
            cls,
            config: str = "s2t",
            entries: Optional[List[UserDictEntry]] = None,
    ) -> "OpenCC":
        """Create a converter with in-memory Jieba user-dictionary entries."""
        cc = cls(config)
        if entries:
            cc.load_user_dict_entries(entries)
        return cc

    @classmethod
    def from_user_dict_files(
            cls,
            config: str = "s2t",
            files: Optional[List[str]] = None,
    ) -> "OpenCC":
        """Create a converter with Jieba user-dictionary files."""
        cc = cls(config)
        if files:
            cc.load_user_dict_files(files)
        return cc

    def set_config(self, config) -> None:
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

    def get_config(self) -> str:
        """
        Get the current conversion config.

        :return: Current config string
        """
        return self.config

    def load_user_dict_entries(self, entries: List[UserDictEntry]) -> None:
        """Post-load structured Jieba user-dictionary entries."""
        super().load_user_dict_entries(entries)

    def load_user_dict_files(self, files: List[str]) -> None:
        """Post-load one or more Jieba user-dictionary files in order."""
        super().load_user_dict_files(files)

    def load_custom_dicts(self, specs: List[CustomDictSpec]) -> None:
        """Post-load in-memory OpenCC custom conversion dictionaries."""
        super().load_custom_dicts(specs)

    def load_custom_dict_files(self, specs: List[CustomDictFileSpec]) -> None:
        """Post-load OpenCC custom conversion dictionary files."""
        super().load_custom_dict_files(specs)

    @staticmethod
    def available_slots() -> List[str]:
        """Return canonical OpenCC dictionary slot names."""
        return _OpenCC.available_slots()

    def zho_check(self, input_text) -> int:
        """
        Heuristically determine whether input text is Simplified or Traditional Chinese.

        :param input_text: Input string
        :return: 0 = unknown, 2 = simplified, 1 = traditional
        """
        return super().zho_check(input_text)

    def convert(self, input_text, punctuation=False) -> str:
        """
        Automatically dispatch to the appropriate conversion method based on `self.config`.

        :param input_text: The string to convert
        :param punctuation: Whether to apply punctuation conversion
        :return: Converted string or error message
        """
        return super().convert(input_text, punctuation)

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

        DeToFu is the opposite side of the pipeline: compatibility ideograph
        normalization is a pre-processing step, while ``detofu()`` is an
        optional post-processing display fallback.

        :param text: Input text.
        :return: Normalized text.
        """
        return super().normalize_compat(text)

    def normalize_compat_extended(self, text: str) -> str:
        """
        Normalize extended Unicode compatibility forms and CJK Compatibility
        Ideographs using the built-in Unicode tables.

        This is an optional Unicode compatibility normalization pre-pass and is
        a superset of ``normalize_compat()``.

        :param text: Input text.
        :return: Extended-normalized text.
        """
        return super().normalize_compat_extended(text)

    def normalize_unicode_compat(self, text: str) -> str:
        """
        Normalize extended Unicode compatibility/variant forms only.

        Unlike ``normalize_compat_extended()``, this does not apply the
        CJK Compatibility Ideograph table.

        :param text: Input text.
        :return: Unicode-normalized text.
        """
        return super().normalize_unicode_compat(text)

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

    def jieba_tag(self, input_text: str, hmm: bool = True) -> List[Tuple[str, str]]:
        """
        Perform part-of-speech tagging on the input text using Jieba.

        :param input_text: The input string to analyze.
        :param hmm: Whether to enable the Hidden Markov Model (HMM) for new word discovery.
        :return: A list of (word, tag) tuples.
        """
        return super().jieba_tag(input_text, hmm)

    def jieba_cut_and_join(self, input_text: str, delimiter: str = "/") -> str:
        """
        ⚠️ Deprecated: Use `jieba_segment_join(..., mode="cut")` instead.

        Perform word segmentation and join the words with a custom delimiter.

        :param input_text: The input string to segment.
        :param delimiter: Delimiter to use between segmented words.
        :return: A single string with segmented words joined by the delimiter.
        """
        import warnings

        warnings.warn(
            "jieba_cut_and_join() is deprecated and will be removed in a future version. "
            "Use jieba_segment_join(input_text, mode='cut', delim=...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Forward to new unified API
        return self.jieba_segment_join(
            input_text,
            mode="cut",
            delim=delimiter,
        )

    def jieba_segment_join(
            self,
            input_text: str,
            mode: str = "cut",
            delim: str = " ",
            hmm: bool = True,
            separator: str = "/",
    ) -> str:
        """
        Perform Jieba segmentation and join result into a string.

        :param input_text: Input text to segment
        :param mode: Segmentation mode:
                     - "cut"    : Accurate mode (default)
                     - "search" : Search engine mode
                     - "full"   : Full mode
                     - "tag"    : POS tagging mode (word/tag)
        :param delim: Delimiter used to join tokens (default: " ")
                      Example: delim="|" -> 我|来到|北京
        :param hmm: Enable Hidden Markov Model (HMM)
        :param separator: Separator between word and POS tag in ``mode="tag"``.
                          Default is ``"/"`` (standard Jieba format).
        :return: Joined string result

        Notes:
            - You can fully customize output using both delim and separator.

        Examples:
            >>> cc = OpenCC()
            >>> cc.jieba_segment_join("我来到北京清华大学", delim="/")
            '我/来到/北京/清华大学'

            >>> cc.jieba_segment_join("我来到北京清华大学", delim="|")
            '我|来到|北京|清华大学'

            >>> cc.jieba_segment_join("我来到北京清华大学", mode="search")
            '我/来到/北京/清华/华大/大学/清华大学'

            >>> cc.jieba_segment_join("我来到北京清华大学", mode="tag")
            '我/r 来到/v 北京/ns 清华大学/nt'

            >>> cc.jieba_segment_join(
            ...     "我来到北京清华大学",
            ...     mode="tag",
            ...     delim=" | ",
            ...     separator=":"
            ... )
            '我:r | 来到:v | 北京:ns | 清华大学:nt'
        """

        mode = mode.lower()

        if mode == "cut":
            return delim.join(super().jieba_cut(input_text, hmm))

        elif mode == "search":
            return delim.join(super().jieba_cut_for_search(input_text, hmm))

        elif mode == "full":
            return delim.join(super().jieba_cut_all(input_text))

        elif mode == "tag":
            tagged = super().jieba_tag(input_text, hmm)
            return delim.join(f"{w}{separator}{t}" for w, t in tagged)

        else:
            raise ValueError(
                f"Unsupported mode: {mode}. "
                f"Supported modes: cut | search | full | tag"
            )

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
        return super().jieba_keyword_extract_textrank(input_text, top_k, allowed_pos)

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
        return super().jieba_keyword_extract_tfidf(input_text, top_k, allowed_pos)

    def jieba_keyword_weight_textrank(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Extract top keywords with their weights using the TextRank algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :param allowed_pos: Optional list of allowed part-of-speech tags.
                            Each item may contain one or more POS tags separated by whitespace.
        :return: A list of (keyword, weight) tuples.
        """
        return super().jieba_keyword_weight_textrank(input_text, top_k, allowed_pos)

    def jieba_keyword_weight_tfidf(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Extract top keywords with their weights using the TF-IDF algorithm.

        :param input_text: The input text to analyze.
        :param top_k: The number of top keywords to extract.
        :param allowed_pos: Optional list of allowed part-of-speech tags.
                            Each item may contain one or more POS tags separated by whitespace.
        :return: A list of (keyword, weight) tuples.
        """
        return super().jieba_keyword_weight_tfidf(input_text, top_k, allowed_pos)


__all__ = [
    "OpenCC",
    "CustomDictSpec",
    "CustomDictFileSpec",
    "UserDictEntry",
]
