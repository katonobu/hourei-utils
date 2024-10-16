import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from extract_text_from_pdf import extract_text

if __name__ == "__main__":
    pdf_file_name = "Chikujo.pdf"
    start_page = 47
    end_page   = 176
    out_file_name = "fuseikyousou_chikuzyo_text.json"

    extract_text(pdf_file_name, "\n", start_page, end_page, False, out_file_name)
