import streamlit as st
import pathlib, io
# (plus your extract_fields() helper defined above)

import pytesseract, re, fitz, pathlib, io, base64
from pdf2image import convert_from_path
from PIL import Image
from google.colab import files

def pdf_page_to_image(pdf_path):
    images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
    return images[0]

def extract_fields(text):
    patterns = {
      "name"   : r"(?:Employee\s+)?Name\s*[:\-]?\s*([A-Z][A-Za-z\-\s']+)",
      "net_pay": r"(?:Net\s+(?:Pay|Payment))\s*[:\-]?\s*£?\s*([\d,]+\.\d{2})",
      "date"   : r"(?:Pay\s*)?Date\s*[:\-]?\s*([0-3]?\d\s*[A-Za-z]{3,9}\s*\d{4})"
    }
    return {k:(m.group(1) if (m:=re.search(v,text,re.I)) else None)
            for k,v in patterns.items()}

st.title("Payslip Extractor MVP")

uploaded = st.file_uploader(
    "Upload your UK payslip",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded:
    suffix = pathlib.Path(uploaded.name).suffix.lower()

    if suffix == ".pdf":
        pdf_bytes = uploaded.read()                # read once
        page = fitz.open(stream=pdf_bytes, filetype="pdf")[0]
        pix  = page.get_pixmap(dpi=300)
        img  = Image.open(io.BytesIO(pix.tobytes()))  # Pillow needs a file-like obj
    else:
        img = Image.open(uploaded)                 # uploaded is file-like already

    st.image(img, caption="Payslip preview", use_column_width=True)

    text = pytesseract.image_to_string(img)
    st.json(extract_fields(text))
