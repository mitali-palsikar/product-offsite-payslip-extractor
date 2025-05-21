# ⬇️ Colab Cell #1 – one-shot install (~20 s)
!apt-get -qq install tesseract-ocr libtesseract-dev
!pip install --quiet pytesseract pillow pdf2image fitz

# ⬇️ Colab Cell #2 – imports & helpers
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

# ⬇️ Colab Cell #3 – upload, OCR, parse
up = files.upload(); f = next(iter(up))
if pathlib.Path(f).suffix.lower() == ".pdf":
    img = pdf_page_to_image(f)
else:
    img = Image.open(f)

text = pytesseract.image_to_string(img)
print(text[:800])               # peek if you’re curious
print("\nEXTRACTED:", extract_fields(text))
