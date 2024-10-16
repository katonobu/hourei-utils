import os
import json
import datetime
import platform
import pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

page_separator = ""

def gettext(pdfname, start=0, end=0, detect_vertical = False):
    # PDFファイル名が未指定の場合は、空文字列を返して終了
    if (pdfname == ''):
        return ''
    else:
        # 処理するPDFファイルを開く/開けなければ
        try:
            fp = open(pdfname, 'rb')
        except:
            return ''

    # リソースマネージャインスタンス
    rsrcmgr = PDFResourceManager()
    # 出力先インスタンス
    outfp = StringIO()
    # パラメータインスタンス
    laparams = LAParams()
    # 縦書き文字を横並びで出力する
    laparams.detect_vertical = detect_vertical
    # デバイスの初期化
    device = TextConverter(rsrcmgr, outfp, laparams=laparams)
    # テキスト抽出インタプリタインスタンス
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # 対象ページを読み、テキスト抽出する。（maxpages：0は全ページ）
    for idx, page in enumerate(PDFPage.get_pages(fp, pagenos=None, maxpages=0, password=None,\
            caching=True, check_extractable=True)):
        if idx < start - 1:
            continue
        if 0 < end and end - 1 <= idx:
            break
        interpreter.process_page(page)
        if (idx+1) % 100 == 0:
            print("O",flush=True)
        if (idx+1) % 10 == 0:
            print("O",end="", flush=True)
        else:
            print(".",end="", flush=True)
    print("!", flush=True)

    #取得したテキストをすべて読みだす
    ret = outfp.getvalue()
    # 後始末をしておく    
    fp.close()
    device.close()
    outfp.close()

    return ret

def extract_text(pdf_filename, line_separator, start_page, end_page, detect_vertical, output_file_name):
    print(f"pdfminer version : {pdfminer.__version__}")
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_file_base = os.path.join(base_path, "pdf")
    pdf_file_path = os.path.join(pdf_file_base, pdf_filename)
    out_file_base = os.path.join(base_path, "extracted_text_from_pdf")
    out_file_path = os.path.join(out_file_base, output_file_name)

    
    result_obj = {
        'pdf_miner_version':pdfminer.__version__,
        'os':platform.platform(),
        'exec_at':datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    }
    page_texts = []
    pages = gettext(pdf_file_path, start_page, end_page, detect_vertical).split(page_separator)
    if len(pages) == 1 and pages[0] == "":
        print(f'Error: specified pdf file {pdf_file_path} not found')
    page_number = start_page
    if start_page == 0:
        page_number = 1
    for page_lines in pages:
        lines = [line for line in page_lines.split(line_separator)]
        if 0 < len(lines):
            page_texts.append({'page_number':page_number, 'lines':lines.copy()})
        page_number += 1

    result_obj.update({
        'pages':page_texts
    })
    with open(os.path.join(out_file_path), "w", encoding='utf-8') as f:
        json.dump(result_obj,f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    pdf_file_name = "all.pdf"
    out_file_name = "sample.json"
    start_page = 83
    end_page   = 85

    extract_text(pdf_file_name, "\n\n", start_page, end_page, True, out_file_name)
