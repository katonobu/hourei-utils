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
import cid_trans

#sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','..','generic','lib'))
#from replace_obj import replace_strs, replace_res

replace_strs = {
    # 特定の漢字の誤読にまつわるもの
    # 願
    '本願':'ほんがん', # ほんねがい
    '先願':'せんがん', # せんねがい

    # 人
    '出願人':'しゅつがんにん', # しゅつがんひと

    # 書
    '明細書':'めいさいしょ', # めいさいか
    '上申書':'じょうしんしょ', # じょうしんか
    '柱書':'はしらがき', # はしらか
    '補正書':'ほせいしょ', # ほせいか
    'ただし書':'ただしがき', # ただしか

    # 特許系に出てきやすい用語
    '減縮':'げんしゅく', # げんちじみ
    '前置':'ぜんち', # まえおき
    '進歩性':'しんぽせい', # すすむほせいい

    # 法律一般で出てきやすい用語
    '単一性':'たんいつせい', # たんいちせい
    '適否':'てきひ', # てきいな
    '過誤':'かご', # かあやまり

    # 一般用語
    '自車':'じしゃ', # じぐるま
}

replace_numbers = {
    '(i)':'[1]',
    '(ii)':'[2]',
    '(iii)':'[3]',
    '(iv)':'[4]',
    '(v)':'[5]',
    '(vi)':'[6]',
    '(vii)':'[7]',
    '(viii)':'[8]',
    '(ix)':'[9]',
    '(x)':'[10]',
    '(xi)':'[11]',
    '(i-':'(1-',
    '(ii-':'(2-',

}

def replace_append(append_to, line):
    # 読み上げ対応変換処理
    pass
    if type(line) is str:
        for replace_str in replace_strs:
            line = line.replace(replace_str, replace_strs[replace_str])
        for replace_str in replace_numbers:
            line = line.replace(replace_str, replace_numbers[replace_str])
        line = re.sub(r"\((\d+-\d+)\)",r"[\1]",line)
        line = re.sub("^ +","",line)
        if 0 < len(line):
            append_to.append(line)
    else:
        print(line)

if __name__ == "__main__":
    dry_run = True
    dry_run = False

    rate = 280

    in_file_name = "shinsa_kizyun_text.json"
    with open(os.path.join(os.path.dirname(__file__), "..", "extracted_text_from_pdf", in_file_name), encoding='utf-8') as f:
        objs = json.load(f)
    sentences = []        
    sentence = ""
    all_lines = []
    for page_obj in objs["pages"]:
        if page_obj["page_number"] < 17:
            continue
        if 68 < page_obj["page_number"]:
            continue
        all_lines += page_obj["lines"]

    for lines in all_lines:
        for line in lines.split("\n"):
            line = cid_trans.cid_trans(line)
            line = re.sub(r"\(\d{4}\.\d{1,2}\)","",line)
            if re.match(r"^第.*?部  第\d+章  第\d+節 ", line):
                # ページ先頭の表示行
                continue
            if re.match(r"^- \d+ - $", line):
                # ページ下部のページ表示行
                continue
            if re.match(r"^ *$", line):
                # 空行はスキップ
                continue

            if "審査官は、まず審査の対象となっている特" in line:
                pass

            # 文章構造
            if re.match(r"^第 \d+ 章  ", line):
                print(line)
                replace_append(sentences,sentence)
                sentences.append("")
                sentence = line
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^第 \d+ 節  ", line):
                print(line)
                replace_append(sentences,sentence)
                sentences.append("")
                sentence = line
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^\d+\. ", line):
                print(line)
                replace_append(sentences,sentence)
                sentences.append("")
                sentence = line
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^\d+\.\d+ ", line):
                print(line)
                replace_append(sentences,sentence)
                sentences.append("")
                sentence = line
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^\d+\.\d+\.\d+ [^(]", line):
                print(line)
                replace_append(sentences,sentence)
                sentences.append("")
                sentence = line
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^\(\d+\)", line):
                print(line)
                replace_append(sentences,sentence)
                sentence = line
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^ *\([ivx]+\)", line):
                line = re.sub(r"^ *\(([ivx]+)\) *",r"(\1)  ",line)
                print(line)
                replace_append(sentences,sentence)
                sentence = line
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            elif re.match(r"^ *[abcdefg]  ", line):
                line = re.sub(r"^ *([abcdefg]) +",r"(\1)  ",line)
                print(line)
                replace_append(sentences,sentence)
                sentence = line
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            # 例：始まりの行は：で改行
            elif re.match(r"^例 ?\d+：", line):
                replace_append(sentences,sentence)
                splitted = line.split("：")
                replace_append(sentences,splitted[0].replace(" ",""))
                sentence = "：".join(splitted[1:])
                if line.endswith(" "):
                    replace_append(sentences,sentence)
                    sentence = ""
            # 末尾にスペースが有るときは改行するといい感じ。
            elif line.endswith(" "):
                sentence += line
                replace_append(sentences,sentence)
                sentence = ""
            else:
                sentence += line

    with open(os.path.join(os.path.dirname(__file__), "..", "extracted_text_from_pdf", "part_1.txt"), "w", encoding='utf-8') as f:
        f.write("\n".join(sentences))

    if not dry_run:
        mp3_file_path = os.path.join(os.path.dirname(__file__), "..", "shinsa_kizyun", "part_1.mp3")
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
                audio.tags.add(TIT2(encoding=3, text=f"第1節 {baisoku:1.1f}倍速"))  # 曲名
            else:
                audio.tags.add(TIT2(encoding=3, text=f"第1節"))  # 曲名
            audio.tags.add(TPE1(encoding=3, text="特許庁"))  # アーティスト
            audio.tags.add(TALB(encoding=3, text="特許審査基準"))  # アルバム
            audio.tags.add(TRCK(encoding=3, text="1"))            # トラック番号
            audio.save()                
            engine.stop()