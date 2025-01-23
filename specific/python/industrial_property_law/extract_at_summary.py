import os
import sys
import re
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))


def delete_brackets(s):
    """
    括弧と括弧内文字列を削除
    """
    """ brackets to zenkaku """
    table = {
        "(": "（",
        ")": "）"
    }
    for key in table.keys():
        s = s.replace(key, table[key])
    """ delete zenkaku_brackets """
    l = ['（[^（|^）]*）']
    for l_ in l:
        s = re.sub(l_, "", s)
    """ recursive processing """
    return delete_brackets(s) if sum([1 if re.search(l_, s) else 0 for l_ in l]) > 0 else s

skip_tails = [
    "条",
    "号",
    "項",
    "二",
    "三",
    "四",
    "五",
    "六",
    "本文",
    "まで",
    "ただし書",
    "⑴",
    "ⅱ",
    "⒜",
    "⑵",
    "⒝",
    "⑴⒜"
]

split_items = [
    "、",
    " ",
    "が",
    "理由となつた",
    "適用及び",
    "準用する",
    "条約",
    "この法律"
]

def extract_at_summary(structur_objs):
    extracted_obj = {}
    for at in structur_objs:
        single_line = delete_brackets(''.join(at["Article"]["Texts"]))
        id_str = at["Article"]["Id"]
        extracted_obj.update({id_str:[]})
        sentences = [s for s in single_line.split("。")]
        for line in sentences:
            if "［" in line and "］" in line:
                splitted = line.split("］")
                for s_line in splitted:
                    m = re.search("(第.*?条.*?)［(.*)］$", s_line+"］")
                    if m:
                        key = m.groups()[0]
                        val = m.groups()[1]
                        for item in split_items:
                            key = key.split(item)[-1]
                        key = key.strip()
                        extracted_obj[id_str].append({
                            "key":key,
                            "str_to_replace":val,
                        })
    return extracted_obj

if __name__ == "__main__":
    json_path = os.path.join(os.path.dirname(__file__), "..","extracted_text_from_pdf","tokkyo_chikujo_structured.json")
    with open(json_path, encoding='utf-8') as f:
        structur_objs = json.load(f)
    extracted_obj = extract_at_summary(structur_objs)
#    print(json.dumps(extracted_obj, indent=2, ensure_ascii=False))
    print(len(extracted_obj))

#    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","..","generic","hourei_data","334AC0000000121", "at_name_replace.json"))
    output_path = os.path.join(os.path.dirname(__file__), "..","extracted_text_from_pdf","tokkyo_at_name_replace.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(extracted_obj, f, indent=2, ensure_ascii=False)
