import os
import sys
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','..','generic','lib'))
from replace_obj import replace_strs, replace_res
from MakeTssTextChDirAtFile import MakeTssTextChDirAtFile
from MakeMp3 import MakeMp3

class ChikujoTtsText(MakeTssTextChDirAtFile):
    _purpose_replace_strs = {
        '一':'1',
        '二':'2',
        '三':'3',
        '四':'4',
        '五':'5',
        '六':'6',
        '七':'7',
        '八':'8',
        '九':'9',
        '〇':'0',
        '⑴':'1',
        '⑵':'2',
        '⑶':'3',
        '⑷':'4',
        '⑸':'5',
        '⑹':'6',
        '⑺':'7',
        '⑻':'8',
        '⑼':'9',
        '⑽':'10',
        '①':'1',
        '②':'2',
        '③':'3',
        '④':'4',
        '⑤':'5',
        '⑥':'6',
        '⑦':'7',
        '⑧':'8',
        '⑨':'9',
        '⑩':'10',
    }

    def convert_line(self, text):
        text = self.delete_brackets(text)
        for replace_str in ChikujoTtsText._purpose_replace_strs:
            text = text.replace(replace_str, ChikujoTtsText._purpose_replace_strs[replace_str])
        if 'replace_res' in self.user_data:
            for replace_re in self.user_data['replace_res']:
                text = re.sub(replace_re, self.user_data['replace_res'][replace_re], text)
        if 'replace_strs' in self.user_data:
            for replace_str in self.user_data['replace_strs']:
                text = text.replace(replace_str, self.user_data['replace_strs'][replace_str])
        return text

    def get_purpose(self, id_str):
        articles = [at for at in self.user_data['structured_chikujo_obj'] if at['Article']['Id'] == id_str]
        purpose_texts = []
        if 0 < len(articles):
            article = articles[0]
            if 'Purpose' in article and 'Texts' in article['Purpose']:
                purpose_texts = [line+"。" for line in self.convert_line(''.join(article['Purpose']['Texts'])).split("。") if 0 < len(line)]
        return purpose_texts

    def user_main_provision_handler(self, el, user_data):
        hourei_base_dir = self.xml_base_path
        if self.dry_run:
            mp3_out_dir = os.path.join(hourei_base_dir, self.hourei_id, "chikujo_mp3_txt")
        else:
            mp3_out_dir = os.path.join(hourei_base_dir, self.hourei_id, "chikujo_mp3")
        self.mk_mp3 = MakeMp3(
            mp3_out_dir,
            self.output_id_filter_str,
            self.del_id_str,
            self.dry_run
        )
        user_data.update({
            'dir_names':[]
        })
        self.user_data.update({
            'playlist_info':[] 
        })
        return user_data

    def user_post_article_handler(self, el, user_data):
        cap_ele = el.find("ArticleCaption")
        caption_str = (cap_ele.text).strip() if cap_ele is not None else ""
        title_str = (el.find("ArticleTitle").text).strip()
        sound_title = f'{title_str} {caption_str}'
        file_name = f'{user_data["_id_str"]}.mp3'
        self.user_data['playlist_info'].append({
            "file":str(file_name),
            "title":str(sound_title),
        })
        tts_texts = self.user_data["tts_texts"]
        purpose_texts = self.get_purpose(user_data["_id_str"])
        if 0 < len(purpose_texts):
            tts_texts = tts_texts+['','趣旨','']+purpose_texts+[' ',' ']
        self.mk_mp3.mp3_tts(file_name, tts_texts, sound_title, self.user_data["LawTitle"]+"逐条解説")


if __name__ == "__main__":
    import json

    hourei_id = "334AC0000000121" # 特許法
    dry_run = False

    hourei_base_dir = os.path.join(os.path.dirname(__file__), "..", "hourei_data")

    structured_json_file_path = os.path.join(os.path.dirname(__file__), "..","extracted_text_from_pdf", "tokkyo_chikujo_structured.json")
    with open(structured_json_file_path, encoding='utf-8') as f:
        structured_obj = json.load(f)

    hourei_xml = ChikujoTtsText(
        hourei_base_dir,
        {
            'replace_strs':replace_strs,
            'replace_res':replace_res,
            'structured_chikujo_obj':structured_obj
        }, 
        "2",#"1",
        "Mp-Ch_",
        dry_run
    )

    xml_str = hourei_xml.get_xml_by_hourei_id(hourei_id)
    if 0 < len(xml_str):
        print('Start parse/analyse xml')
        try:
            hourei_xml.parse_xml_tree()
        except Exception as e:
            print("Catch exception....")
            raise e
