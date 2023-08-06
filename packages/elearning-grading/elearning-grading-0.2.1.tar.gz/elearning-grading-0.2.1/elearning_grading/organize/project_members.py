import argparse
import os

import docx
import pdfplumber

from elearning_grading.utilities.el_utils import get_net_ids


def get_pdf_txt(file_path):
    # creating a pdf file object
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            text.append(page_text)
    return "\n".join(text)


def get_word_txt(file_path):
    doc = docx.Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)


def collect_ids(root_dir):
    for file in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file)
        try:
            if file_path.endswith(".pdf"):
                file_text = get_pdf_txt(file_path)
            elif file_path.endswith(".docx"):
                file_text = get_word_txt(file_path)
            else:
                print(f"UNKNOWN FILE FORMAT: {file_path}")
                continue
        except Exception as e:
            print(f"ERROR READING {file_path}: {e}")
            continue
        file_ids = get_net_ids(file_text)
        print(f"{file}:")
        for netid in file_ids:
            print(f"  {netid}")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_path",
        help="filepath to folder of project report files, in which project pdf or docx files contain team netids.",
    )
    args = parser.parse_args()
    collect_ids(args.input_path)


if __name__ == "__main__":
    main()
