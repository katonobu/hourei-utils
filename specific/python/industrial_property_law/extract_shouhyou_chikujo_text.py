import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from extract_text_from_pdf import extract_text

if __name__ == "__main__":
    pdf_file_name = "all.pdf"
    start_page = 1591
    end_page   = 1967
    out_file_name = "shouhyou_chikujo_text.json"

    extract_text(pdf_file_name, "\n\n", start_page, end_page, True, out_file_name)
