from __future__ import print_function

import argparse
import sys
from pathlib import Path

from opencc_jieba_pyo3 import OpenCC, CustomDictFileSpec

CONFIG_HELP = "Configuration: " + "|".join(OpenCC.supported_configs())
SLOT_HELP = "Available slots: " + "|".join(OpenCC.available_slots())


def resolve_config(config):
    if config is None:
        print("ℹ️  Config not set. Use default: s2t", file=sys.stderr)
        return "s2t"

    try:
        return OpenCC.canonicalise_config(config)
    except ValueError:
        print(f"❌  Invalid OpenCC config: {config}", file=sys.stderr)
        print(
            f"   Supported configs: {' | '.join(OpenCC.supported_configs())}",
            file=sys.stderr,
        )
        return None


def resolve_slot(slot):
    slot_key = slot.strip().casefold()

    for available_slot in OpenCC.available_slots():
        if available_slot.casefold() == slot_key:
            return available_slot

    raise ValueError(
        f"Invalid custom dictionary slot: {slot}. "
        f"Expected one of: {' | '.join(OpenCC.available_slots())}"
    )


def parse_custom_dict_spec(spec: str) -> CustomDictFileSpec:
    """
    Parse one ``--custom-dict`` value using ``slot:mode:path`` syntax.

    Splitting is limited to two separators so Windows drive-letter paths such
    as ``R:\\dicts\\UserDict.txt`` remain intact.
    """
    parts = spec.split(":", 2)
    if len(parts) != 3:
        raise ValueError(
            "Invalid --custom-dict spec {!r}. Expected slot:mode:path".format(spec)
        )

    slot, mode, path = (part.strip() for part in parts)

    if not slot:
        raise ValueError(
            "Invalid --custom-dict spec {!r}: slot is empty".format(spec)
        )

    mode = mode.lower()
    if mode not in ("append", "override"):
        raise ValueError(
            "Invalid --custom-dict mode {!r}. Expected append or override".format(
                mode
            )
        )

    if not path:
        raise ValueError(
            "Invalid --custom-dict spec {!r}: path is empty".format(spec)
        )

    if not Path(path).is_file():
        raise ValueError("Custom dictionary file not found: {}".format(path))

    return {
        "slot": resolve_slot(slot),
        "mode": mode,
        "files": [path],
    }


def custom_dict_specs_from_args(args):
    return [
        parse_custom_dict_spec(spec)
        for spec in (getattr(args, "custom_dict", None) or [])
    ]


def user_dict_files_from_args(args):
    """
    Validate and return ``-U/--user-dict-file`` paths in command-line order.
    """
    paths = getattr(args, "user_dict_file", None) or []

    for path in paths:
        if not Path(path).is_file():
            raise ValueError("Jieba user dictionary file not found: {}".format(path))

    return paths


def build_opencc(config, args):
    """
    Construct one OpenCC instance and apply optional Jieba and OpenCC files.

    Jieba user dictionaries are loaded first so custom OpenCC phrase mappings
    see the intended segmentation.
    """
    custom_specs = custom_dict_specs_from_args(args)
    user_files = user_dict_files_from_args(args)

    opencc = OpenCC(config)

    if user_files:
        opencc.load_user_dict_files(user_files)

    if custom_specs:
        opencc.load_custom_dict_files(custom_specs)

    return opencc


def paths_refer_to_same_file(input_path: str, output_path: str) -> bool:
    import os

    return os.path.normcase(os.path.abspath(input_path)) == os.path.normcase(
        os.path.abspath(output_path)
    )


def subcommand_convert(args):
    import io

    config = resolve_config(args.config)
    if config is None:
        return 1
    args.config = config

    if args.input and not Path(args.input).is_file():
        print(f"❌ Input file not found: {args.input}", file=sys.stderr)
        return 1

    if args.input and args.output and paths_refer_to_same_file(args.input, args.output):
        print("❌ Input and output files must be different.", file=sys.stderr)
        return 1

    try:
        opencc = build_opencc(config, args)
    except (OSError, RuntimeError, ValueError) as ex:
        print(f"❌ Failed to initialize OpenCC: {ex}", file=sys.stderr)
        return 1

    if args.input is None and sys.stdin.isatty():
        print(
            "Input text to convert, <Ctrl+Z> (Windows) or <Ctrl+D> (Unix) then Enter to submit:",
            file=sys.stderr,
        )

    try:
        with io.open(args.input if args.input else 0, encoding=args.in_enc) as f:
            input_str = f.read()
    except LookupError as ex:
        print(f"❌ Invalid input encoding '{args.in_enc}': {ex}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as ex:
        source = args.input or "<stdin>"
        print(f"❌ Failed to read input '{source}': {ex}", file=sys.stderr)
        return 1

    output_str = opencc.convert(input_str, args.punct)

    try:
        with io.open(args.output if args.output else 1, "w", encoding=args.out_enc) as f:
            f.write(output_str)
    except LookupError as ex:
        print(f"❌ Invalid output encoding '{args.out_enc}': {ex}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as ex:
        target = args.output or "<stdout>"
        print(f"❌ Failed to write output '{target}': {ex}", file=sys.stderr)
        return 1

    in_from = args.input if args.input else "<stdin>"
    out_to = args.output if args.output else "<stdout>"

    if sys.stderr.isatty():
        if output_str and not output_str.endswith("\n"):
            print()
        print(
            f"Conversion completed ({config}): {in_from} -> {out_to}",
            file=sys.stderr,
        )

    return 0


def subcommand_segment(args):
    import io

    try:
        # Segmentation does not need an OpenCC conversion config, but using the
        # normal default constructor gives us the same native Jieba instance.
        opencc = build_opencc("s2t", args)
    except (OSError, RuntimeError, ValueError) as ex:
        print(f"❌ Failed to initialize OpenCC/Jieba: {ex}", file=sys.stderr)
        return 1

    if args.input is None and sys.stdin.isatty():
        print(
            "Input text to segment, <Ctrl+Z> (Windows) or <Ctrl+D> (Unix) then Enter to submit:",
            file=sys.stderr,
        )

    try:
        with io.open(args.input if args.input else 0, encoding=args.in_enc) as f:
            input_str = f.read()
    except LookupError as ex:
        print(f"❌ Invalid input encoding '{args.in_enc}': {ex}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as ex:
        source = args.input or "<stdin>"
        print(f"❌ Failed to read input '{source}': {ex}", file=sys.stderr)
        return 1

    mode = args.mode
    delim = args.delim if args.delim not in (None, "", "/") else " "
    separator = args.separator if args.separator not in (None, "") else "/"
    hmm = not args.no_hmm

    if mode == "cut":
        segments = opencc.jieba_cut(input_str, hmm)
        output_str = delim.join(segments)

    elif mode == "search":
        segments = opencc.jieba_cut_for_search(input_str, hmm)
        output_str = delim.join(segments)

    elif mode == "full":
        segments = opencc.jieba_cut_all(input_str)
        output_str = delim.join(segments)

    elif mode == "tag":
        tagged = opencc.jieba_tag(input_str, hmm)
        output_str = delim.join(
            f"{word}{separator}{tag}" for word, tag in tagged
        )

    else:
        print(f"❌ Invalid segmentation mode: {mode}", file=sys.stderr)
        return 1

    try:
        with io.open(args.output if args.output else 1, "w", encoding=args.out_enc) as f:
            f.write(output_str)
    except LookupError as ex:
        print(f"❌ Invalid output encoding '{args.out_enc}': {ex}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as ex:
        target = args.output or "<stdout>"
        print(f"❌ Failed to write output '{target}': {ex}", file=sys.stderr)
        return 1

    in_from = args.input if args.input else "<stdin>"
    out_to = args.output if args.output else "<stdout>"

    if sys.stderr.isatty():
        if output_str and not output_str.endswith("\n"):
            print()
        print(
            f"Segmentation completed ({mode}, HMM:{hmm if mode != 'full' else 'None'}): "
            f"{in_from} -> {out_to}",
            file=sys.stderr,
        )

    return 0


def subcommand_office(args):
    import os
    from .office_helper import OFFICE_FORMATS, convert_office_doc

    input_file = args.input
    output_file = args.output
    office_format = args.format
    auto_ext = getattr(args, "auto_ext", False)
    punct = args.punct
    keep_font = getattr(args, "keep_font", False)

    config = resolve_config(args.config)
    if config is None:
        return 1
    args.config = config

    if not input_file and not output_file:
        print("❌ Input and output files are missing.", file=sys.stderr)
        return 1

    if not input_file:
        print("❌ Input file is missing.", file=sys.stderr)
        return 1

    if not Path(input_file).is_file():
        print(f"❌ Input file not found: {input_file}", file=sys.stderr)
        return 1

    if not output_file:
        input_path = Path(input_file)

        input_name = input_path.stem
        input_ext = input_path.suffix
        input_dir = input_path.parent if input_path.parent != Path("") else Path.cwd()

        if auto_ext and office_format in OFFICE_FORMATS:
            ext = f".{office_format}"
        else:
            ext = input_ext

        output_path = input_dir / f"{input_name}_converted{ext}"
        output_file = str(output_path)

        print(f"ℹ️  Output file not specified. Using: {output_path}", file=sys.stderr)

    if not office_format:
        file_ext = os.path.splitext(input_file)[1].lower()
        if file_ext[1:] not in OFFICE_FORMATS:
            print(f"❌ Invalid Office file extension: {file_ext}", file=sys.stderr)
            print(
                "   Valid extensions: .docx | .xlsx | .pptx | .odt | .ods | .odp | .epub",
                file=sys.stderr,
            )
            return 1
        office_format = str(file_ext[1:])

    if auto_ext and output_file and not os.path.splitext(output_file)[1] and office_format in OFFICE_FORMATS:
        output_file += f".{office_format}"
        print(f"ℹ️  Auto-extension applied: {output_file}", file=sys.stderr)

    if paths_refer_to_same_file(input_file, output_file):
        print("❌ Input and output files must be different.", file=sys.stderr)
        return 1

    try:
        opencc = build_opencc(config, args)
    except (OSError, RuntimeError, ValueError) as ex:
        print(f"❌ Failed to initialize OpenCC: {ex}", file=sys.stderr)
        return 1

    try:
        success, message = convert_office_doc(
            input_file,
            output_file,
            office_format,
            opencc,
            punct,
            keep_font,
        )

        if success:
            print(
                f"{message} ({config})\n📁  Output saved to: {os.path.abspath(output_file)}",
                file=sys.stderr,
            )
            return 0

        print(f"❌ Office document conversion failed: {message}", file=sys.stderr)
        return 1

    except Exception as ex:
        print(f"❌ Error during Office document conversion: {str(ex)}", file=sys.stderr)
        return 1


def add_dictionary_options(parser):
    parser.add_argument(
        "-D",
        "--custom-dict",
        action="append",
        metavar="<slot:mode:path>",
        help=(
                "Load custom OpenCC dictionary file. "
                "Format: slot:mode:path, e.g. STPhrases:append:custom.txt. "
                "Can be used multiple times. " + SLOT_HELP
        ),
    )
    parser.add_argument(
        "-U",
        "--user-dict-file",
        action="append",
        metavar="<file>",
        help=(
            "Load Jieba user dictionary file using 'word freq [tag]' format. "
            "Can be used multiple times."
        ),
    )


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="opencc_jieba_pyo3 – OpenCC + Jieba CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -----------------
    # convert subcommand
    # -----------------
    parser_convert = subparsers.add_parser(
        "convert",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Convert Chinese text using OpenCC + Jieba",
    )
    parser_convert.add_argument(
        "-i",
        "--input",
        metavar="<file>",
        help="Read original text from <file>.",
    )
    parser_convert.add_argument(
        "-o",
        "--output",
        metavar="<file>",
        help="Write converted text to <file>.",
    )
    parser_convert.add_argument(
        "-c",
        "--config",
        metavar="<conversion>",
        help=CONFIG_HELP,
    )
    parser_convert.add_argument(
        "-p",
        "--punct",
        action="store_true",
        default=False,
        help="Enable punctuation conversion.",
    )
    parser_convert.add_argument(
        "--in-enc",
        metavar="<encoding>",
        default="UTF-8",
        help="Encoding for input.",
    )
    parser_convert.add_argument(
        "--out-enc",
        metavar="<encoding>",
        default="UTF-8",
        help="Encoding for output.",
    )
    add_dictionary_options(parser_convert)
    parser_convert.set_defaults(func=subcommand_convert)

    # -----------------
    # segment subcommand
    # -----------------
    parser_segment = subparsers.add_parser(
        "segment",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Segment Chinese text using Jieba",
    )
    parser_segment.add_argument(
        "-i",
        "--input",
        metavar="<file>",
        help="Read input text from <file>.",
    )
    parser_segment.add_argument(
        "-o",
        "--output",
        metavar="<file>",
        help="Write segmented text to <file>.",
    )
    parser_segment.add_argument(
        "-d",
        "--delim",
        metavar="<char>",
        default=" ",
        help="Delimiter to join segments.",
    )
    parser_segment.add_argument(
        "-s",
        "--separator",
        metavar="<char>",
        default="/",
        help="Separator for segment mode: tag.",
    )
    parser_segment.add_argument(
        "--no-hmm",
        action="store_true",
        default=False,
        help="Disable HMM.",
    )
    parser_segment.add_argument(
        "-m",
        "--mode",
        choices=["cut", "search", "full", "tag"],
        default="cut",
        help="Segmentation mode.",
    )
    parser_segment.add_argument(
        "--in-enc",
        metavar="<encoding>",
        default="UTF-8",
        help="Encoding for input.",
    )
    parser_segment.add_argument(
        "--out-enc",
        metavar="<encoding>",
        default="UTF-8",
        help="Encoding for output.",
    )
    add_dictionary_options(parser_segment)
    parser_segment.set_defaults(func=subcommand_segment)

    # -----------------
    # office subcommand
    # -----------------
    parser_office = subparsers.add_parser(
        "office",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Convert Office document Chinese text using OpenCC + Jieba",
    )
    parser_office.add_argument(
        "-i",
        "--input",
        metavar="<file>",
        help="Input Office document from <file>.",
    )
    parser_office.add_argument(
        "-o",
        "--output",
        metavar="<file>",
        help="Output Office document to <file>.",
    )
    parser_office.add_argument(
        "-c",
        "--config",
        metavar="<conversion>",
        help=CONFIG_HELP,
    )
    parser_office.add_argument(
        "-p",
        "--punct",
        action="store_true",
        default=False,
        help="Enable punctuation conversion.",
    )
    parser_office.add_argument(
        "-f",
        "--format",
        metavar="<format>",
        help="Target Office format (e.g. docx, xlsx, pptx, odt, ods, odp, epub).",
    )
    parser_office.add_argument(
        "--auto-ext",
        action="store_true",
        default=False,
        help="Auto-append extension to output file.",
    )
    parser_office.add_argument(
        "--keep-font",
        action="store_true",
        default=False,
        help="Preserve font-family information in Office content.",
    )
    add_dictionary_options(parser_office)
    parser_office.set_defaults(func=subcommand_office)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
