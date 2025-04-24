from python.opencc_jieba_pyo3 import OpenCC

text = "“春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少”"
# text = "潦水盡而寒潭清，煙光凝而暮山紫。儼驂騑於上路，訪風景於崇阿；臨帝子之長洲，得天人之舊館。"
opencc = OpenCC()
print(f"Original text: {text}")
print(f"Default config: {opencc.config}")
original_text_code = opencc.zho_check(text)
print(f"Original text code: {original_text_code}")
opencc.config = "t2s" if original_text_code == 1 else "s2t"
converted = opencc.convert(text, True)
converted_code = opencc.zho_check(converted)
print(f"Auto config: {opencc.config}")
print(f"Converted text: {converted}")
print(f"Converted text code: {converted_code}")
opencc.config = "t2s" if converted_code == 1 else "s2t"
converted_2 = opencc.convert(converted, True)
print("Reconvert " + opencc.config + ": " + converted_2)
cut_text = opencc.jieba_cut(text)
print(f"Cut text: {cut_text}")
join_text = opencc.jieba_cut_and_join(text)
print(f"Joined text: {join_text}")
keywords_textrank = opencc.jieba_keyword_extract_textrank(text, 5)
print(f"Keywords TextRank: {keywords_textrank}")
keywords_tfidf = opencc.jieba_keyword_extract_tfidf(text, 5)
print(f"Keywords TF-IDF: {keywords_tfidf}")
keywords_weights_textrank = opencc.jieba_keyword_weight_textrank(text, 5)
print(f"Keywords Weights TextRank: {keywords_weights_textrank}")
keywords_weights_tfidf = opencc.jieba_keyword_weight_tfidf(text, 5)
print(f"Keywords Weights TF-IDF: {keywords_weights_tfidf}")