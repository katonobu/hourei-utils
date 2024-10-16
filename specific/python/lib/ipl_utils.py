import os
import sys
import re
import cid_trans


def is_skipped_line(line):
    # ページ番号表記
    if re.match(r"^\d+ 特", line) or re.match(r"^\d+ 特 許", line) or line=="許" or line=="法":
        return True
    if re.match(r"^特 許 法 \d+", line):
        return True
    # 内部間利用?フッター
    if re.match(r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}  v\d.\d{2}", line):
        return True
    if re.match(r"^\d{2}-\d{2}-\d{3}　.*?  Page ([0-9]+)$", line):
        return True
    # 空行
    if len(line) == 0:
        return True
    else:
        return False

def make_trans():
    return str.maketrans({
        '︑':'、',
        '︒':'。',
        '︵':'（',
        '︶':'）',
        '︹':'［',
        '︺':'］',
        '︿':'＜',
        '﹀':'＞'
    })

def replace_line(line, trans, opt=None):
    line = line.translate(trans)
    line = cid_trans.cid_trans(line)
    return line


if __name__ == "__main__":
    import json
    in_file_name = "tokkyo_chikujo_text.json"
    out_file_name = "tokkyo_chikujo_text2.json"
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    in_file_base = os.path.join(base_path, "extracted_text_from_pdf")
    in_file_path = os.path.join(in_file_base, in_file_name)
    out_file_base = os.path.join(base_path, "extracted_text_from_pdf")
    out_file_path = os.path.join(out_file_base, out_file_name)

    with open(in_file_path, encoding='utf-8') as f:
        in_obj = json.load(f)
    result = []
    if "pages" in in_obj:
        trans = make_trans()

        pages = in_obj["pages"]
        for page in pages:
            out_obj = {
                "page_number": page["page_number"],
                "lines": []
            }
            for in_line in page["lines"]:
                if is_skipped_line(in_line):
                    continue
                out_line = replace_line(in_line, trans)
                if 0 < len(out_line):
                    out_obj["lines"].append(out_line)
            if 0 < len(out_obj["lines"]):
                result.append(out_obj)
    
    with open(out_file_path, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)