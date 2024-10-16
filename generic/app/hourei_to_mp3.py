import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..','lib'))
from replace_obj import replace_strs, replace_res
from MakeTssTextChDirAtFile import MakeTssTextChDirAtFile

if __name__ == "__main__":
    hourei_ids = [
        "414AC0000000122", # 知的財産基本法
        "334AC0000000121", # 特許法
        "334AC0000000123", # 実用新案法
        "334AC0000000125", # 意匠法
        "334AC0000000127", # 商標法

        "129AC0000000089", # 民法
        "325AC0000000131", # 電波法
        "359AC0000000086", # 電気通信事業者法

        "503AC0000000035", # デジタル社会形成基本法
        "426AC1000000104", # サイバーセキュリティ基本法
        "345AC0000000090", # 情報処理の促進に関する法律
    ]
    hourei_ids_advanced = [
        # コーナーケース
        "503M60000008044", # 条なし項始まり→何も生成されない
        "411AC0000000127" # 章なし条始まり 国旗及び国歌に関する法律→実行時エラー
    ]

    hourei_ids = [
        "334AC0000000121", # 特許法
    ]

    dry_run = False
    hourei_base_dir = os.path.join(os.path.dirname(__file__), "..", "hourei_data")

    hourei_xml = MakeTssTextChDirAtFile(
        hourei_base_dir,
        {
            'replace_strs':replace_strs,
            'replace_res':replace_res
        }, 
        "",#"1",
        "Mp-Ch_",
        dry_run
    )

    for hourei_id in hourei_ids:
        xml_str = hourei_xml.get_xml_by_hourei_id(hourei_id)
        if 0 < len(xml_str):
            print('Start parse/analyse xml')
            try:
                hourei_xml.parse_xml_tree()
            except Exception as e:
                print("Catch exception....")
                raise e
