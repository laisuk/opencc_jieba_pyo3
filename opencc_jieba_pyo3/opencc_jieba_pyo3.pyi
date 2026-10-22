from typing import List, Tuple, Optional, TypedDict


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


class _CustomDictSpecRequired(TypedDict):
    slot: str
    pairs: List[Tuple[str, str]]


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


class OpenCC:
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
    config: str

    def __init__(self, config: str = "s2t") -> None:
        """Create a converter with built-in OpenCC and Jieba dictionaries.

        Args:
            config (str): Conversion name, case-insensitive. Defaults to ``"s2t"``
                (Simplified to Traditional); an unsupported name also uses ``"s2t"``.
                See ``supported_configs()`` for the complete list.

        Custom mappings and segmentation words can be loaded afterward with
        ``load_custom_dicts()`` and ``load_user_dict_entries()`` respectively.
        """
        ...

    def set_config(self, config: str) -> None:
        """Select the conversion used by subsequent ``convert()`` calls.

        Args:
            config (str): Supported configuration name, matched case-insensitively
                and stored in lowercase. Unsupported names select ``"s2t"``.

        Existing custom mappings and Jieba words are retained. For strict validation
        that raises ValueError on an unsupported name, use ``apply_config()`` or
        assign to ``config`` directly.
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
        """Return the current conversion configuration as a lowercase name.

        This is the same value exposed by ``config``, for example ``"s2t"`` or
        ``"t2s"``. It controls ``convert()``, not standalone Jieba analysis.
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
        ...

    def zho_check(self, input_text: str) -> int:
        """Heuristically classify the Chinese script in a sample of the text.

        Args:
            input_text (str): Text to inspect; the backend checks a bounded prefix.

        Returns:
            int: 1 for Traditional, 2 for Simplified, or 0 for undetermined,
            including empty text and text with no distinguishing Chinese forms.

        The result is a heuristic, not a language identifier or a reliable mixed
        script classifier. It does not change ``config`` or convert the input.
        """
        ...

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
        ...

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
        ...

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
        ...

    def detofu(self, text: str, level: str = "ExtB") -> str:
        """
        Apply the built-in DeTofu fallback mappings.

        DeTofu replaces selected CJK Extension characters with display-compatible
        fallback characters when a built-in mapping is available. Characters
        without a matching fallback mapping remain unchanged.

        ``level`` is case-insensitive and accepts:

        - ``"all"`` or ``"ExtB"``: Extension B and all supported later extensions
        - ``"ExtC"``: Extension C and later
        - ``"ExtD"``: Extension D and later
        - ``"ExtE"``: Extension E and later
        - ``"ExtF"``: Extension F and later
        - ``"ExtG"``: Extension G and later
        - ``"ExtH"``: Extension H and later
        - ``"ExtI"``: Extension I only

        This is intended as an optional post-processing step after ``convert()``.
        It does not modify this OpenCC instance, its selected config, conversion
        dictionaries, or Jieba segmentation state.

        Args:
            text (str): Input text.
            level (str): Minimum CJK extension level. Defaults to ``"ExtB"``.

        Returns:
            str: Text after DeTofu fallback replacement.

        Raises:
            ValueError: If ``level`` is not supported.

        Example:
            >>> cc = OpenCC("t2s")
            >>> converted = cc.convert("驂𬴂", False)
            >>> cc.detofu(converted, "ExtB")
            '骖騑'
        """
        ...

    def detofu_with_custom_file(
            self,
            text: str,
            level: str,
            path: str,
    ) -> str:
        """
        Apply DeTofu using the built-in mappings plus a custom fallback file.

        The custom UTF-8 file is loaded in addition to the built-in DeTofu
        mappings. Custom mappings override built-in mappings for the same source
        character.

        ``level`` uses the same case-insensitive values accepted by
        ``detofu()``: ``"all"``, ``"ExtB"``, ``"ExtC"``, ``"ExtD"``,
        ``"ExtE"``, ``"ExtF"``, ``"ExtG"``, ``"ExtH"``, or ``"ExtI"``.

        This is an optional post-processing operation after ``convert()`` and
        does not modify this OpenCC instance, its selected config, custom OpenCC
        dictionaries, Jieba user dictionaries, or segmentation state.

        Args:
            text (str): Input text.
            level (str): Minimum CJK extension level.
            path (str): Path to a UTF-8 custom DeTofu mapping file.

        Returns:
            str: Text after built-in and custom DeTofu fallback replacement.

        Raises:
            ValueError: If ``level`` is invalid or the custom mapping file
                cannot be loaded or parsed.

        Example:
            >>> cc = OpenCC("t2s")
            >>> converted = cc.convert("驂𬴂", False)
            >>> cc.detofu_with_custom_file(
            ...     converted,
            ...     "ExtB",
            ...     "custom_tofu.txt",
            ... )
            '骖騑'
        """
        ...

    def load_user_dict_entries(self, entries: List[UserDictEntry]) -> None:
        """Add structured words to this instance's Jieba dictionary.

        Args:
            entries (List[UserDictEntry]): Dictionaries with required ``word`` and
                non-negative ``freq`` fields and an optional POS ``tag``.
                Words must be nonempty and contain no whitespace.

        Updates segmentation and POS information. It does not define conversion
        replacements; use ``load_custom_dicts()`` for those. Changed word boundaries
        may indirectly affect phrase conversion. Use ``add_word()`` for a single
        word with an automatically selected frequency.

        Raises:
            ValueError: If the backend rejects an entry.
            OverflowError: If a frequency does not fit the platform's Rust usize.
        """
        ...

    def load_user_dict(self, path: str) -> None:
        """Load a UTF-8 Jieba user-dictionary file into this instance.

        Args:
            path (str): Relative or absolute file path. Lines use whitespace-separated
                ``word freq [tag]`` fields; frequency is required, POS tag optional.

        Adds words to the existing Jieba dictionary. This affects segmentation and
        tagging, and may indirectly affect phrase conversion through word boundaries.
        It does not load OpenCC source/target mappings. Use
        ``load_custom_dict_files()`` for conversion dictionaries.

        Raises:
            ValueError: If the file cannot be read or parsed.
        """
        ...

    def load_user_dict_files(self, files: List[str]) -> None:
        """Load multiple Jieba user-dictionary files in the supplied order.

        Args:
            files (List[str]): Relative or absolute paths to UTF-8 files containing
                whitespace-separated ``word freq [tag]`` lines.

        Calls ``load_user_dict()`` for each path. Earlier successfully loaded files
        remain applied if a later file fails; the whole call is not rolled back.
        This extends the current Jieba dictionary, not OpenCC replacement mappings.
        An empty list does nothing.

        Raises:
            ValueError: If a file cannot be read or parsed.
        """
        ...

    def load_custom_dicts(self, specs: List[CustomDictSpec]) -> None:
        """Merge or replace OpenCC source/target mappings in selected slots.

        Args:
            specs (List[CustomDictSpec]): Dictionaries with required ``slot`` and
                ``pairs`` fields. Pairs are ``(source, target)`` string tuples.
                Optional ``mode`` is ``"append"`` (default) or ``"override"``.

        Append preserves unrelated mappings; duplicate source keys use the last
        supplied value. Override clears only the selected slot before inserting
        pairs. Use ``available_slots()`` for supported names. Mappings remain across
        configuration changes and affect conversions that use their slot.

        This does not register phrases with Jieba. Use ``add_word()`` or
        ``load_user_dict_entries()`` too when a phrase needs to be a single token.

        Raises:
            ValueError: If a slot or mode is invalid or mappings are rejected.
        """
        ...

    def load_custom_dict_files(self, specs: List[CustomDictFileSpec]) -> None:
        """Load UTF-8 OpenCC source/target files into selected dictionary slots.

        Args:
            specs (List[CustomDictFileSpec]): Dictionaries with required ``slot``
                and ``files`` fields. Paths may be relative or absolute. Optional
                ``mode`` is ``"append"`` (default) or ``"override"``.

        Files contain ``source<TAB>target`` lines, with actual tabs, not Jieba
        ``word freq [tag]`` entries. Files in each spec contribute mappings to its
        slot. Append merges with existing mappings; override replaces that slot
        with the combined file mappings. Duplicate source keys use the last value.
        All files are parsed before changes are applied.

        Mappings affect configurations using their slot and survive configuration
        changes. Jieba words must be registered separately when phrase boundaries
        require it; see ``load_user_dict_files()``.

        Raises:
            ValueError: If a slot or mode is invalid, a file cannot be read or parsed,
                or the backend rejects its mappings.
        """
        ...

    def add_word(
            self,
            word: str,
            freq: Optional[int] = None,
            tag: Optional[str] = None,
    ) -> None:
        """
        Add or update a single word in this instance's Jieba dictionary.

        The word becomes available immediately for subsequent Jieba
        segmentation and part-of-speech tagging operations.

        Unlike ``load_user_dict_entries()``, which loads multiple structured
        entries, this method provides a convenient way to register individual
        words dynamically without creating a user-dictionary file.

        This affects the current instance's Jieba tokenizer only. It does
        not modify OpenCC conversion dictionary slots, conversion configs,
        or other OpenCC instances.

        Args:
            word (str):
                Word to add or update. Must not be empty or contain
                whitespace.

            freq (Optional[int]):
                Optional word frequency. If ``None``, Jieba determines
                the frequency automatically. Defaults to ``None``.

            tag (Optional[str]):
                Optional part-of-speech tag, such as ``"nz"`` for a
                proper noun. Must not contain whitespace or NUL
                characters. Defaults to ``None``.

        Returns:
            None:
                The word is added or updated in the Jieba dictionary.

        Raises:
            ValueError:
                If ``word`` is empty, contains whitespace, or ``tag``
                contains whitespace or NUL characters.

            OverflowError:
                If ``freq`` cannot be represented as a non-negative
                platform-sized integer.

        Example:
            >>> cc = OpenCC("s2t")
            >>> cc.add_word("帕兰蒂尔", freq=100000, tag="nz")
            >>> cc.jieba_cut("帕兰蒂尔", hmm=False)
            ['帕兰蒂尔']

        Notes:
            - Existing word entries may be updated.
            - The change takes effect without rebuilding the converter.
            - Jieba user words can influence phrase-based OpenCC conversion
              by changing how input text is segmented.
            - For loading multiple words, use ``load_user_dict_entries()``
              or ``load_user_dict_files()``.

        See Also:
            load_user_dict_entries:
                Load multiple structured Jieba dictionary entries.
            load_user_dict:
                Load a Jieba user-dictionary file.
            jieba_cut:
                Segment text using the current Jieba dictionary.
            jieba_tag:
                Segment and assign part-of-speech tags.
        """
        ...

    @staticmethod
    def available_slots() -> List[str]:
        """Return supported OpenCC conversion dictionary slot names.

        Use these names as ``slot`` in ``load_custom_dicts()`` or
        ``load_custom_dict_files()``. For example, ``"STCharacters"`` and
        ``"STPhrases"`` participate in Simplified-to-Traditional conversion.
        A custom mapping takes effect only when the active configuration uses
        its slot. These names are dictionary slots, not configuration names.
        """
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...
