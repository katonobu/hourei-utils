import os
import sys
import re
import json
import tempfile

try:
    import pyttsx3
except ModuleNotFoundError as e:
    pyttsx3 = None

from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TCON, TYER    

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))

#sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','..','generic','lib'))
#from replace_obj import replace_strs, replace_res

replace_strs = {
    # 書
    '柱書':'はしらがき', # はしらか
    'ただし書':'ただしがき', # ただしか
}

def replace_append(append_to, line):
    if type(line) is str:
        line = re.sub("^ +","",line)
        if 0 < len(line):
            append_to.append(line)
    else:
        print(f"Error : {line}")
        exit()

def analyse_lines(all_lines, make_md):
    sentence = ""
    sentences = []        
    is_in_article_define = False
    is_in_zuhyou = False

    for lines in all_lines:
        for line in lines.split("\n"):
            if re.match(r"^ *$", line):
                # 空行はスキップ
                continue

            # 文章構造
            if re.match(r"^第 \d+ 章 　", line):
                print(f"Chapter : {line}")
                replace_append(sentences,sentence)
                if make_md:
                    sentence = "# "+line
                else:
                    sentence = line
                if line.endswith("。"):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^第 \d+ 節 　", line):
                print(f"Section : {line}")
                replace_append(sentences,sentence)
                if make_md:
                    sentence = "## "+line
                else:
                    sentence = line
                if line.endswith("。"):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^\d+[ 　]+", line):
                if is_in_article_define:
                    replace_append(sentences,sentence)
                    sentences.append("")
                    sentence = re.sub(r"^(\d+)[ 　]+(.*)$", r"\1. \2", line)
                else:
                    print(f"Subsection : {line}")
                    replace_append(sentences,sentence)
                    if make_md:
                        sentence = "### "+line
                    else:
                        sentence = line
                if line.endswith("。"):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^　（定義）", line):
                is_in_article_define = True
                print(f"ArticleTitle : {line}")
                replace_append(sentences,sentence)
                sentence = line
                replace_append(sentences,sentence)
                sentence = ""
            elif re.match(r"^第[一二三四五六七八九十]+条", line):
                is_in_article_define = True
                print(f"Article : {line}")
                replace_append(sentences,sentence)
                sentences.append("")
                sentence = line
                replace_append(sentences,sentence)
                sentence = ""
            elif re.match(r"^　[①②③④⑤⑥⑦⑧⑨⑩][　 ]?", line):
                print(f"Enum : '{line}'")
                replace_append(sentences,sentence)
                if make_md:
                    sentence = "- "+line
                else:
                    sentence = line
                replace_append(sentences,sentence)
                sentence = ""
            elif re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩] 　", line):
                replace_append(sentences,sentence)
                if make_md:
                    sentence = "##### "+line
                else:
                    sentence = line
                replace_append(sentences,sentence)
                sentence = ""
            elif re.match(r"^（\d+） 　.+", line):
                replace_append(sentences,sentence)
                if make_md:
                    sentence = "#### "+line
                else:
                    sentence = line
                replace_append(sentences,sentence)
                sentence = ""
            elif re.match(r"^［図表 ", line):
                is_in_zuhyou = True
            elif re.match(r"^　.+", line):
                if is_in_article_define:
                    is_in_article_define = False
                if is_in_zuhyou:
                    is_in_zuhyou = False
                replace_append(sentences,sentence)
                sentences.append("")
                sentence = line
                if line.endswith("。"):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^（注.*）", line):
                replace_append(sentences,sentence)
                if make_md:
                    sentence = "- "+line
                else:
                    sentence = line
                if line.endswith("。"):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.search(r"（注.*）", line):
                if make_md:
                    sentence += re.sub(r"(（注.*）)",r"<sup>\1</sup>",line)
                else:
                    sentence += re.sub(r"(（注.*）)","",line)
                if line.endswith("。"):
                    replace_append(sentences,sentence)
                    sentence = ""
            # 末尾に。が有るときは改行するといい感じ。
            elif line.endswith("。"):
                sentence += line
                replace_append(sentences,sentence)
                sentence = ""
            else:
                if not is_in_zuhyou:
                    sentence += line

    return sentences

if __name__ == "__main__":
    rate = 280
#    dry_run = True
    dry_run = False
    make_md = False

    in_file_name = "fuseikyousou_chikuzyo_text.json"
    with open(os.path.join(os.path.dirname(__file__), "..", "extracted_text_from_pdf", in_file_name), encoding='utf-8') as f:
        objs = json.load(f)
    all_lines = []
    for page_obj in objs["pages"]:
        all_lines += page_obj["lines"][1:]

    sentences = analyse_lines(all_lines, make_md)

    if make_md:
        with open(os.path.join(os.path.dirname(__file__), "..", "extracted_text_from_pdf", "不正競争防止法_第3章_不正競争.md"), "w", encoding='utf-8') as f:
            f.write("\n".join(sentences))
    else:
        mp3_lines = []
        for line in sentences:
            for replace_str in replace_strs:
                line = line.replace(replace_str, replace_strs[replace_str])
            mp3_lines.append(line)
        with open(os.path.join(os.path.dirname(__file__), "..", "extracted_text_from_pdf", "不正競争防止法_第3章_不正競争_mp3.txt"), "w", encoding='utf-8') as f:
            f.write("\n".join(sentences))
        
        if not dry_run:
            mp3_file_path = os.path.join(os.path.dirname(__file__), "chapter_3.mp3")
            engine = pyttsx3.init()

            with tempfile.TemporaryDirectory() as td:
                wav_file = os.path.join(td, "tmp.wav")
                engine.setProperty('rate', rate)
                engine.save_to_file('\n'.join(sentences), wav_file)
                engine.runAndWait()

                print("converting to mp3")
                audio = AudioSegment.from_wav(wav_file)
                audio.export(mp3_file_path, format="mp3")
                print("Done")

                # タグを設定
                audio = MP3(mp3_file_path, ID3=ID3)
                if rate != 200:
                    baisoku = rate/200
                    audio.tags.add(TIT2(encoding=3, text=f"第3章不正競争_第2条関係_{baisoku:1.1f}倍速"))  # 曲名
                else:
                    audio.tags.add(TIT2(encoding=3, text=f"第3章不正競争_第2条関係"))  # 曲名
                audio.tags.add(TPE1(encoding=3, text="経済産業省"))  # アーティスト
                audio.tags.add(TALB(encoding=3, text="不正競争防止法逐条解説"))  # アルバム
                audio.tags.add(TRCK(encoding=3, text="1"))            # トラック番号
                audio.save()                
                engine.stop()