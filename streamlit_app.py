import streamlit as st
from PIL import Image
import fitz  # PyMuPDF for PDF rendering
from io import BytesIO

# 1. Lazily load the Document-QA pipeline to avoid Streamlit startup errors
@st.cache_resource
def load_doc_qa():
    from transformers import pipeline
    return pipeline(
        "document-question-answering",
        model="impira/layoutlm-document-qa",
        tokenizer="impira/layoutlm-document-qa",
        device=0,                      # or -1 on CPU-only hosts
        aggregation_strategy="simple"  # stitch tokens into full spans
    )

doc_qa = None  # will be initialized on first use

def render_pdf_to_image(uploaded_file) -> Image.Image:
    """Render the first page of a PDF into a PIL image via PyMuPDF."""
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

def extract_fields_from_image(img: Image.Image, threshold=0.4) -> dict:
    """Extract name, net_pay, and date using top_k QA and explicit prompts."""
    global doc_qa
    if doc_qa is None:
        doc_qa = load_doc_qa()

    questions = {
        "name": (
            "What is the employee’s full name? "
            "Look next to the label 'Employee', 'Name' or 'Staff name'."
        ),
        "net_pay": (
            "What is the net pay (including the £ symbol) as shown on this payslip?"
        ),
        "date": (
            "What is the pay date? Please reply in DD MMM YYYY format."
        )
    }

    answers = {}
    for field, q in questions.items():
        # get top 5 spans
        raw = doc_qa(image=img, question=q, top_k=5)
        candidates = raw if isinstance(raw, list) else [raw]

        # pick highest-confidence span
        best = max(candidates, key=lambda x: x.get("score", 0))
        score = best.get("score", 0)
        text  = best.get("answer", "").strip()

        # optional: display debug info
        st.write(f"**Debug [{field}]** → '{text}'  _(score={score:.2f})_")

        # fallback marker if low confidence
        if score < threshold:
            text += "  ← low confidence"

        answers[field] = text

    return answers

# --- Streamlit UI ---
st.title("Payslip Extractor MVP")

uploaded_file = st.file_uploader("Upload your UK payslip", type=["pdf","png","jpg","jpeg"])
if uploaded_file:
    suffix = uploaded_file.name.rsplit(".", 1)[-1].lower()

    # Render PDF or load image
    if suffix == "pdf":
        img = render_pdf_to_image(uploaded_file)
    else:
        img = Image.open(uploaded_file)

    st.image(img, caption="Payslip preview", use_column_width=True)

    # Extract and show the fields
    result = extract_fields_from_image(img)
    st.json(result)
