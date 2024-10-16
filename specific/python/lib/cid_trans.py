import os
import re
import json

base_path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(base_path, "cid_trans_table.json"), encoding='utf-8') as f:
    cid_trans_table = json.load(f)

def cid_trans(line):
    for item in cid_trans_table:
        line = re.sub(item.replace("(",r"\(").replace(")",r"\)"), cid_trans_table[item], line)
    return line

if __name__ == "__main__":
    print(json.dumps([{"org":item, "tranced":cid_trans(item)} for item in cid_trans_table], indent=2, ensure_ascii=False))
