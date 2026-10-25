"""Regression checks for CLI I/O, formatting, and conversion options."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from opencc_jieba_pyo3 import OpenCC
from opencc_jieba_pyo3 import __main__ as cli


class TestCLI(unittest.TestCase):
    def run_cli(self, argv, text=""):
        output = io.StringIO()
        errors = io.StringIO()
        with patch.object(sys, "stdin", io.StringIO(text)):
            with redirect_stdout(output), redirect_stderr(errors):
                status = cli.main(argv)
        return status, output.getvalue(), errors.getvalue()

    def test_embedded_conversion_with_text_streams(self):
        status, output, errors = self.run_cli(["convert", "-c", "S2T"], "汉语")
        self.assertEqual((status, output, errors), (0, "漢語", ""))

    def test_segmentation_modes_and_empty_separators(self):
        text = "我来到北京清华大学"
        cc = OpenCC()
        for mode in ("cut", "search", "full", "tag"):
            for delimiter, separator in ((" ", "/"), ("", ""), (" | ", ":")):
                with self.subTest(mode=mode, delimiter=delimiter, separator=separator):
                    status, output, errors = self.run_cli(
                        ["segment", "-m", mode, "-d", delimiter,
                         "-s", separator, "--no-hmm"], text
                    )
                    expected = cc.jieba_segment_join(
                        text, mode=mode, delim=delimiter, separator=separator, hmm=False
                    )
                    self.assertEqual((status, output, errors), (0, expected, ""))

    def test_invalid_config_does_not_read_stdin(self):
        with patch.object(cli, "read_text_input") as read:
            status, output, errors = self.run_cli(["convert", "-c", "invalid"])
        self.assertEqual((status, output), (1, ""))
        self.assertIn("Invalid OpenCC config", errors)
        read.assert_not_called()

    def test_detofu_file_requires_level(self):
        with patch.object(cli, "build_opencc") as build:
            status, output, errors = self.run_cli(
                ["convert", "-c", "s2t", "--detofu-file", "missing.txt"]
            )
        self.assertEqual((status, output), (1, ""))
        self.assertIn("--detofu-file requires --detofu", errors)
        build.assert_not_called()

    def test_segment_ignores_legacy_conversion_dictionary_option(self):
        status, output, errors = self.run_cli(
            ["segment", "-D", "not-a-dictionary-spec"], "我来到北京"
        )
        self.assertEqual((status, output, errors), (0, "我 来到 北京", ""))

    def test_file_encodings(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.txt"
            target = Path(directory) / "output.txt"
            source.write_bytes("汉语".encode("utf-16"))
            status, output, errors = self.run_cli(
                ["convert", "-c", "s2t", "-i", str(source), "-o", str(target),
                 "--in-enc", "utf-16", "--out-enc", "utf-16"]
            )
            self.assertEqual((status, output, errors), (0, "", ""))
            self.assertEqual(target.read_bytes().decode("utf-16"), "漢語")

    def test_invalid_output_codec_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "output.txt"
            target.write_text("keep", encoding="utf-8")
            status, output, errors = self.run_cli(
                ["convert", "-c", "s2t", "-o", str(target),
                 "--out-enc", "not-an-encoding"], "汉语"
            )
            self.assertEqual((status, output), (1, ""))
            self.assertIn("Invalid output encoding", errors)
            self.assertEqual(target.read_text(encoding="utf-8"), "keep")

    def test_output_alias_cannot_overwrite_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.txt"
            alias = Path(directory) / "alias.txt"
            source.write_text("汉语", encoding="utf-8")
            try:
                os.link(source, alias)
            except OSError as error:
                self.skipTest(f"Hard links unavailable: {error}")
            for output in (source, alias):
                with self.subTest(output=output):
                    status, _, errors = self.run_cli(
                        ["convert", "-c", "s2t", "-i", str(source), "-o", str(output)]
                    )
                    self.assertEqual(status, 1)
                    self.assertIn("must be different", errors)
                    self.assertEqual(source.read_text(encoding="utf-8"), "汉语")
            self.assertFalse(cli.paths_refer_to_same_file(str(source), str(source) + ".new"))

    def test_pipeline_normalization_precedence_and_fallbacks(self):
        cc = OpenCC("t2s")
        text = "金驂𬴂"
        with tempfile.TemporaryDirectory() as directory:
            custom = Path(directory) / "tofu.txt"
            custom.write_text("𬴂\t非\tExtC\n", encoding="utf-8")
            for normalization in ([], ["-n"], ["-n", "-E"]):
                for fallback in ([], ["--detofu"], ["--detofu", "--detofu-file", str(custom)]):
                    with self.subTest(normalization=normalization, fallback=fallback):
                        args = cli.build_parser().parse_args(
                            ["convert", "-c", "t2s", "-p"] + normalization + fallback
                        )
                        expected = cli.normalize_input(cc, text, args)
                        expected = cc.convert(expected, True)
                        if args.detofu_file:
                            expected = cc.detofu_with_custom_file(expected, args.detofu, args.detofu_file)
                        elif args.detofu:
                            expected = cc.detofu(expected, args.detofu)
                        self.assertEqual(cli.make_text_converter(cc, args)(text), expected)

    def test_subprocess_preserves_encoded_stdout(self):
        result = subprocess.run(
            [sys.executable, "-m", "opencc_jieba_pyo3", "convert", "-c", "s2t",
             "--in-enc", "utf-16", "--out-enc", "utf-16"],
            input="汉语".encode("utf-16"), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=str(Path(__file__).resolve().parents[1]),
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.decode("utf-16"), "漢語")
        self.assertEqual(result.stderr, b"")

    def test_office_conversion_uses_shared_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.docx"
            target = Path(directory) / "output.docx"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr(
                    "word/document.xml",
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    '<w:body><w:p><w:r><w:t>金汉语</w:t></w:r></w:p></w:body></w:document>',
                )
            status, _, errors = self.run_cli(
                ["office", "-c", "s2t", "-n", "-i", str(source), "-o", str(target)]
            )
            self.assertEqual(status, 0, errors)
            with zipfile.ZipFile(target) as archive:
                self.assertIn("金漢語", archive.read("word/document.xml").decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
