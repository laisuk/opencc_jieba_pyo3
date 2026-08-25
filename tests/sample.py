import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).absolute().parents[1]))

from opencc_jieba_pyo3 import OpenCC

text: str = "“春眠不觉晓，处处闻啼鸟。”"
segment_text: str = "我独自来到无人海岸线"

opencc = OpenCC("s2t")

converted: str = opencc.convert(text, punctuation=True)
print(converted)  # 「春眠不覺曉，處處聞啼鳥。」

# Segmentation
words: List[str] = opencc.jieba_cut(segment_text, hmm=True)
print(words)  # ['我', '独自', '来到', '无人', '海岸线']

# Segmentation and join
joined: str = opencc.jieba_segment_join(
    segment_text,
    mode="cut",
    delim="/",
)
print("cut: " + joined)  # 我/独自/来到/无人/海岸线

joined = opencc.jieba_segment_join(
    segment_text,
    mode="search",
    delim="/",
)
print("search: " + joined)  # 我/独自/来到/无人/海岸/岸线/海岸线

joined = opencc.jieba_segment_join(
    segment_text,
    mode="full",
    delim="/",
)
print("full: " + joined)

joined = opencc.jieba_segment_join(
    segment_text,
    mode="tag",
    delim=" ",
    separator=":",
)
print("tag: " + joined)  # 我:r 独自:d 来到:v 无人:n 海岸线:n

# Keyword extraction
keywords: List[str] = opencc.jieba_keyword_extract_textrank(
    segment_text,
    top_k=3,
)
print(keywords)

keywords_tfidf: List[str] = opencc.jieba_keyword_extract_tfidf(
    segment_text,
    top_k=3,
)
print(keywords_tfidf)

# Keyword weights
kw_weights: List[Tuple[str, float]] = opencc.jieba_keyword_weight_textrank(
    segment_text,
    top_k=3,
)
print(kw_weights)

kw_weights_tfidf: List[Tuple[str, float]] = opencc.jieba_keyword_weight_tfidf(
    segment_text,
    top_k=3,
)
print(kw_weights_tfidf)
