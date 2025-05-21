import streamlit as st
from transformers import pipeline
from PIL import Image
import fitz
from io import BytesIO

@st.cache_resource
def load_doc_qa():
    return pipeline(
        "document-question-answering",
        model="impira/layoutlm-document-qa",
        tokenizer="impira/layoutlm-document-qa",
        device=0  # or -1 on CPU
    )

doc_qa = load_doc_qa()

def extract_fields_from_image(img: Image.Image) -> dict:
    questions = {
        "name":    "What is the employee’s name?",
        "net_pay": "What is the net pay?",
        "date":    "What is the pay date?"
    }
    answers = {}
    for field, question in questions.items():
        out = doc_qa(image=img, question=question)
        # DEBUG: show raw output in your Streamlit app
        st.write(f"Debug `{field}` output:", out)

        # Normalize to a single dict
        if isinstance(out, list):
            out = out[0] if out else {}
        if not isinstance(out, dict):
            out = {}

        # Safely grab the answer
        ans = out.get("answer", "")
        answers[field] = ans.strip()
    return answers

st.title("Payslip Extractor MVP")

uploaded_file = st.file_uploader("Upload your UK payslip", type=["pdf","png","jpg","jpeg"])
if uploaded_file:
    suffix = uploaded_file.name.lower().split(".")[-1]
    if suffix == "pdf":
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    else:
        img = Image.open(uploaded_file)

    st.image(img, caption="Payslip preview", use_column_width=True)
    result = extract_fields_from_image(img)
    st.json(result)
