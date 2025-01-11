import os
import re
import json
from HoureiXml import HoureiXml
from MakeMp3 import MakeMp3

class MakeTssTextChDirAtFile(HoureiXml):
    def __init__(self, xml_base_path, user_data = {}, output_id_filter_str = "", del_id_str = "Mp-Ch_", dry_run = False, spped_percent = 100):
        super().__init__(xml_base_path, user_data)
        self.output_id_filter_str = output_id_filter_str
        self.del_id_str = del_id_str
        self.dry_run = dry_run
        self.speed_percent = spped_percent

    # 【Python3】括弧と括弧内文字列削除
    # https://qiita.com/mynkit/items/d6714b659a9f595bcac8
    def delete_brackets(self,s):
        """
        括弧と括弧内文字列を削除
        """
        """ brackets to zenkaku """
        table = {
            "(": "（",
            ")": "）",
            "<": "＜",
            ">": "＞",
            "{": "｛",
            "}": "｝",
            "[": "［",
            "]": "］"
        }
        for key in table.keys():
            s = s.replace(key, table[key])
        """ delete zenkaku_brackets """
        l = ['（[^（|^）]*）', '【[^【|^】]*】', '＜[^＜|^＞]*＞', '［[^［|^］]*］',
#            地の「」は第二条定義で出てくるので消さずに残す。             
#            '「[^「|^」]*」', '｛[^｛|^｝]*｝', '〔[^〔|^〕]*〕', '〈[^〈|^〉]*〉']
                             '｛[^｛|^｝]*｝', '〔[^〔|^〕]*〕', '〈[^〈|^〉]*〉']
        for l_ in l:
            s = re.sub(l_, "", s)
        """ recursive processing """
        return self.delete_brackets(s) if sum([1 if re.search(l_, s) else 0 for l_ in l]) > 0 else s


    def get_inline_text(self, el):
        text = el.text
        for ruby in el.findall("Ruby"):
            # ルビを読ませる
            text += ruby.find("Rt").text
            text += ruby.tail
        text += el.tail
        text = self.delete_brackets(text)
        if 'replace_res' in self.user_data:
            for replace_re in self.user_data['replace_res']:
                text = re.sub(replace_re, self.user_data['replace_res'][replace_re], text)
        if 'replace_strs' in self.user_data:
            for replace_str in self.user_data['replace_strs']:
                text = text.replace(replace_str, self.user_data['replace_strs'][replace_str])
        return text

    def user_law_title_handler(self, el, user_data):
        title_str = self.get_inline_text(el).strip()
        self.user_data.update({"LawTitle":title_str})
        return user_data

    def user_main_provision_handler(self, el, user_data):
        hourei_base_dir = self.xml_base_path
        if self.dry_run:
            mp3_out_dir = os.path.join(hourei_base_dir, self.hourei_id, "mp3_txt")
        else:
            dir_name_str = "mp3"
            if self.speed_percent != 100:
                dir_name_str = f"mp3_x{self.speed_percent/100:1.1f}".replace(".","_")
            mp3_out_dir = os.path.join(hourei_base_dir, self.hourei_id, dir_name_str)

        name_replace_obj = {}
        name_replace_file_path = os.path.join(hourei_base_dir, self.hourei_id, "at_name_replace.json")
        if os.path.isfile(name_replace_file_path):
            with open(name_replace_file_path, encoding='utf-8') as f:
                name_replace_obj = json.load(f)
        self.user_data['name_replace_obj'] = name_replace_obj

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

    def user_analyse_finished(self):
        self.mk_mp3.finish()

    def user_chapter_handler(self, el, user_data):
        user_data.update({
            'dir_names':[]
        })
        dir_name = self.get_inline_text(el.find("ChapterTitle")).strip().replace("　","_")
        user_data['dir_names'].append(dir_name)
        self.user_data.update({
            'playlist_info':[] 
        })
        self.mk_mp3.mp3_mkdir(user_data['_id_str'], user_data["dir_names"])
        return user_data

    def user_post_chapter_handler(self, el, user_data):
        self.mk_mp3.mp3_playlist(self.user_data['playlist_info'])

    def user_section_handler(self, el, user_data):
        dir_name = self.get_inline_text(el.find("SectionTitle")).strip().replace("　","_")
        user_data['dir_names'].append(dir_name)
        self.user_data.update({
            'playlist_info':[] 
        })
        self.mk_mp3.mp3_mkdir(user_data['_id_str'], user_data["dir_names"])
        return user_data

    def user_post_section_handler(self, el, user_data):
        self.mk_mp3.mp3_playlist(self.user_data['playlist_info'])

    def user_article_handler(self, el, user_data):
        user_data.update({
            "parent_article_str":f'第{el.get("Num").replace("_","の")}条'
        })
        self.user_data.update({
            'tts_texts':[]
        })
        return user_data

    def convert_article_sentences(self, id_str, texts):
        if 'name_replace_obj' in self.user_data and id_str in self.user_data['name_replace_obj'] and 0 < len(self.user_data['name_replace_obj'][id_str]):
            new_texts = []
            for text in texts:
                for item in self.user_data['name_replace_obj'][id_str]:
#                    text = text.replace(item['key'], item['key']+"\n"+item['str_to_replace']+"\n")
                    text = text.replace(item['key'], "\n"+item['str_to_replace']+"\n")
                for item in text.split("\n"):
                    new_texts.append(item)
            return new_texts
        else:
            return texts

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
        tts_text = '\n'.join(self.convert_article_sentences(user_data["_id_str"], self.user_data["tts_texts"]))
        self.mk_mp3.mp3_tts(file_name, tts_text.split('\n'), sound_title, self.user_data["LawTitle"], self.speed_percent * 2)

    def user_paragraph_handler(self, el, user_data):
        if "parent_article_str" not in user_data:
            # 条なしで来ることもある("503M60000008044")
            user_data.update({"parent_article_str":""})
        if "parent_article_str" in user_data:
            if el.get("Num") == "1":
                pass
            else:
                user_data.update({
                    "parent_article_str":f'{user_data["parent_article_str"]}第{el.get("Num")}項'
                })
        return user_data

    def user_item_handler(self, el, user_data):
        if "parent_article_str" in user_data:
            user_data.update({
                "parent_article_str":f'{user_data["parent_article_str"]}第{el.get("Num")}号'
            })
        return user_data

    def user_sentence_handler(self, el, user_data):
        if "parent_article_str" in user_data:
            if el.get("Num") == "1" or el.get("Num") == None: # "Num"がないときもparent_article_strは表示させる
                tts_text = f'{user_data["parent_article_str"]}\n{self.get_inline_text(el)}'
            else:
                tts_text = f'{self.get_inline_text(el)}'
            if 'tts_texts' in self.user_data:
                self.user_data["tts_texts"].append(tts_text)
        return user_data

if __name__ == "__main__":
#    hourei_id = "411AC0000000127" # 国旗及び国歌に関する法律
    hourei_id = "334AC0000000121" # 特許法

    # Subsectionに対応した? 電気通信事業法
    # Divisionに対応できていない。 民法
    # 章のない場合に対応できていない 国旗及び国歌に関する法律

    dry_run = True
    hourei_base_dir = os.path.join(os.path.dirname(__file__), "..", "hourei_data")
    hourei_xml = MakeTssTextChDirAtFile(
        hourei_base_dir,
        {
            'replace_strs':{
                '目的':'もくてき',
                '定義':'ていぎ'
            },
            'replace_res':{},
        }, 
        "1",
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

    print(hourei_xml.delete_brackets("ここ(の「か(っ)こ」)は削除されるべきだが、「ここ(但しここは除く)」は残るのが期待される動作である。"))
