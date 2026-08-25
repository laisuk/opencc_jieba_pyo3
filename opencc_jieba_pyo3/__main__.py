from __future__ import print_function

import argparse
import codecs
import io
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from opencc_jieba_pyo3 import CustomDictFileSpec, OpenCC

SUPPORTED_CONFIGS = OpenCC.supported_configs()
AVAILABLE_SLOTS = OpenCC.available_slots()
CONFIG_HELP = "Configuration: " + "|".join(SUPPORTED_CONFIGS)
SLOT_HELP = "Available slots: " + "|".join(AVAILABLE_SLOTS)


def resolve_config(config: Optional[str]) -> Optional[str]:
    if config is None:
        print("ℹ️  Config not set. Use default: s2t", file=sys.stderr)
        return "s2t"

    try:
        return OpenCC.canonicalise_config(config)
    except ValueError:
        print(f"❌ Invalid OpenCC config: {config}", file=sys.stderr)
        print(
            f"   Supported configs: {' | '.join(SUPPORTED_CONFIGS)}",
            file=sys.stderr,
        )
        return None


def resolve_slot(slot: str) -> str:
    slot_key = slot.strip().casefold()

    for available_slot in AVAILABLE_SLOTS:
        if available_slot.casefold() == slot_key:
            return available_slot

    raise ValueError(
        f"Invalid custom dictionary slot: {slot}. "
        f"Expected one of: {' | '.join(AVAILABLE_SLOTS)}"
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


def custom_dict_specs_from_args(args: argparse.Namespace) -> List[CustomDictFileSpec]:
    return [
        parse_custom_dict_spec(spec)
        for spec in (getattr(args, "custom_dict", None) or [])
    ]


def user_dict_files_from_args(args: argparse.Namespace) -> List[str]:
    """Validate and return ``-U/--user-dict-file`` paths in CLI order."""
    paths = getattr(args, "user_dict_file", None) or []

    for path in paths:
        if not Path(path).is_file():
            raise ValueError("Jieba user dictionary file not found: {}".format(path))

    return paths


def build_opencc(
        config: str,
        args: argparse.Namespace,
) -> Tuple[OpenCC, List[CustomDictFileSpec]]:
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

    return opencc, custom_specs


def build_jieba(args: argparse.Namespace) -> OpenCC:
    """Construct the Jieba instance and load only ``-U`` user dictionaries."""
    user_files = user_dict_files_from_args(args)
    opencc = OpenCC("s2t")

    if user_files:
        opencc.load_user_dict_files(user_files)

    return opencc


def paths_refer_to_same_file(input_path: str, output_path: str) -> bool:
    return os.path.normcase(os.path.abspath(input_path)) == os.path.normcase(
        os.path.abspath(output_path)
    )


def validate_input_output_paths(
        input_path: Optional[str],
        output_path: Optional[str],
) -> bool:
    if input_path and not Path(input_path).is_file():
        print(f"❌ Input file not found: {input_path}", file=sys.stderr)
        return False

    if input_path and output_path and paths_refer_to_same_file(input_path, output_path):
        print("❌ Input and output files must be different.", file=sys.stderr)
        return False

    return True


def read_text_input(input_path: Optional[str], encoding: str) -> Optional[str]:
    try:
        with io.open(input_path if input_path else 0, encoding=encoding) as stream:
            return stream.read()
    except LookupError as ex:
        print(f"❌ Invalid input encoding '{encoding}': {ex}", file=sys.stderr)
    except (OSError, UnicodeError) as ex:
        source = input_path or "<stdin>"
        print(f"❌ Failed to read input '{source}': {ex}", file=sys.stderr)

    return None


def write_text_output(
        output_str: str,
        output_path: Optional[str],
        encoding: str,
) -> bool:
    # Validate even for interactive consoles, which write Unicode directly.
    try:
        codecs.lookup(encoding)
    except LookupError as ex:
        print(f"❌ Invalid output encoding '{encoding}': {ex}", file=sys.stderr)
        return False

    try:
        if output_path:
            with io.open(output_path, "w", encoding=encoding) as stream:
                stream.write(output_str)
        elif sys.stdout.isatty():
            sys.stdout.write(output_str)
            sys.stdout.flush()
        else:
            sys.stdout.buffer.write(output_str.encode(encoding))
            sys.stdout.buffer.flush()
    except (OSError, UnicodeError) as ex:
        target = output_path or "<stdout>"
        print(f"❌ Failed to write output '{target}': {ex}", file=sys.stderr)
        return False

    return True


def normalize_input(opencc: OpenCC, input_str: str, args: argparse.Namespace) -> str:
    if getattr(args, "norm_compat_extended", False):
        return opencc.normalize_compat_extended(input_str)
    if getattr(args, "norm_compat", False):
        return opencc.normalize_compat(input_str)
    return input_str


def normalization_status(args: argparse.Namespace) -> str:
    if getattr(args, "norm_compat_extended", False):
        return ", norm-compat:extended"
    if getattr(args, "norm_compat", False):
        return ", norm-compat"
    return ""


def custom_dict_status(specs: List[CustomDictFileSpec]) -> str:
    if not specs:
        return ""

    details = ",".join(
        f"{spec['slot']}:{spec.get('mode', 'append')}" for spec in specs
    )
    return f", custom:{details}"


def finish_text_status(
        output_str: str,
        output_path: Optional[str],
        status: str,
) -> None:
    if not sys.stderr.isatty():
        return

    # Add only a display newline after direct interactive stdout output.
    if not output_path and sys.stdout.isatty() and output_str and not output_str.endswith("\n"):
        sys.stdout.write("\n")
        sys.stdout.flush()

    print(status, file=sys.stderr)


def subcommand_convert(args: argparse.Namespace) -> int:
    config = resolve_config(args.config)
    if config is None:
        return 1
    args.config = config

    if not validate_input_output_paths(args.input, args.output):
        return 1

    try:
        opencc, specs = build_opencc(config, args)
    except (OSError, RuntimeError, ValueError) as ex:
        print(f"❌ Failed to initialize OpenCC: {ex}", file=sys.stderr)
        return 1

    if args.input is None and sys.stdin.isatty():
        print(
            "Input text to convert, <Ctrl+Z> (Windows) or <Ctrl+D> (Unix) "
            "then Enter to submit:",
            file=sys.stderr,
        )

    input_str = read_text_input(args.input, args.in_enc)
    if input_str is None:
        return 1

    try:
        input_str = normalize_input(opencc, input_str, args)
        output_str = opencc.convert(input_str, args.punct)
    except ValueError as ex:
        print(f"❌ Conversion failed: {ex}", file=sys.stderr)
        return 1

    if not write_text_output(output_str, args.output, args.out_enc):
        return 1

    in_from = args.input or "<stdin>"
    out_to = args.output or "<stdout>"
    status = (
        f"Conversion completed ({config}"
        f"{normalization_status(args)}"
        f"{custom_dict_status(specs)}"
        f"): {in_from} -> {out_to}"
    )
    finish_text_status(output_str, args.output, status)
    return 0


def subcommand_segment(args: argparse.Namespace) -> int:
    if not validate_input_output_paths(args.input, args.output):
        return 1

    try:
        # Segmentation uses only Jieba user dictionaries (-U).
        # OpenCC custom dictionaries (-D) are intentionally not loaded here.
        opencc = build_jieba(args)
    except (OSError, RuntimeError, ValueError) as ex:
        print(f"❌ Failed to initialize OpenCC/Jieba: {ex}", file=sys.stderr)
        return 1

    if args.input is None and sys.stdin.isatty():
        print(
            "Input text to segment, <Ctrl+Z> (Windows) or <Ctrl+D> (Unix) "
            "then Enter to submit:",
            file=sys.stderr,
        )

    input_str = read_text_input(args.input, args.in_enc)
    if input_str is None:
        return 1

    try:
        input_str = normalize_input(opencc, input_str, args)

        mode = args.mode
        delim = args.delim if args.delim not in (None, "", "/") else " "
        separator = args.separator if args.separator not in (None, "") else "/"
        hmm = not args.no_hmm

        if mode == "cut":
            output_str = delim.join(opencc.jieba_cut(input_str, hmm))
        elif mode == "search":
            output_str = delim.join(opencc.jieba_cut_for_search(input_str, hmm))
        elif mode == "full":
            output_str = delim.join(opencc.jieba_cut_all(input_str))
        elif mode == "tag":
            tagged = opencc.jieba_tag(input_str, hmm)
            output_str = delim.join(
                f"{word}{separator}{tag}" for word, tag in tagged
            )
        else:
            print(f"❌ Invalid segmentation mode: {mode}", file=sys.stderr)
            return 1
    except ValueError as ex:
        print(f"❌ Segmentation failed: {ex}", file=sys.stderr)
        return 1

    if not write_text_output(output_str, args.output, args.out_enc):
        return 1

    in_from = args.input or "<stdin>"
    out_to = args.output or "<stdout>"
    hmm_status = "" if mode == "full" else f", HMM:{hmm}"
    status = (
        f"Segmentation completed ({mode}"
        f"{hmm_status}"
        f"{normalization_status(args)}"
        f"): {in_from} -> {out_to}"
    )
    finish_text_status(output_str, args.output, status)
    return 0


def subcommand_office(args: argparse.Namespace) -> int:
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

    if not office_format:
        file_ext = os.path.splitext(input_file)[1].lower()
        if file_ext[1:] not in OFFICE_FORMATS:
            print(f"❌ Invalid Office file extension: {file_ext}", file=sys.stderr)
            print(
                "   Valid extensions: .docx | .xlsx | .pptx | .odt | .ods | .odp | .epub",
                file=sys.stderr,
            )
            return 1
        office_format = file_ext[1:]
    else:
        office_format = office_format.lower()
        if office_format not in OFFICE_FORMATS:
            print(f"❌ Invalid Office format: {office_format}", file=sys.stderr)
            print(
                "   Valid formats: docx | xlsx | pptx | odt | ods | odp | epub",
                file=sys.stderr,
            )
            return 1

    if not output_file:
        input_path = Path(input_file)
        ext = f".{office_format}" if auto_ext else input_path.suffix
        output_path = input_path.with_name(f"{input_path.stem}_converted{ext}")
        output_file = str(output_path)
        print(f"ℹ️  Output file not specified. Using: {output_path}", file=sys.stderr)
    elif auto_ext and not os.path.splitext(output_file)[1]:
        output_file += f".{office_format}"
        print(f"ℹ️  Auto-extension applied: {output_file}", file=sys.stderr)

    if paths_refer_to_same_file(input_file, output_file):
        print("❌ Input and output files must be different.", file=sys.stderr)
        return 1

    try:
        opencc, _ = build_opencc(config, args)
    except (OSError, RuntimeError, ValueError) as ex:
        print(f"❌ Failed to initialize OpenCC: {ex}", file=sys.stderr)
        return 1

    try:
        success, message = convert_office_doc(
            input_file,
            output_file,
            str(office_format),
            opencc,
            punct,
            keep_font,
        )
    except Exception as ex:
        print(f"❌ Error during Office document conversion: {ex}", file=sys.stderr)
        return 1

    if not success:
        print(f"❌ Office document conversion failed: {message}", file=sys.stderr)
        return 1

    print(
        f"{message} ({config})\n📁  Output saved to: {os.path.abspath(output_file)}",
        file=sys.stderr,
    )
    return 0


def add_custom_dict_option(parser: argparse.ArgumentParser) -> None:
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


def add_user_dict_option(parser: argparse.ArgumentParser) -> None:
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


def add_conversion_dictionary_options(parser: argparse.ArgumentParser) -> None:
    add_custom_dict_option(parser)
    add_user_dict_option(parser)


def add_normalization_options(parser: argparse.ArgumentParser, action: str) -> None:
    parser.add_argument(
        "-n",
        "--norm-compat",
        action="store_true",
        help=f"Normalize CJK Compatibility Ideographs before {action}.",
    )
    parser.add_argument(
        "-E",
        "--norm-compat-extended",
        action="store_true",
        help=f"Normalize extended Unicode compatibility forms before {action}.",
    )


def add_text_io_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-i", "--input", metavar="<file>", help="Read input text from <file>."
    )
    parser.add_argument(
        "-o", "--output", metavar="<file>", help="Write output text to <file>."
    )
    parser.add_argument(
        "--in-enc",
        metavar="<encoding>",
        default="UTF-8",
        help="Encoding for input.",
    )
    parser.add_argument(
        "--out-enc",
        metavar="<encoding>",
        default="UTF-8",
        help="Encoding for output.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="opencc_jieba_pyo3 – OpenCC + Jieba CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_convert = subparsers.add_parser(
        "convert",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Convert Chinese text using OpenCC + Jieba",
    )
    add_text_io_options(parser_convert)
    parser_convert.add_argument(
        "-c", "--config", metavar="<conversion>", help=CONFIG_HELP
    )
    parser_convert.add_argument(
        "-p",
        "--punct",
        action="store_true",
        help="Enable punctuation conversion.",
    )
    add_normalization_options(parser_convert, "conversion")
    add_conversion_dictionary_options(parser_convert)
    parser_convert.set_defaults(func=subcommand_convert)

    parser_segment = subparsers.add_parser(
        "segment",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Segment Chinese text using Jieba",
    )
    add_text_io_options(parser_segment)
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
        help="Separator for tag mode.",
    )
    parser_segment.add_argument(
        "--no-hmm",
        action="store_true",
        help="Disable HMM.",
    )
    parser_segment.add_argument(
        "-m",
        "--mode",
        choices=["cut", "search", "full", "tag"],
        default="cut",
        help="Segmentation mode.",
    )
    add_normalization_options(parser_segment, "segmentation")
    add_user_dict_option(parser_segment)
    # Backward compatibility: accept -D/--custom-dict for segment, but do not
    # expose or load it. OpenCC custom dictionaries do not affect Jieba-only
    # segmentation.
    parser_segment.add_argument(
        "-D",
        "--custom-dict",
        action="append",
        metavar="<slot:mode:path>",
        help=argparse.SUPPRESS,
    )
    parser_segment.set_defaults(func=subcommand_segment)

    parser_office = subparsers.add_parser(
        "office",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Convert Office document Chinese text using OpenCC + Jieba",
    )
    parser_office.add_argument(
        "-i", "--input", metavar="<file>", help="Input Office document from <file>."
    )
    parser_office.add_argument(
        "-o", "--output", metavar="<file>", help="Output Office document to <file>."
    )
    parser_office.add_argument(
        "-c", "--config", metavar="<conversion>", help=CONFIG_HELP
    )
    parser_office.add_argument(
        "-p",
        "--punct",
        action="store_true",
        help="Enable punctuation conversion.",
    )
    parser_office.add_argument(
        "-f",
        "--format",
        metavar="<format>",
        help="Target Office format (docx, xlsx, pptx, odt, ods, odp, epub).",
    )
    parser_office.add_argument(
        "--auto-ext",
        action="store_true",
        help="Auto-append extension to output file.",
    )
    parser_office.add_argument(
        "--keep-font",
        action="store_true",
        help="Preserve font-family information in Office content.",
    )
    add_conversion_dictionary_options(parser_office)
    parser_office.set_defaults(func=subcommand_office)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
