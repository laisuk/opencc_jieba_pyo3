from __future__ import print_function

import argparse
import sys
import io
from opencc_jieba_pyo3 import OpenCC


def subcommand_convert(args):
    if args.config is None:
        print("Please set conversion configuration.", file=sys.stderr)
        return 1

    opencc = OpenCC(args.config)

    # Prompt only if reading from stdin and it's interactive (i.e., not piped or redirected)
    if args.input is None and sys.stdin.isatty():
        print("Input text to convert, <Ctrl+Z> (Windows) or <Ctrl+D> (Unix) then Enter to submit:", file=sys.stderr)

    with io.open(args.input if args.input else 0, encoding=args.in_enc) as f:
        input_str = f.read()

    output_str = opencc.convert(input_str, args.punct)

    with io.open(args.output if args.output else 1, 'w', encoding=args.out_enc) as f:
        f.write(output_str)

    in_from = args.input if args.input else "<stdin>"
    out_to = args.output if args.output else "<stdout>"
    if sys.stderr.isatty():
        print(f"Conversion completed ({args.config}): {in_from} -> {out_to}", file=sys.stderr)
    return 0


def subcommand_segment(args):
    opencc = OpenCC()  # Default config if not needed for segmentation

    # Prompt only if reading from stdin, and it's interactive (i.e., not piped or redirected)
    if args.input is None and sys.stdin.isatty():
        print("Input text to segment, <Ctrl+Z> (Windows) or <Ctrl+D> (Unix) then Enter to submit:", file=sys.stderr)

    with io.open(args.input if args.input else 0, encoding=args.in_enc) as f:
        input_str = f.read()

    segments = opencc.jieba_cut(input_str)
    delim = args.delim if args.delim is not None else " "
    output_str = delim.join(segments)

    with io.open(args.output if args.output else 1, 'w', encoding=args.out_enc) as f:
        f.write(output_str)

    in_from = args.input if args.input else "<stdin>"
    out_to = args.output if args.output else "<stdout>"
    if sys.stderr.isatty():
        print(f"Segmentation completed: {in_from} -> {out_to}", file=sys.stderr)
    return 0


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="opencc_jieba_pyo3 an OpenCC + Jieba CLI"
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Convert subcommand
    parser_convert = subparsers.add_parser('convert', help='Convert text using OpenCC')
    parser_convert.add_argument('-i', '--input', metavar='<file>',
                                help='Read original text from <file>.')
    parser_convert.add_argument('-o', '--output', metavar='<file>',
                                help='Write converted text to <file>.')
    parser_convert.add_argument('-c', '--config', metavar='<conversion>',
                                help='Conversion configuration: [s2t|s2tw|s2twp|s2hk|t2s|tw2s|tw2sp|hk2s|jp2t|t2jp]')
    parser_convert.add_argument('-p', '--punct', action='store_true', default=False,
                                help='Punctuation conversion')
    parser_convert.add_argument('--in-enc', metavar='<encoding>', default='UTF-8',
                                help='Encoding for input')
    parser_convert.add_argument('--out-enc', metavar='<encoding>', default='UTF-8',
                                help='Encoding for output')
    parser_convert.set_defaults(func=subcommand_convert)

    # Segment subcommand
    parser_segment = subparsers.add_parser('segment', help='Segment text using Jieba')
    parser_segment.add_argument('-i', '--input', metavar='<file>',
                                help='Read input text from <file>.')
    parser_segment.add_argument('-o', '--output', metavar='<file>',
                                help='Write segmented text to <file>.')
    parser_segment.add_argument('-d', '--delim', metavar='<char>', default=' ',
                                help='Delimiter to join segments')
    parser_segment.add_argument('--in-enc', metavar='<encoding>', default='UTF-8',
                                help='Encoding for input')
    parser_segment.add_argument('--out-enc', metavar='<encoding>', default='UTF-8',
                                help='Encoding for output')
    parser_segment.set_defaults(func=subcommand_segment)

    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
