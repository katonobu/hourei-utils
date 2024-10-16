import os
import tempfile
try:
    import pyttsx3
except ModuleNotFoundError as e:
    pyttsx3 = None

from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TCON, TYER    

class MakeMp3():
    def __init__(self, base_dir, output_id_filter_str = "", del_id_str = "Mp-Ch_", dry_run = False):
        self.base_dir = base_dir
        self.init(output_id_filter_str, del_id_str, dry_run)

    def init(self, output_id_filter_str = "", del_id_str = "Mp-Ch_", dry_run = False):
        self.is_skip = False
        self.output_id_filter_str = output_id_filter_str
        self.del_id_str = del_id_str
        self.dir_path = None
        self.track_count = 1
        self.dry_run = pyttsx3 is None or dry_run
        if self.dry_run == False:
            self.engine = pyttsx3.init()
        else:
            self.engine = None
            print("MakeMp3() is initialized with dry_ryn mode.")


    def mp3_mkdir(self, id_str, dirs):
#        print(len(self.output_id_filter_str), id_str.replace(self.del_id_str,"") in self.output_id_filter_str)
        if 0 == len(self.output_id_filter_str) or id_str.replace(self.del_id_str,"") in self.output_id_filter_str:
            self.is_skip = False
            print(f'Making dir for {id_str}')
            self.dir_path = os.path.join(self.base_dir, '_'.join(dirs))
            os.makedirs(self.dir_path, exist_ok=True)
        else:
            self.is_skip = True
            print(f'Skip making dir for {id_str}')

    def mp3_tts(self, file_name, texts, title):
        if self.is_skip == False:
            mp3_file_path = os.path.join(self.dir_path, file_name)
            if self.dry_run == False:
                with tempfile.TemporaryDirectory() as td:
                    wav_file = os.path.join(td, "tmp.wav")
                    self.engine.save_to_file('\n'.join(texts), wav_file)
                    print(f'  Generating {title}')
                    self.engine.runAndWait()

                    audio = AudioSegment.from_wav(wav_file)
                    audio.export(mp3_file_path, format="mp3")

                    # タグを設定
                    audio = MP3(mp3_file_path, ID3=ID3)
                    audio.tags.add(TIT2(encoding=3, text=title))  # 曲名
                    audio.tags.add(TPE1(encoding=3, text="法令読み上げ"))  # アーティスト
                    audio.tags.add(TALB(encoding=3, text=os.path.basename(self.dir_path)))  # アルバム
                    audio.tags.add(TRCK(encoding=3, text=f"{self.track_count}"))            # トラック番号
                    audio.save()                
                    self.track_count += 1
            else:
                with open(mp3_file_path.replace(".mp3",".txt"), "w", encoding='utf-8') as f:
                    f.write('\n'.join(texts))
                print(f'  Generating {title}(dry_run), {len(texts)} lines')
        else:
            print(f"  Skipping generating {title}")
    
    def mp3_playlist(self, playlist_info):
        if self.is_skip == False:
            print(f'Making playlist')
            dir_name = os.path.basename(self.dir_path)
            play_list_path = os.path.join(self.dir_path, f"{dir_name}.m3u8")
            with open(play_list_path, "w", encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                for info in playlist_info:
                    f.write(f'\n#EXTINF:-1, {dir_name} - {info["title"]}\n')
        else:
            print(f'Skip making playlist')

    def finish(self):
        print("Finish MakeMp3().")
        if self.dry_run == False:
            self.engine.stop()
            self.engine = None


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__),"mp3")
    mk_mp3 = MakeMp3(base_dir)