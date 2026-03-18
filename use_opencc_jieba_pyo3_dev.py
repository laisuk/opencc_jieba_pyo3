#!/usr/bin/env python3
"""
Quick smoke test for opencc_jieba_pyo3 after:
    maturin develop --release

Run:
    python use_opencc_jieba_pyo3_dev.py
"""

from __future__ import annotations

from opencc_jieba_pyo3 import OpenCC


def detect_auto_config(zho_code: int) -> str:
    """
    Heuristic:
      - if zho_check() returns 1 => treat as Traditional -> use t2s
      - otherwise => use s2t
    """
    return "t2s" if zho_code == 1 else "s2t"


def main() -> None:
    text = "“春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少”"
    # text = "潦水盡而寒潭清，煙光凝而暮山紫。儼驂騑於上路，訪風景於崇阿；臨帝子之長洲，得天人之舊館。"

    # opencc = OpenCC()
    opencc = OpenCC("T2S")
    opencc.set_config("Tw2S")
    opencc.config = "Tw2SP"
    print(f"Original config: {opencc.config}")
    print(f"Supported configs: {OpenCC.supported_configs()}")

    print(f"Original text: {text}")
    print(f"Default config: {opencc.config}")

    original_code = opencc.zho_check(text)
    print(f"Original text code: {original_code}")

    # First conversion (auto config)
    opencc.config = detect_auto_config(original_code)
    converted = opencc.convert(text, True)
    converted_code = opencc.zho_check(converted)

    print(f"Auto config: {opencc.config}")
    print(f"Converted text: {converted}")
    print(f"Converted text code: {converted_code}")

    # Reconvert (flip based on converted result)
    opencc.config = detect_auto_config(converted_code)
    reconverted = opencc.convert(converted, True)
    print(f"Reconvert {opencc.config}: {reconverted}")

    print("\n=== Jieba Segmentation ===")

    hmm = True

    cut_text = opencc.jieba_cut(text, hmm)
    print(f"Cut text: {cut_text}")

    cut_search = opencc.jieba_cut_for_search(text, hmm)
    print(f"Cut for search: {cut_search}")

    cut_all = opencc.jieba_cut_all(text)
    print(f"Cut all: {cut_all}")

    join_text = opencc.jieba_cut_and_join(text)
    print(f"Joined text: {join_text}")

    print("\n=== Jieba POS Tagging ===")

    tags = opencc.jieba_tag(text, hmm)
    print("Tags:")
    for word, tag in tags:
        print(f"  {word}/{tag}")

    print("\n=== Keyword Extraction ===")

    top_k = 5

    keywords_textrank = opencc.jieba_keyword_extract_textrank(text, top_k)
    print(f"Keywords TextRank (top {top_k}): {keywords_textrank}")

    keywords_tfidf = opencc.jieba_keyword_extract_tfidf(text, top_k)
    print(f"Keywords TF-IDF (top {top_k}): {keywords_tfidf}")

    keywords_weights_textrank = opencc.jieba_keyword_weight_textrank(text, top_k)
    print(f"Keywords Weights TextRank (top {top_k}): {keywords_weights_textrank}")

    keywords_weights_tfidf = opencc.jieba_keyword_weight_tfidf(text, top_k)
    print(f"Keywords Weights TF-IDF (top {top_k}): {keywords_weights_tfidf}")


if __name__ == "__main__":
    main()
