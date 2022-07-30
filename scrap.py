#!/usr/bin/env python

from fileinput import filename
from io import StringIO
import logging
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

output_string = StringIO()

logging.getLogger().setLevel(logging.INFO)

extracted_text = ""

credit_card_statement_filename = "20211503.pdf"

def isexpenditureline(candidate_line):
    return "SU PAGO EN PESOS" in candidate_line or "21 Marzo" in candidate_line


def process_lines(expenditure_line):
    lines = expenditure_line.split("\n")
    stripped = []
    for line in lines:
        stripped_line = line.strip()
        if len(stripped_line) > 3 and \
            (stripped_line[-3] == "," or stripped_line[-1] == "-") \
            and "SU PAGO EN PESOS" not in stripped_line:
            stripped.append(stripped_line)
    return stripped
    


with open(credit_card_statement_filename, 'rb') as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    lines = []
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        layout = device.get_result()
        # Out of the many LT objects within layout, we are interested in LTTextBox and LTTextLine
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                raw_text = lt_obj.get_text()
                if isexpenditureline(raw_text):
                    lines.extend(process_lines(raw_text))

    for line in lines:
        print("Gasto: " + line)
    print("Total gastos: " + str(len(lines)))