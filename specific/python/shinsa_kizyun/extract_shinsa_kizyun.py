import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from extract_text_from_pdf import extract_text

if __name__ == "__main__":
    pdf_file_name = "tukujitu_kijun.pdf"
    start_page = 0
    end_page   = 0
    out_file_name = "shinsa_kizyun_text.json"

    extract_text(pdf_file_name, "\n\n", start_page, end_page, False, out_file_name)
