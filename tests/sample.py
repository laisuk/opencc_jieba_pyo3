from opencc_jieba_pyo3 import OpenCC

text = "“春眠不觉晓，处处闻啼鸟。”"
segment_text = "我独自来到无人海岸线"
opencc = OpenCC("s2t")
converted = opencc.convert(text, punctuation=True)
print(converted)  # 「春眠不覺曉，處處聞啼鳥。」

# Segmentation
words = opencc.jieba_cut(segment_text, hmm=True)
print(words)  # ['我', '独自', '来到', '无人', '海岸线']

# Segmentation and join
joined = opencc.jieba_segment_join(segment_text, mode="cut", delim="/")
print(joined)  # 我/独自/来到/无人/海岸线

joined = opencc.jieba_segment_join(segment_text, mode="search", delim="/")
print(joined)  # 我/独自/来到/无人/海岸/岸线/海岸线

joined = opencc.jieba_segment_join(segment_text, mode="full", delim="/")
print(joined)  # 我/独/独自/自/自来/来/来到/到/无/无人/人/人海/海/海岸/海岸线/岸/岸线/线

joined = opencc.jieba_segment_join(segment_text, mode="tag", delim=" ")
print(joined)  # 我/r 独自/d 来到/v 无人/n 海岸线/n

# Keyword extraction (TextRank)
keywords = opencc.jieba_keyword_extract_textrank(segment_text, top_k=3)
print(keywords)  # ['海岸线', '无人', '来到']

# Keyword extraction (TF-IDF)
keywords_tfidf = opencc.jieba_keyword_extract_tfidf(segment_text, top_k=3)
print(keywords_tfidf)  # ['海岸线', '独自', '无人']

# Keyword weights (TextRank)
kw_weights = opencc.jieba_keyword_weight_textrank(segment_text, top_k=3)
print(kw_weights)  # [('海岸线', 9987587364.22353), ('无人', 9986551019.39923), ('来到', 9985428148.988083)]

# Keyword weights (TF-IDF)
kw_weights_tfidf = opencc.jieba_keyword_weight_tfidf(segment_text, top_k=3)
print(kw_weights_tfidf)  # [('海岸线', 1.995445949425), ('独自', 1.8446462134525), ('无人', 1.7299179778125)]