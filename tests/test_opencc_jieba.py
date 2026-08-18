import unittest
from typing import List

from opencc_jieba_pyo3 import OpenCC, CustomDictSpec, CustomDictFileSpec, UserDictEntry


class TestOpenCCJieba(unittest.TestCase):

    def test_valid_config(self):
        cc = OpenCC("t2s")
        self.assertEqual(cc.get_config(), "t2s")

    def test_invalid_config_fallback(self):
        cc = OpenCC("invalid")
        self.assertEqual(cc.get_config(), "s2t")

    def test_supported_configs(self):
        configs = OpenCC.supported_configs()

        self.assertIn("s2t", configs)
        self.assertIn("t2jp", configs)
        self.assertIn("t2hkp", configs)
        self.assertIn("hk2tp", configs)

        self.assertTrue(OpenCC.is_valid_config("t2s"))
        self.assertTrue(OpenCC.is_valid_config("T2HKP"))
        self.assertTrue(OpenCC.is_valid_config("HK2TP"))
        self.assertFalse(OpenCC.is_valid_config("abc"))

    def test_set_config(self):
        cc = OpenCC("t2s")

        cc.set_config("s2tw")
        self.assertEqual(cc.get_config(), "s2tw")

        cc.set_config("nonexistent")
        self.assertEqual(cc.get_config(), "s2t")

    def test_convert(self):
        cc = OpenCC("s2t")

        result = cc.convert("八千里路云和月")

        self.assertIsInstance(result, str)
        self.assertEqual(result, "八千里路雲和月")

    def test_convert_with_punctuation(self):
        cc = OpenCC("s2t")

        result = cc.convert("“春眠不觉晓，处处闻啼鸟。”", punctuation=True)

        self.assertEqual(result, "「春眠不覺曉，處處聞啼鳥。」")

    def test_zho_check(self):
        cc = OpenCC()

        self.assertEqual(cc.zho_check("八千里路云和月"), 2)
        self.assertEqual(cc.zho_check("八千里路雲和月"), 1)
        self.assertEqual(cc.zho_check("hello world"), 0)

    def test_jieba_cut(self):
        cc = OpenCC()

        result = cc.jieba_cut("我来到北京清华大学", hmm=True)

        self.assertEqual(result, ["我", "来到", "北京", "清华大学"])

    def test_jieba_cut_without_hmm(self):
        cc = OpenCC()

        result = cc.jieba_cut("我来到北京清华大学", hmm=False)

        self.assertEqual(result, ["我", "来到", "北京", "清华大学"])

    def test_jieba_cut_for_search(self):
        cc = OpenCC()

        result = cc.jieba_cut_for_search("我来到北京清华大学", hmm=True)

        self.assertEqual(
            result,
            ["我", "来到", "北京", "清华", "华大", "大学", "清华大学"],
        )

    def test_jieba_cut_all(self):
        cc = OpenCC()

        result = cc.jieba_cut_all("我来到北京清华大学")

        self.assertIsInstance(result, list)
        self.assertIn("清华大学", result)
        self.assertIn("北京", result)

    def test_jieba_tag(self):
        cc = OpenCC()

        result = cc.jieba_tag("我来到北京清华大学", hmm=True)

        self.assertEqual(
            result,
            [
                ("我", "r"),
                ("来到", "v"),
                ("北京", "ns"),
                ("清华大学", "nt"),
            ],
        )

    def test_jieba_segment_join_cut(self):
        cc = OpenCC()

        result = cc.jieba_segment_join(
            "我来到北京清华大学",
            mode="cut",
            delim="|",
        )

        self.assertEqual(result, "我|来到|北京|清华大学")

    def test_jieba_segment_join_search(self):
        cc = OpenCC()

        result = cc.jieba_segment_join(
            "我来到北京清华大学",
            mode="search",
            delim="/",
        )

        self.assertEqual(
            result,
            "我/来到/北京/清华/华大/大学/清华大学",
        )

    def test_jieba_segment_join_full(self):
        cc = OpenCC()

        result = cc.jieba_segment_join(
            "我来到北京清华大学",
            mode="full",
            delim="|",
        )

        self.assertIsInstance(result, str)
        self.assertIn("清华大学", result)
        self.assertIn("北京", result)

    def test_jieba_segment_join_tag(self):
        cc = OpenCC()

        result = cc.jieba_segment_join(
            "我来到北京清华大学",
            mode="tag",
            delim=" | ",
            separator=":",
        )

        self.assertEqual(
            result,
            "我:r | 来到:v | 北京:ns | 清华大学:nt",
        )

    def test_jieba_segment_join_invalid_mode(self):
        cc = OpenCC()

        with self.assertRaises(ValueError):
            cc.jieba_segment_join(
                "我来到北京清华大学",
                mode="invalid",
            )

    def test_jieba_keyword_extract_textrank(self):
        cc = OpenCC()

        result = cc.jieba_keyword_extract_textrank(
            "自然语言处理是人工智能的重要领域，自然语言处理可以帮助计算机理解文本。",
            top_k=5,
        )

        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)
        self.assertTrue(all(isinstance(item, str) for item in result))

    def test_jieba_keyword_extract_tfidf(self):
        cc = OpenCC()

        result = cc.jieba_keyword_extract_tfidf(
            "自然语言处理是人工智能的重要领域，自然语言处理可以帮助计算机理解文本。",
            top_k=5,
        )

        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)
        self.assertTrue(all(isinstance(item, str) for item in result))

    def test_jieba_keyword_weight_textrank(self):
        cc = OpenCC()

        result = cc.jieba_keyword_weight_textrank(
            "自然语言处理是人工智能的重要领域，自然语言处理可以帮助计算机理解文本。",
            top_k=5,
        )

        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)

        for keyword, weight in result:
            self.assertIsInstance(keyword, str)
            self.assertIsInstance(weight, float)

    def test_jieba_keyword_weight_tfidf(self):
        cc = OpenCC()

        result = cc.jieba_keyword_weight_tfidf(
            "自然语言处理是人工智能的重要领域，自然语言处理可以帮助计算机理解文本。",
            top_k=5,
        )

        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)

        for keyword, weight in result:
            self.assertIsInstance(keyword, str)
            self.assertIsInstance(weight, float)

    # ------------------------------------------------------------------
    # Custom OpenCC dictionary + Jieba user-dictionary tests go below.
    # ------------------------------------------------------------------

    def test_from_dicts_custom_st_characters(self):
        specs: List[CustomDictSpec] = [
            {
                "slot": "STCharacters",
                "pairs": [("龙", "龍龍")],
                "mode": "append",
            }
        ]

        cc = OpenCC.from_dicts("s2t", specs)

        self.assertEqual(cc.get_config(), "s2t")
        self.assertEqual(cc.convert("龙"), "龍龍")

    def test_from_dict_files_custom_st_characters(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmpdir:
            dict_path = Path(tmpdir) / "custom_st_characters.txt"
            dict_path.write_text(
                "龙\t龍龍\n",
                encoding="utf-8",
            )

            specs: List[CustomDictFileSpec] = [
                {
                    "slot": "STCharacters",
                    "files": [str(dict_path)],
                    "mode": "append",
                }
            ]

            cc = OpenCC.from_dict_files("s2t", specs)

            self.assertEqual(cc.get_config(), "s2t")
            self.assertEqual(cc.convert("龙"), "龍龍")

    def test_post_load_custom_dicts(self):
        cc = OpenCC("s2t")

        cc.load_custom_dicts([
            {
                "slot": "STCharacters",
                "pairs": [("龙", "龍龍")],
                "mode": "append",
            }
        ])

        self.assertEqual(cc.convert("龙"), "龍龍")

    def test_post_load_custom_dict_files(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmpdir:
            dict_path = Path(tmpdir) / "custom_st_characters.txt"
            dict_path.write_text(
                "龙\t龍龍\n",
                encoding="utf-8",
            )

            cc = OpenCC("s2t")

            cc.load_custom_dict_files([
                {
                    "slot": "STCharacters",
                    "files": [str(dict_path)],
                    "mode": "append",
                }
            ])

            self.assertEqual(cc.convert("龙"), "龍龍")

    def test_from_user_dict_entries_preserves_domain_term(self):
        user_dict: List[UserDictEntry] = [
            {
                "word": "帕兰蒂尔",
                "freq": 100000,
                "tag": "nz",
            }
        ]

        cc = OpenCC.from_user_dict_entries("s2t", user_dict)

        self.assertEqual(
            cc.jieba_cut("帕兰蒂尔", hmm=False),
            ["帕兰蒂尔"],
        )

    def test_from_user_dict_files_preserves_domain_term(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmpdir:
            dict_path = Path(tmpdir) / "jieba_user_dict.txt"
            dict_path.write_text(
                "帕兰蒂尔 100000 nz\n",
                encoding="utf-8",
            )

            cc = OpenCC.from_user_dict_files(
                "s2t",
                [str(dict_path)],
            )

            self.assertEqual(
                cc.jieba_cut("帕兰蒂尔", hmm=False),
                ["帕兰蒂尔"],
            )

    def test_post_load_user_dict_entries(self):
        cc = OpenCC("s2t")

        cc.load_user_dict_entries([
            {
                "word": "帕兰蒂尔",
                "freq": 100000,
                "tag": "nz",
            }
        ])

        self.assertEqual(
            cc.jieba_cut("帕兰蒂尔", hmm=False),
            ["帕兰蒂尔"],
        )

    def test_post_load_user_dict_files(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmpdir:
            dict_path = Path(tmpdir) / "jieba_user_dict.txt"
            dict_path.write_text(
                "帕兰蒂尔 100000 nz\n",
                encoding="utf-8",
            )

            cc = OpenCC("s2t")
            cc.load_user_dict_files([str(dict_path)])

            self.assertEqual(
                cc.jieba_cut("帕兰蒂尔", hmm=False),
                ["帕兰蒂尔"],
            )

    def test_user_dict_entries_compose_with_custom_phrase(self):
        user_dict: List[UserDictEntry] = [
            {
                "word": "帕兰蒂尔",
                "freq": 100000,
                "tag": "nz",
            }
        ]

        cc = OpenCC.from_user_dict_entries("s2t", user_dict)

        cc.load_custom_dicts([
            {
                "slot": "STPhrases",
                "pairs": [("帕兰蒂尔", "柏蘭蒂爾")],
                "mode": "append",
            }
        ])

        self.assertEqual(
            cc.jieba_cut("帕兰蒂尔", hmm=False),
            ["帕兰蒂尔"],
        )
        self.assertEqual(
            cc.convert("帕兰蒂尔是一家公司"),
            "柏蘭蒂爾是一家公司",
        )

    def test_user_dict_files_compose_with_custom_phrase_files(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmpdir:
            jieba_path = Path(tmpdir) / "jieba_user_dict.txt"
            opencc_path = Path(tmpdir) / "custom_st_phrases.txt"

            jieba_path.write_text(
                "帕兰蒂尔 100000 nz\n",
                encoding="utf-8",
            )
            opencc_path.write_text(
                "帕兰蒂尔\t柏蘭蒂爾\n",
                encoding="utf-8",
            )

            cc = OpenCC.from_user_dict_files(
                "s2t",
                [str(jieba_path)],
            )

            cc.load_custom_dict_files([
                {
                    "slot": "STPhrases",
                    "files": [str(opencc_path)],
                    "mode": "append",
                }
            ])

            self.assertEqual(
                cc.convert("帕兰蒂尔是一家公司"),
                "柏蘭蒂爾是一家公司",
            )

    def test_custom_dict_survives_config_switch(self):
        user_specs: List[CustomDictSpec] = [
            {
                "slot": "STCharacters",
                "pairs": [("龙", "龍龍")],
                "mode": "append",
            }
        ]

        cc = OpenCC.from_dicts(
            "s2t", user_specs
        )

        self.assertEqual(cc.convert("龙"), "龍龍")

        cc.set_config("t2s")
        self.assertEqual(cc.convert("龍"), "龙")

        cc.set_config("s2t")
        self.assertEqual(cc.convert("龙"), "龍龍")

    def test_available_slots_contains_expected_slots(self):
        slots = OpenCC.available_slots()

        self.assertIn("STCharacters", slots)
        self.assertIn("STPhrases", slots)
        self.assertIn("HKPhrases", slots)
        self.assertIn("HKPhrasesRev", slots)


if __name__ == "__main__":
    unittest.main()
