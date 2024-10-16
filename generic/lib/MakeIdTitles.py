from HoureiXml import HoureiXml

class MakeIdTitles(HoureiXml):
    def user_law_title_handler(self, el, user_data):
        title_str = self.get_inline_text(el).strip()
        self.user_data.update({'id_titles':{"LawTitle":title_str}})
        return user_data
    
    def user_main_provision_handler(self, el, user_data):
#        self.user_data.update({'id_titles':{}})
        return user_data

    def user_part_handler(self, el, user_data):
        title_str = self.get_inline_text(el.find("PartTitle")).strip()
        id_str = user_data["_id_str"]
        self.user_data["id_titles"].update({id_str:title_str})
        return user_data
    
    def user_chapter_handler(self, el, user_data):
        title_str = self.get_inline_text(el.find("ChapterTitle")).strip()
        id_str = user_data["_id_str"]
        self.user_data["id_titles"].update({id_str:title_str})
        return user_data

    def user_section_handler(self, el, user_data):
        title_str = self.get_inline_text(el.find("SectionTitle")).strip()
        id_str = user_data["_id_str"]
        self.user_data["id_titles"].update({id_str:title_str})
        return user_data

    def user_article_handler(self, el, user_data):
        title_str = self.get_inline_text(el.find("ArticleTitle")).strip()
        id_str = user_data["_id_str"]
        self.user_data["id_titles"].update({id_str:title_str})
        return user_data

    def user_paragraph_handler(self, el, user_data):
        return user_data

    def user_paragraph_sentence_handler(self, el, user_data):
        return user_data

    def user_item_handler(self, el, user_data):
        return user_data

    def user_item_sentence_handler(self, el, user_data):
        return user_data

    def user_sentence_handler(self, el, user_data):
        return user_data

if __name__ == "__main__":
    import os
    import re

    hourei_base_dir = os.path.join(os.path.dirname(__file__), "..", "hourei_data")
    hourei_xml = MakeIdTitles(hourei_base_dir)

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

        # コーナーケース
        "503M60000008044", # 条なし項始まり
    ]

    for hourei_id in hourei_ids:
        xml_str = hourei_xml.get_xml_by_hourei_id(hourei_id, verbose = False)
        if 0 < len(xml_str):
            try:
                hourei_xml.parse_xml_tree()
                print(hourei_xml.user_data['id_titles']['LawTitle'])
                for id in hourei_xml.user_data['id_titles']:
                    print(f"  {id}:{hourei_xml.user_data['id_titles'][id]}")
            except Exception as e:
                print("Catch exception....")
                raise e

