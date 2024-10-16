# hourei-utils
法令関係ユーティリティ

## 課題
### generic\lib\HoureiXml.py
- subsectionに対応したが、id文字列が正しく生成されていない。
  - "359AC0000000086", # 電気通信事業者法
- divisionに対応できていない。
  - "129AC0000000089", # 民法
  - "325AC0000000131", # 電波法
- 条文中のテーブル未対応。

### generic\lib\MakeTssTextChDirAtFile.py
- 条なし項始まりだと何も生成されない
  - "503M60000008044", # 有明海及び八代海等を再生するための特別措置に関する法律第十一条第一項に規定する特定事業を定める省令
- chapterなしの条始まりだと実行時エラー
  - "411AC0000000127" # 国旗及び国歌に関する法律

## Appの各ファイル
- `get_all_hourei_xml.py`
  - 法令APIを使って全法令の一覧を取得し、各法令の法令IDを用いてデータを取得、parseし実行時エラーが発生しないことを確認する。
- `hourei_to_mp3.py`
  - 指定された法令IDを読み上げ、mp3ファイルを生成する。

## Libの各ファイル
- `generic\lib\HoureiXml.py`
  - 法令APIで得られるxmlを解析する基底クラス
  - get_xml_by_hourei_id()
    - インスタンス時の引数で指定されたパスの下に、get_xml_by_hourei_id()で指定された法令id文字列のディレクトリを掘り、
    - 法令id.xmlファイルがあれば、それを使う、なければ法令APIでxmlを取ってきてファイルに保存する。
    - xml文字列を返す。
  - parse_xml_tree()
    - 引数で指定されたxpathを起点として解析を開始する。
    - 現時点では、引数は"./ApplData/LawFullText"を想定。
    - 指定パス以下を再帰的に解析し、user_*_handlerを呼び出す。
    - HoureiXmlのsub classでuser_*_handlerをオーバーライドすることで各種処理を実現できる。

- `generic\lib\MakeIdTitles.py`
  - HoureiXml.pyのサブクラスの実装例
  - idとタイトルを抽出

- `generic\lib\MakeTssTextChDirAtFile.py`
  - 章単位でディレクトリを生成し、条単位で読み上げmp3ファイルを生成するHoureiXmlクラスを継承したクラス。

- `generic\lib\MakeMp3.py`
  - MakeTssTextChDirAtFile.pyから呼ばれる。
    - 新たな章毎に呼び出されるディレクトリ生成処理
    - 条が終了する毎に呼ばれる、tts/mp3ファイル生成/id3タグ生成
    - 章が終了する毎に呼ばれるプレイリスト生成処理

- `replace_obj.pyreplace_obj.py`
  - ttsの読み方がアレな単語の置換用テーブル。

