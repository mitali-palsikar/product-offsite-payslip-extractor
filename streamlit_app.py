import streamlit as st
import pymupdf
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
st.title("Payslip Extractor MVP")
f = st.file_uploader("Upload your UK payslip", type=["pdf","png","jpg","jpeg"])
def extract(text):
    import re
    m = lambda p: (re.search(p,text,re.I) or [None, None])[1]
    return dict(name=m(r"Name\s*[:\-]?\s*([A-Z][A-Za-z\-\s']+)"),
                net_pay=m(r"Net\s*(?:Pay|Payment)\s*[:\-]?\s*£?\s*([\d,]+\.\d{2})"),
                date=m(r"Date\s*[:\-]?\s*([0-3]?\d\s*[A-Za-z]{3,9}\s*\d{4})"))
if f:   
    if pathlib.Path(f.name).suffix==".pdf":
        page = fitz.open(stream=f.read(),filetype="pdf")[0]
        img = Image.frombytes("RGB",[page.rect.width,page.rect.height],page.get_pixmap(dpi=300).samples)
    else:
        img = Image.open(f)
    st.image(img, caption="Payslip preview", use_column_width=True)
    st.json(extract(pytesseract.image_to_string(img)))
PY
