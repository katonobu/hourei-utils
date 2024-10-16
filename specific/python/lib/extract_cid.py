import os
import re
import json

if __name__ == "__main__":
    files = [
        "tokkyo_chikujo_text.json",
        "jitsu_chikujo_text.json",
        "isho_chikujo_text.json",
        "shouhyou_chikujo_text.json"
    ]

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"..","extracted_text_from_pdf"))

    cids = []
    for file in files:
        with open(os.path.join(base_path, file), encoding='utf-8') as f:
            in_obj = json.load(f)

        if "pages" in in_obj:
            for page in in_obj["pages"]:
                for line in page["lines"]:
                    cids += [cid for cid in re.findall(r"\(cid:\d+\)", line)]

    sorted_cids = sorted(list(set(cids)), key=lambda x:int(x.split(":")[-1].replace(")",""), 10), reverse=False)
    cid_obj = {cid:"<"+cid+">" for cid in sorted_cids}

    with open(os.path.join(os.path.dirname(__file__),"cid_trans_table.json"), encoding='utf-8') as f:
        existing_cid_obj = json.load(f)
    cid_obj.update(existing_cid_obj)

    with open(os.path.join(base_path, "cid_trans_table_merged.json"), "w", encoding='utf-8') as f:
        json.dump(cid_obj, f, indent=2, ensure_ascii=False)

    print(json.dumps(cid_obj, indent=2, ensure_ascii=False))
