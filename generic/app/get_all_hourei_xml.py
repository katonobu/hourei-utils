import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..','lib'))
from HoureiXml import HoureiXml

if __name__ == "__main__":
    import requests
    import xmltodict

    # 法令一覧を取得
    url = f"https://elaws.e-gov.go.jp/api/1/lawlists/2"
    response = requests.get(url)
    if response.ok:
        result = xmltodict.parse(response.text)
        if "DataRoot" in result and "Result" in result['DataRoot'] and 'Code' in result['DataRoot']['Result'] and result['DataRoot']['Result']['Code'] == '0':
            if "ApplData" in result['DataRoot'] and 'LawNameListInfo' in result['DataRoot']['ApplData']:
                # 法令一覧リスト
                law_name_ids = result['DataRoot']['ApplData']['LawNameListInfo']

                hourei_base_dir = os.path.join(os.path.dirname(__file__), "..", "hourei_data")
                hourei_xml = HoureiXml(hourei_base_dir)
                # 法令idでループ
                for law_name_id in law_name_ids:
                    print(f'Getting {law_name_id["LawName"]}')
                    xml_str = hourei_xml.get_xml_by_hourei_id(law_name_id['LawId'])
                    if 0 < len(xml_str):
                        print('Start parse/analyse xml')
                        # パースして例外が発生しないこと。
                        try:
                            hourei_xml.parse_xml_tree()
                            print("Parse succeede.")
                        except Exception as e:
                            print("Catch exception....")
                            raise e

