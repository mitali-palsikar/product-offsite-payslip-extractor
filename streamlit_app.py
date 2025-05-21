from transformers import pipeline
from PIL import Image
import fitz
from io import BytesIO

# 1. Load the Document-QA pipeline with simple aggregation
doc_qa = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa",
    tokenizer="impira/layoutlm-document-qa",
    device=0,                        # set to -1 if no GPU
    aggregation_strategy="simple"   # group tokens into contiguous spans
)

def render_pdf_to_image(uploaded_file) -> Image.Image:
    """Render first page of a PDF into a PIL image via PyMuPDF."""
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

def extract_fields_from_image(img: Image.Image, threshold=0.4) -> dict:
    """Extract name, net_pay, date using top_k QA and explicit questions."""
    questions = {
        "name":    (
            "What is the employee’s full name? "
            "Look next to the label 'Employee', 'Name' or 'Staff name'."
        ),
        "net_pay": (
            "What is the net pay (including the £ symbol) as shown on this payslip?"
        ),
        "date":    (
            "What is the pay date? Please reply in DD MMM YYYY format."
        )
    }
    answers = {}
    for field, q in questions.items():
        # ask for top 5 spans
        raw = doc_qa(image=img, question=q, top_k=5)
        # normalize to a list
        candidates = raw if isinstance(raw, list) else [raw]

        # pick the highest-score candidate
        best = max(candidates, key=lambda x: x.get("score", 0))
        score = best.get("score", 0)
        text  = best.get("answer", "").strip()

        # debug print (or st.write in Streamlit)
        print(f"[{field}] → '{text}' (score={score:.2f})")

        # thresholding / fallback
        if score < threshold:
            # if you want, you can trigger another strategy here
            text += "  <-- low confidence, consider fallback"
        answers[field] = text

    return answers

# Example usage:
# ----------------
# uploaded_file = ...  # from Streamlit file_uploader or Colab files.upload()
# suffix = uploaded_file.name.split(".")[-1].lower()
# img = render_pdf_to_image(uploaded_file) if suffix == "pdf" else Image.open(uploaded_file)
# extracted = extract_fields_from_image(img)
# print(extracted)
