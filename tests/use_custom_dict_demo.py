from typing import List

from opencc_jieba_pyo3 import OpenCC, CustomDictFileSpec


cc = OpenCC("hk2sp")

cc.load_user_dict_files(["tests/data/user_dict.txt"])

specs: List[CustomDictFileSpec] = [
    {
        "slot": "HKPhrasesRev",
        "mode": "append",
        "files": ["tests/data/my_hk_dict.txt"],
    }
]

cc.load_custom_dict_files(specs)

print(cc.convert("這個細路哥很靈活"))