import streamlit as st
import io, pathlib, re
import fitz                    # PyMuPDF (imported as “fitz”)
from PIL import Image
import pytesseract

# ---------- tiny helper -----------------------------------------------------
def extract_fields(text: str) -> dict:
    patterns = {
        "name":    r"(?:Employee\s+)?Name\s*[:\-]?\s*([A-Z][A-Za-z\-\s']+)",
        "net_pay": r"(?:Net\s+(?:Pay|Payment))\s*[:\-]?\s*£?\s*([\d,]+\.\d{2})",
        "date":    r"(?:Pay\s*)?Date\s*[:\-]?\s*([0-3]?\d\s*[A-Za-z]{3,9}\s*\d{4})",
    }
    return {k: (m.group(1) if (m := re.search(p, text, re.I)) else None)
            for k, p in patterns.items()}
# ---------------------------------------------------------------------------

st.title("Payslip Extractor MVP")

uploaded = st.file_uploader(
    "Upload a UK payslip (PDF or image)",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded:
    suffix = pathlib.Path(uploaded.name).suffix.lower()

    # --- turn whatever we got into a Pillow Image --------------------------
    if suffix == ".pdf":
        pdf_bytes = uploaded.read()                        # read once
        page      = fitz.open(stream=pdf_bytes, filetype="pdf")[0]
        pix       = page.get_pixmap(dpi=300)
        img       = Image.open(io.BytesIO(pix.tobytes()))
    else:
        img = Image.open(uploaded)                         # already file-like
    # -----------------------------------------------------------------------

    st.image(img, caption="Payslip preview", use_column_width=True)

    ocr_text = pytesseract.image_to_string(img)
    st.json(extract_fields(ocr_text))
