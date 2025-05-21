import streamlit as st
from transformers import pipeline
from pdf2image import convert_from_path
from PIL import Image
from io import BytesIO

# Load the LayoutLM-based Document QA model
@st.cache_resource
def load_doc_qa():
    return pipeline(
        "document-question-answering",
        model="impira/layoutlm-document-qa",
        tokenizer="impira/layoutlm-document-qa",
        device=0  # or -1 if you don’t have GPU
    )

def extract_fields_from_image(img: Image.Image) -> dict:
    questions = {
        "name":    "What is the employee’s name?",
        "net_pay": "What is the net pay?",
        "date":    "What is the pay date?"
    }
    answers = {}
    for key, q in questions.items():
        out = doc_qa(image=img, question=q)
        answers[key] = out.get("answer", "").strip()
    return answers

doc_qa = load_doc_qa()

st.title("Payslip Extractor MVP")

uploaded_file = st.file_uploader("Upload your UK payslip", type=["pdf","png","jpg","jpeg"])
if uploaded_file:
    # convert PDF → PIL image if needed
    suffix = uploaded_file.name.lower().split(".")[-1]
    if suffix == "pdf":
        pages = convert_from_path(BytesIO(uploaded_file.read()), dpi=300, first_page=1, last_page=1)
        img = pages[0]
    else:
        img = Image.open(uploaded_file)

    st.image(img, caption="Payslip preview", use_column_width=True)
    result = extract_fields_from_image(img)
    st.json(result)
