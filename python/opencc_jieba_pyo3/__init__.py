from .opencc_jieba_pyo3 import OpenCC as _OpenCC
from typing import List, Tuple, Optional, TypedDict

_CustomDictPair = Tuple[str, str]


class _CustomDictSpecRequired(TypedDict):
    slot: str
    pairs: List[_CustomDictPair]


class CustomDictSpec(_CustomDictSpecRequired, total=False):
    """In-memory OpenCC replacements for one dictionary slot.

    Required keys are ``slot`` (see ``OpenCC.available_slots()``) and ``pairs``
    (a list of source/target string tuples). Optional ``mode`` is ``"append"``
    by default, or ``"override"`` to clear that slot before inserting pairs.
    This defines conversion mappings, not Jieba word frequencies or POS tags.
    """
    mode: str


class _CustomDictFileSpecRequired(TypedDict):
    slot: str
    files: List[str]


class CustomDictFileSpec(_CustomDictFileSpecRequired, total=False):
    """UTF-8 OpenCC mapping files to load into one dictionary slot.

    Required keys are ``slot`` and ``files`` (a list of paths). Each file uses
    ``source<TAB>target`` lines, with an actual tab between the fields.
    Optional ``mode`` is ``"append"`` (default) or ``"override"``; override
    replaces the selected slot with the combined mappings from the files.
    These files have a different format from Jieba user dictionaries.
    """
    mode: str


class _UserDictEntryRequired(TypedDict):
    word: str
    freq: int


class UserDictEntry(_UserDictEntryRequired, total=False):
    """A Jieba word entry for segmentation and part-of-speech tagging.

    Required keys are ``word`` (a nonempty word without whitespace) and ``freq``
    (a non-negative integer that fits the platform's Rust ``usize``). Optional
    ``tag`` supplies a POS tag such as ``"nz"``. This registers a word without
    defining a Simplified/Traditional replacement; use ``CustomDictSpec`` for
    conversion mappings. Use ``add_word()`` to choose frequency automatically.
    """
    tag: str


class OpenCC(_OpenCC):
    """Convert Chinese text and access Jieba segmentation and keyword extraction.

    ``config`` selects the conversion direction and regional vocabulary, for
    example ``"s2t"`` (Simplified to Traditional), ``"t2s"`` (the reverse), or
    ``"s2twp"`` (Simplified to Taiwan Traditional with phrase conversion).
    Names are case-insensitive; unsupported names fall back to ``"s2t"``.
    Use ``supported_configs()`` to discover all supported names.

    ``convert()`` uses the selected configuration. The ``jieba_*`` methods
    analyze the text supplied to them without first converting its script.
    OpenCC custom dictionaries define replacement text; Jieba user dictionaries
    define word boundaries, frequencies, and part-of-speech (POS) tags.
    Both kinds of customization belong to this converter instance.

    Attributes:
        config (str): Current canonical lowercase configuration name. Assigning
            an unsupported name raises ValueError; ``set_config()`` instead
            falls back to ``"s2t"``.
    """
    def __init__(self, config: str = "s2t") -> None:
        """Create a converter with built-in OpenCC and Jieba dictionaries.

        Args:
            config (str): Conversion name, case-insensitive. Defaults to ``"s2t"``
                (Simplified to Traditional); an unsupported name also uses ``"s2t"``.
                See ``supported_configs()`` for the complete list.

        Custom mappings and segmentation words can be loaded afterward with
        ``load_custom_dicts()`` and ``load_user_dict_entries()`` respectively.
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
        """Create a converter and load in-memory OpenCC conversion mappings.

        Equivalent to constructing ``cls(config)`` and calling ``load_custom_dicts(specs)``
        when ``specs`` is nonempty. See ``load_custom_dicts()`` for the required format,
        merge or loading behavior, and exceptions.

        Args:
            config (str): Conversion name, case-insensitive; defaults and falls back
                to ``"s2t"`` for an unsupported name.
            specs: Optional loader input. None or an empty list keeps the built-in
                dictionaries without loading additional data.

        Returns:
            OpenCC: A new converter with the supplied customizations applied.

        Loader errors propagate to the caller instead of returning a converter.
        """
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
        """Create a converter and load OpenCC conversion mapping files.

        Equivalent to constructing ``cls(config)`` and calling ``load_custom_dict_files(specs)``
        when ``specs`` is nonempty. See ``load_custom_dict_files()`` for the required format,
        merge or loading behavior, and exceptions.

        Args:
            config (str): Conversion name, case-insensitive; defaults and falls back
                to ``"s2t"`` for an unsupported name.
            specs: Optional loader input. None or an empty list keeps the built-in
                dictionaries without loading additional data.

        Returns:
            OpenCC: A new converter with the supplied customizations applied.

        Loader errors propagate to the caller instead of returning a converter.
        """
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
        """Create a converter and load in-memory Jieba word entries.

        Equivalent to constructing ``cls(config)`` and calling ``load_user_dict_entries(entries)``
        when ``entries`` is nonempty. See ``load_user_dict_entries()`` for the required format,
        merge or loading behavior, and exceptions.

        Args:
            config (str): Conversion name, case-insensitive; defaults and falls back
                to ``"s2t"`` for an unsupported name.
            entries: Optional loader input. None or an empty list keeps the built-in
                dictionaries without loading additional data.

        Returns:
            OpenCC: A new converter with the supplied customizations applied.

        Loader errors propagate to the caller instead of returning a converter.
        """
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
        """Create a converter and load Jieba user-dictionary files.

        Equivalent to constructing ``cls(config)`` and calling ``load_user_dict_files(files)``
        when ``files`` is nonempty. See ``load_user_dict_files()`` for the required format,
        merge or loading behavior, and exceptions.

        Args:
            config (str): Conversion name, case-insensitive; defaults and falls back
                to ``"s2t"`` for an unsupported name.
            files: Optional loader input. None or an empty list keeps the built-in
                dictionaries without loading additional data.

        Returns:
            OpenCC: A new converter with the supplied customizations applied.

        Loader errors propagate to the caller instead of returning a converter.
        """
        cc = cls(config)
        if files:
            cc.load_user_dict_files(files)
        return cc

    def set_config(self, config) -> None:
        """Select the conversion used by subsequent ``convert()`` calls.

        Args:
            config (str): Supported configuration name, matched case-insensitively
                and stored in lowercase. Unsupported names select ``"s2t"``.

        Existing custom mappings and Jieba words are retained. For strict validation
        that raises ValueError on an unsupported name, use ``apply_config()`` or
        assign to ``config`` directly.
        """
        if super().is_valid_config(config):
            super().apply_config(config)
        else:
            self.config = "s2t"

    def get_config(self) -> str:
        """Return the current conversion configuration as a lowercase name.

        This is the same value exposed by ``config``, for example ``"s2t"`` or
        ``"t2s"``. It controls ``convert()``, not standalone Jieba analysis.
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
        """Return supported OpenCC conversion dictionary slot names.

        Use these names as ``slot`` in ``load_custom_dicts()`` or
        ``load_custom_dict_files()``. For example, ``"STCharacters"`` and
        ``"STPhrases"`` participate in Simplified-to-Traditional conversion.
        A custom mapping takes effect only when the active configuration uses
        its slot. These names are dictionary slots, not configuration names.
        """
        return _OpenCC.available_slots()

    def zho_check(self, input_text) -> int:
        """Heuristically classify the Chinese script in a sample of the text.

        Args:
            input_text (str): Text to inspect; the backend checks a bounded prefix.

        Returns:
            int: 1 for Traditional, 2 for Simplified, or 0 for undetermined,
            including empty text and text with no distinguishing Chinese forms.

        The result is a heuristic, not a language identifier or a reliable mixed
        script classifier. It does not change ``config`` or convert the input.
        """
        return super().zho_check(input_text)

    def convert(self, input_text, punctuation=False) -> str:
        """Return text converted according to this instance's ``config``.

        The configuration selects the direction and regional conversion rules;
        this method does not detect the input script and choose a direction.
        Conversion uses the current OpenCC mappings and Jieba segmentation state.

        Args:
            input_text (str): Text to convert.
            punctuation (bool): Apply the configuration's punctuation conversion
                when True (for example, curly quotes to corner brackets in
                ``"s2t"``). Defaults to False.

        Returns:
            str: Converted text as a single string, without segmentation delimiters.

        Compatibility normalization and DeTofu fallback are separate optional
        steps; call ``normalize_compat*()`` before conversion and ``detofu()`` after.

        Example:
            >>> OpenCC("s2t").convert("汉语")
            '漢語'
        """
        return super().convert(input_text, punctuation)

    def normalize_compat(self, text: str) -> str:
        """Map CJK Compatibility Ideographs to their unified forms.

        Uses the built-in Unicode mapping table, for example ``"金"`` becomes
        ``"金"``. Unmapped characters are preserved. This returns a new string
        without changing the converter's configuration or dictionaries.

        Args:
            text (str): Text containing possible CJK Compatibility Ideographs.

        Returns:
            str: Normalized text. This does not perform Simplified/Traditional
            conversion; pass the result to ``convert()`` when needed.

        Use ``normalize_unicode_compat()`` for the extended compatibility/variant
        table alone, or ``normalize_compat_extended()`` to apply both tables.
        """
        return super().normalize_compat(text)

    def normalize_compat_extended(self, text: str) -> str:
        """Normalize both extended compatibility forms and CJK Compatibility Ideographs.

        Applies the built-in extended Unicode compatibility/variant mappings
        together with the CJK Compatibility Ideograph table. This covers both
        ``normalize_unicode_compat()`` and ``normalize_compat()`` mappings.

        Args:
            text (str): Text to normalize before optional OpenCC conversion.

        Returns:
            str: Text with mapped forms normalized and unmapped characters retained.

        This table-based operation is separate from Simplified/Traditional
        conversion and does not change the converter's configuration or dictionaries.
        """
        return super().normalize_compat_extended(text)

    def normalize_unicode_compat(self, text: str) -> str:
        """Normalize forms covered by the extended Unicode compatibility/variant table.

        Applies only the built-in extended table; it does not apply the separate
        CJK Compatibility Ideograph table. Use ``normalize_compat_extended()``
        to combine both. This API is table-based, not a general Unicode NFKC API.

        Args:
            text (str): Text to normalize before optional OpenCC conversion.

        Returns:
            str: Text with mapped forms normalized and unmapped characters retained.

        This does not perform Simplified/Traditional conversion or change the
        converter's configuration or dictionaries.
        """
        return super().normalize_unicode_compat(text)

    def jieba_cut(self, input_text: str, hmm: bool = True) -> List[str]:
        """Segment the supplied text into words using Jieba's accurate mode.

        This mode chooses a segmentation, unlike full mode which includes
        overlapping dictionary matches. The selected OpenCC ``config`` does not
        convert the text before segmentation.

        Args:
            input_text (str): Text to segment.
            hmm (bool): Enable the Hidden Markov Model for recognizing words beyond
                dictionary matches. Defaults to True.

        Returns:
            List[str]: Tokens in text order, using this instance's Jieba dictionary.

        Example:
            >>> OpenCC().jieba_cut("我来到北京清华大学")
            ['我', '来到', '北京', '清华大学']
        """
        return super().jieba_cut(input_text, hmm)

    def jieba_cut_for_search(self, input_text: str, hmm: bool = True) -> List[str]:
        """Segment text into overlapping tokens for search indexing.

        Starts from accurate-mode segmentation and adds shorter dictionary words
        within longer tokens. For example, ``"清华大学"`` can produce ``"清华"``,
        ``"华大"``, ``"大学"``, and ``"清华大学"``. Joining the output does not
        reconstruct the input because these tokens overlap.

        Args:
            input_text (str): Text to segment, without automatic OpenCC conversion.
            hmm (bool): Enable HMM recognition of words beyond dictionary matches.
                Defaults to True.

        Returns:
            List[str]: Search tokens, including shorter matches and original words.
        """
        return super().jieba_cut_for_search(input_text, hmm)

    def jieba_cut_all(self, input_text: str) -> List[str]:
        """Return Jieba full-mode dictionary matches without disambiguation.

        This mode includes overlapping word candidates rather than choosing one
        segmentation. Use ``jieba_cut()`` for ordinary word segmentation or
        ``jieba_cut_for_search()`` to expand accurate-mode tokens for indexing.
        Full mode has no HMM option.

        Args:
            input_text (str): Text to segment, without automatic OpenCC conversion.

        Returns:
            List[str]: Word candidates; joining them may repeat overlapping text.
        """
        return super().jieba_cut_all(input_text)

    def jieba_tag(self, input_text: str, hmm: bool = True) -> List[Tuple[str, str]]:
        """Segment text and attach a Jieba part-of-speech tag to each token.

        Args:
            input_text (str): Text to analyze, without automatic OpenCC conversion.
            hmm (bool): Enable HMM recognition of words beyond dictionary matches.
                Defaults to True.

        Returns:
            List[Tuple[str, str]]: ``(word, tag)`` pairs in text order. Common tags
            include ``"n"`` (noun), ``"nr"`` (person), ``"ns"`` (place), ``"nt"``
            (organization), and ``"v"`` (verb). User-dictionary tags are available
            to subsequent tagging calls.
        """
        return super().jieba_tag(input_text, hmm)

    def jieba_cut_and_join(self, input_text: str, delimiter: str = "/") -> str:
        """Segment in accurate mode with HMM enabled and join the tokens.

        Deprecated: emits DeprecationWarning. Use
        ``jieba_segment_join(input_text, mode="cut", delim=delimiter)`` instead.

        Args:
            input_text (str): Text to segment, without automatic OpenCC conversion.
            delimiter (str): Text inserted between tokens. Defaults to ``"/"``;
                pass it as ``delim`` when migrating to ``jieba_segment_join()``.

        Returns:
            str: Tokens joined with the chosen delimiter.
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
        """Segment or POS-tag text and format the result as one string.

        Args:
            input_text (str): Text to analyze, without automatic OpenCC conversion.
            mode (str): Case-insensitive mode: ``"cut"`` chooses accurate-mode
                words; ``"search"`` adds overlapping search tokens; ``"full"``
                returns dictionary candidates without disambiguation; ``"tag"``
                formats each token as a word and POS tag. Defaults to ``"cut"``.
            delim (str): Text inserted between tokens (or word/tag pairs).
                Defaults to a space for every mode.
            hmm (bool): Enable HMM recognition in cut, search, and tag modes.
                Defaults to True; ignored in full mode.
            separator (str): Text between word and POS tag in tag mode, default
                ``"/"``. Ignored in the other modes.

        Returns:
            str: Formatted tokens. Search and full modes may repeat overlapping text.

        Raises:
            ValueError: If mode is not cut, search, full, or tag.

        Examples:
            >>> cc = OpenCC()
            >>> cc.jieba_segment_join("我来到北京清华大学", delim="/")
            '我/来到/北京/清华大学'
            >>> cc.jieba_segment_join("我来到北京清华大学", mode="search")
            '我 来到 北京 清华 华大 大学 清华大学'
            >>> cc.jieba_segment_join(
            ...     "我来到北京清华大学", mode="tag", delim=" | ", separator=":"
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
        """Extract keyword strings using TextRank.

        TextRank ranks words using a graph of word co-occurrences in the input.
        Analysis uses the supplied text and current Jieba dictionary, without
        applying the selected OpenCC conversion configuration.

        Args:
            input_text (str): Text to analyze.
            top_k (int): Maximum number of results, default 10. Zero or negative
                values return an empty list; filtering may yield fewer results.
            allowed_pos (Optional[List[str]]): Exact Jieba POS tags to allow.
                Each item is split on whitespace, so ``["n nr", "ns"]`` and
                ``["n", "nr", "ns"]`` are equivalent. ``"n"`` does not include
                every noun subtype. None, an empty list, or whitespace-only items
                apply no explicit POS restriction; algorithm filtering still applies.

        Returns:
            List[str]: Keywords ranked by score, without weights.

        Use ``jieba_keyword_weight_textrank()`` for keyword/weight pairs.
        """
        return super().jieba_keyword_extract_textrank(input_text, top_k, allowed_pos)

    def jieba_keyword_extract_tfidf(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[str]:
        """Extract keyword strings using TF-IDF.

        TF-IDF combines word frequency in the input with Jieba's built-in inverse
        document frequency data; it does not train a new corpus from this call.
        Analysis uses the supplied text and current Jieba dictionary, without
        applying the selected OpenCC conversion configuration.

        Args:
            input_text (str): Text to analyze.
            top_k (int): Maximum number of results, default 10. Zero or negative
                values return an empty list; filtering may yield fewer results.
            allowed_pos (Optional[List[str]]): Exact Jieba POS tags to allow.
                Each item is split on whitespace, so ``["n nr", "ns"]`` and
                ``["n", "nr", "ns"]`` are equivalent. ``"n"`` does not include
                every noun subtype. None, an empty list, or whitespace-only items
                apply no explicit POS restriction; algorithm filtering still applies.

        Returns:
            List[str]: Keywords ranked by score, without weights.

        Use ``jieba_keyword_weight_tfidf()`` for keyword/weight pairs.
        """
        return super().jieba_keyword_extract_tfidf(input_text, top_k, allowed_pos)

    def jieba_keyword_weight_textrank(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[Tuple[str, float]]:
        """Extract weighted keywords using TextRank.

        TextRank ranks words using a graph of word co-occurrences in the input.
        Analysis uses the supplied text and current Jieba dictionary, without
        applying the selected OpenCC conversion configuration.

        Args:
            input_text (str): Text to analyze.
            top_k (int): Maximum number of results, default 10. Zero or negative
                values return an empty list; filtering may yield fewer results.
            allowed_pos (Optional[List[str]]): Exact Jieba POS tags to allow.
                Each item is split on whitespace, so ``["n nr", "ns"]`` and
                ``["n", "nr", "ns"]`` are equivalent. ``"n"`` does not include
                every noun subtype. None, an empty list, or whitespace-only items
                apply no explicit POS restriction; algorithm filtering still applies.

        Returns:
            List[Tuple[str, float]]: ``(keyword, weight)`` pairs ranked by score.
            Weights are algorithm scores, not occurrence counts or probabilities.

        Use ``jieba_keyword_extract_textrank()`` for keyword strings without scores.
        """
        return super().jieba_keyword_weight_textrank(input_text, top_k, allowed_pos)

    def jieba_keyword_weight_tfidf(
            self,
            input_text: str,
            top_k: int = 10,
            allowed_pos: Optional[List[str]] = None,
    ) -> List[Tuple[str, float]]:
        """Extract weighted keywords using TF-IDF.

        TF-IDF combines word frequency in the input with Jieba's built-in inverse
        document frequency data; it does not train a new corpus from this call.
        Analysis uses the supplied text and current Jieba dictionary, without
        applying the selected OpenCC conversion configuration.

        Args:
            input_text (str): Text to analyze.
            top_k (int): Maximum number of results, default 10. Zero or negative
                values return an empty list; filtering may yield fewer results.
            allowed_pos (Optional[List[str]]): Exact Jieba POS tags to allow.
                Each item is split on whitespace, so ``["n nr", "ns"]`` and
                ``["n", "nr", "ns"]`` are equivalent. ``"n"`` does not include
                every noun subtype. None, an empty list, or whitespace-only items
                apply no explicit POS restriction; algorithm filtering still applies.

        Returns:
            List[Tuple[str, float]]: ``(keyword, weight)`` pairs ranked by score.
            Weights are algorithm scores, not occurrence counts or probabilities.

        Use ``jieba_keyword_extract_tfidf()`` for keyword strings without scores.
        """
        return super().jieba_keyword_weight_tfidf(input_text, top_k, allowed_pos)


__all__ = [
    "OpenCC",
    "CustomDictSpec",
    "CustomDictFileSpec",
    "UserDictEntry",
]
