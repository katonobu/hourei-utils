import os
import requests
import xml.etree.ElementTree as ET
import copy

class HoureiXml():
    def __init__(self, xml_base_path, user_data = {}):
        self.user_data = user_data
        self.xml_base_path = xml_base_path
        self.xml_str = ""
        self.hourei_id = ""

    def get_xml_by_hourei_id(self, hourei_id, verbose = True):
        self.hourei_id = hourei_id
        xml_file_path = os.path.join(self.xml_base_path, hourei_id, f"{hourei_id}.xml")
        if not os.path.isfile(xml_file_path):
            if verbose:
                print("Not found xml file, get it using 法令-API")
            url = f"https://elaws.e-gov.go.jp/api/1/lawdata/{hourei_id}"
            rsp = requests.get(url)
            if rsp.ok:
                self.xml_str = rsp.text
                os.makedirs(os.path.dirname(xml_file_path), exist_ok=True)
                with open(xml_file_path, "w", encoding='utf-8') as f:
                    f.write(self.xml_str)
                if verbose:
                    print(f'Write downloaded xml to {xml_file_path}')
            else:
                self.xml_str = ""
                if verbose:
                    print(f'Fail to get {hourei_id}')
        else:
            if verbose:
                print('xml file found, use it')
            with open(xml_file_path, encoding='utf-8') as f:
                self.xml_str = f.read()
        return self.xml_str

    def parse_xml_tree(self, start_xpath = "./ApplData/LawFullText"):
        self.root = ET.fromstring(self.xml_str)
        self._handle_xml(self.root.find(start_xpath), self.user_data)
        self.user_analyse_finished()
        self.analyse_finished()

    def _handle_xml(self, el, user_data):
        self._handle_law(el, user_data)

    def _handle_law(self, el, user_data):
        for ch_el in el.findall("Law"):
            local_data = self.law_handler(ch_el, user_data)
            # <LawNum> | <LawBody>
            self._handle_law_body(ch_el, local_data)

    def _handle_law_body(self, el, user_data):
        for ch_el in el.findall("LawBody"):
            local_data = self.law_body_handler(ch_el, user_data)
        # LawBody
        # <LawTitle> | <EnactStatement> | <TOC> | 
        # <Preamble> | <MainProvision> | <SupplProvision> | 
        # <AppdxTable> | <AppdxNote> | <AppdxStyle> | 
        # <Appdx> | <AppdxFig> | <AppdxFormat>
            self._handle_law_title(ch_el, local_data)
            self._handle_main_provision(ch_el, local_data)

    def _handle_law_title(self, el, local_data):
        for ch_el in el.findall("LawTitle"):
            local_data = self.law_title_handler(ch_el, local_data)
            local_data = self.user_law_title_handler(ch_el, local_data)

    def _handle_main_provision(self, el, user_data):
        for ch_el in el.findall("MainProvision"):
            local_data = self.main_provision_handler(ch_el, user_data)
            local_data = self.user_main_provision_handler(ch_el, local_data)
            # <Part> | <Section> | 
            # <Chapter> | <Article> | <Paragraph>
            self._handle_part(ch_el, local_data)
            self._handle_chapter(ch_el, local_data)
            self._handle_section(ch_el, local_data)
            self._handle_article(ch_el, local_data)
            self._handle_paragraph(ch_el, local_data)

    def _handle_part(self, el, user_data):
        for ch_el in el.findall("Part"):
            local_data = self.part_handler(ch_el, user_data)
            local_data = self.user_part_handler(ch_el, local_data)
            # <PartTitle> | <Article> | <Chapter>
            self._handle_chapter(ch_el, local_data)
            self._handle_article(ch_el, local_data)
            self.user_post_part_handler(ch_el, local_data)

    def _handle_chapter(self, el, user_data):
        for ch_el in el.findall("Chapter"):
            local_data = self.chapter_handler(ch_el, user_data)
            local_data = self.user_chapter_handler(ch_el, local_data)
            # <ChapterTitle> | <Article> | <Section>
            self._handle_section(ch_el, local_data)
            self._handle_article(ch_el, local_data)
            self.user_post_chapter_handler(ch_el, local_data)

    def _handle_section(self, el, user_data):
        for ch_el in el.findall("Section"):
            local_data = self.section_handler(ch_el, user_data)
            local_data = self.user_section_handler(ch_el, local_data)
            # <SectionTitle> | <Article> | <Subsection> | <Division>
            self._handle_subsection(ch_el, local_data)
            self._handle_article(ch_el, local_data)
            self.user_post_section_handler(ch_el, local_data)

    def _handle_subsection(self, el, local_data):
        for ch_el in el.findall("Subsection"):
            local_data = self.subsection_handler(ch_el, local_data)
            local_data = self.user_subsection_handler(ch_el, local_data)
            # ??
            self._handle_article(ch_el, local_data)

    def _handle_article(self, el, user_data):
        for ch_el in el.findall("Article"):
            local_data = self.article_handler(ch_el, user_data)
            local_data = self.user_article_handler(ch_el, local_data)
            # <ArticleCaption> | <ArticleTitle> | <Paragraph> | <SupplNote>
            self._handle_paragraph(ch_el, local_data)
            self.user_post_article_handler(ch_el, local_data)

    def _handle_paragraph(self, el, user_data):
        for ch_el in el.findall("Paragraph"):
            local_data = self.paragraph_handler(ch_el, user_data)
            local_data = self.user_paragraph_handler(ch_el, local_data)
            # <ParagraphCaption> | <ParagraphNum> | 
            # <ParagraphSentence> | 
            # <AmendProvision> | <Class> | <TableStruct> | <FigStruct> | <StyleStruct> | 
            # <Item> | <List>
            self._handle_paragraph_sentence(ch_el, local_data)
            self._handle_item(ch_el, local_data)

    def _handle_paragraph_sentence(self, el, user_data):
        for ch_el in el.findall("ParagraphSentence"):
            local_data = self.paragraph_sentence_handler(ch_el, user_data)
            local_data = self.user_paragraph_sentence_handler(ch_el, local_data)
            # <Sentence>
            self._handle_sentence(ch_el, local_data)

    def _handle_item(self, el, user_data):
        for ch_el in el.findall("Item"):
            local_data = self.item_handler(ch_el, user_data)
            local_data = self.user_item_handler(ch_el, local_data)
            # <ItemTitle> | <ItemSentence> | <Subitem1> | 
            # <TableStruct> | <FigStruct> | <StyleStruct> | <List>
            self._handle_item_sentence(ch_el, local_data)

    def _handle_item_sentence(self, el, user_data):
        for ch_el in el.findall("ItemSentence"):
            local_data = self.item_sentencehandler(ch_el, user_data)
            local_data = self.user_item_sentence_handler(ch_el, local_data)
            # <Sentence> | <Column> | <Table>
            self._handle_sentence(ch_el, local_data)

    def _handle_sentence(self, el, user_data):
        for ch_el in el.findall("Sentence"):
            local_data = self.sentence_handler(ch_el, user_data)
            local_data = self.user_sentence_handler(ch_el, local_data)
            # <Line> | <QuoteStruct> | <ArithFormula> | 
            # <Ruby> | <Sup> | <Sub> | string
            self._handle_inline(ch_el, local_data)

    def _handle_inline(self, el, user_data):
        # <Ruby> | <Sup> | <Sub> | string
        pass    

# ---- system define handler
    def analyse_finished(self):
        pass

    def law_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        return new_user_data

    def main_provision_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        new_user_data.update({'_id_str':"Mp"})
        return new_user_data

    def law_num_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        return new_user_data

    def law_body_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        return new_user_data

    def law_title_handler(self, el, user_data):
        user_data.update({'_law_title':self.get_inline_text(el).strip()})
        new_user_data = copy.deepcopy(user_data)
        return new_user_data

    def toc_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        return new_user_data
        
    def part_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        if '_id_str' in user_data:
            new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-Pa{el.get("Num")}'})
        return new_user_data

    def chapter_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        if '_id_str' in user_data:
            new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-Ch_{el.get("Num")}'})
        return new_user_data

    def section_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        if '_id_str' in user_data:
            new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-Se_{el.get("Num")}'})
        return new_user_data

    def subsection_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        if '_id_str' in user_data:
            new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-Ss_{el.get("Num")}'})
        return new_user_data

    def article_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        if '_id_str' in user_data:
            new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-At_{el.get("Num")}'})
        return new_user_data

    def paragraph_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        if '_id_str' in user_data:
            new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-Pr_{el.get("Num")}'})
        return new_user_data

    def paragraph_sentence_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        return new_user_data

    def item_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        if '_id_str' in user_data:
            new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-It_{el.get("Num")}'})
        return new_user_data

    def item_sentencehandler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        return new_user_data
    
    def sentence_handler(self, el, user_data):
        new_user_data = copy.deepcopy(user_data)
        if '_id_str' in user_data:
            if el.get("Num") is not None:
                new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-Sn_{el.get("Num")}'})
            else:
                new_user_data.update({'_id_str':f'{new_user_data["_id_str"]}-Sn_0'})
        return new_user_data

# ---- user define handler
    def user_analyse_finished(self):
        pass

    def get_inline_text(self, el):
        # ルビをかっこでくくる
        text = el.text
        for ruby in el.findall("Ruby"):
            text += ruby.text
            text += f'({ruby.find("Rt").text})'
            text += ruby.tail
        text += el.tail
        return text
    
    def user_law_title_handler(self, el, user_data):
        return user_data
    
    def user_main_provision_handler(self, el, user_data):
        return user_data

    def user_part_handler(self, el, user_data):
        return user_data
    
    def user_post_part_handler(self, el, user_data):
        return user_data
    
    def user_chapter_handler(self, el, user_data):
        return user_data
    
    def user_post_chapter_handler(self, el, user_data):
        return user_data

    def user_section_handler(self, el, user_data):
        return user_data

    def user_subsection_handler(self, el, user_data):
        return user_data

    def user_post_section_handler(self, el, user_data):
        return user_data

    def user_article_handler(self, el, user_data):
        return user_data

    def user_post_article_handler(self, el, user_data):
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
    import copy
    import json
    import re

    class IdDump(HoureiXml):
        def user_main_provision_handler(self, el, user_data):
            self.user_data.update({
                'law_title':user_data['_law_title'],
                'article_ids':[]
            })
            return user_data

        def user_article_handler(self, el, user_data):
            self.user_data["article_ids"].append(user_data['_id_str'])
            return user_data

    hourei_base_dir = os.path.join(os.path.dirname(__file__), "..", "hourei_data")
    hourei_xml = IdDump(hourei_base_dir)

    hourei_ids = [
        "414AC0000000122", # 知的財産基本法
        "334AC0000000121", # 特許法
        "334AC0000000123", # 実用新案法
        "334AC0000000125", # 意匠法
        "334AC0000000127", # 商標法

        # Divisionあり
        "129AC0000000089", # 民法
        "325AC0000000131", # 電波法
        # Subsectionあり
        "359AC0000000086", # 電気通信事業者法

        "503AC0000000035", # デジタル社会形成基本法
        "426AC1000000104", # サイバーセキュリティ基本法
        "345AC0000000090", # 情報処理の促進に関する法律

        # 章なし条はじまり
        "411AC0000000127", # 国旗及び国歌に関する法律

        # 条なし項始まり
        "503M60000008044", # 有明海及び八代海等を再生するための特別措置に関する法律第十一条第一項に規定する特定事業を定める省令
    ]

    results = []
    for hourei_id in hourei_ids:
        xml_str = hourei_xml.get_xml_by_hourei_id(hourei_id, verbose=False)
        if 0 < len(xml_str):
#            print('Start parse/analyse xml')
            try:
                hourei_xml.parse_xml_tree()
                # idから条番号を抽出して条番号の連続性をチェック
                # 条番号が"数値:数値"の時は、その範囲の条文が削除されているとみなす。
                at_number = []
                skip_at = []
                print(hourei_xml.user_data["law_title"])
                # idに含まれる条番号を抽出
                for id in hourei_xml.user_data["article_ids"]:
                    m = re.match(r"^(\d+)(.*)$", id.split("-At_")[-1])
                    if m:
                        at_number.append(int(m.groups()[0], 10))
                        # 条番号に":"を含む場合(=条番号範囲指定)
                        if ":" in id:
                            # 開始、終了の条番号ペアを表示&保存
                            skip_at.append([int(num_str, 10) for num_str in m.group().split(":")])
                            print(f"  {m.group()}")
                # 条番号を一意にしてソート
                uniqued_sorted_at_numbers = sorted(list(set(at_number)),reverse=False)
                for idx, num in enumerate(uniqued_sorted_at_numbers):
                    # 2つめ以降の条番号に対し、前の条番号と不連続になっている?
                    if 0 < idx and (num - uniqued_sorted_at_numbers[idx-1]) != 1:
                        skip_count = num - uniqued_sorted_at_numbers[idx-1]
                        # 条番号範囲指定の情報と突き合わせて整合するならきっと削除されてる。
                        found = False
                        for skip_info in skip_at:
                            if skip_info[1] == num -1:
                                found = True
                                if skip_info[1] - skip_info[0] + 1 == skip_count:
                                    print(f"  discontinuous detected, but matched to skip info At:{num}, skip:{skip_count}, start:{skip_info[0]}, end:{skip_info[1]}")
                                    
                                    pass
                                else:
                                    print(f"    Invalid skip : At:{num}, skip:{skip_count}")
                                break
                        if found == False:
                            print(f"    Skip detected : At:{num}, skip:{skip_count}, but not found skip info")
                results.append(copy.deepcopy(hourei_xml.user_data))
                hourei_xml.user_data = {}

            except Exception as e:
                print("Catch exception....")
                raise e

    with open("result.json", "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)