import streamlit as st
import tempfile
import openai
import pandas as pd


from utils.ocr_utils import perform_ocr  # clean_ocr_text removed as requested
from utils.parsing_utils import parse_lab_results
from utils.openai_utils import generate_explanation, generate_summary_and_suggestions
from utils.pdf_utils import export_to_pdf

# Load config
from config.config import TESSERACT_CMD

# Set Tesseract command (redundant if done in ocr_utils, but safe)
import pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
from dotenv import load_dotenv
load_dotenv()
import os

# Streamlit app setup
st.set_page_config(page_title="Medical Report Analyzer", layout="wide")
st.title("🧪 Medical Report Analyzer")

# Set OpenAI API key from Streamlit secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Upload a scanned medical report (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_details = {"filename": uploaded_file.name, "type": uploaded_file.type}
    st.write("Uploaded File:", file_details)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.image(tmp_path, caption="Uploaded Image", use_container_width=True)

    # Use raw OCR text directly, no cleaning step
    ocr_text = perform_ocr(tmp_path)

    if ocr_text:
        st.text_area("📄 Extracted Text", ocr_text, height=300)
    else:
        st.warning("No text found in the image. Try uploading a clearer image.")

    if st.button("📊 Structure Lab Results"):
        with st.spinner("Structuring extracted data..."):
            structured_data = parse_lab_results(ocr_text)

            # Convert list to DataFrame if needed
            if isinstance(structured_data, list):
                structured_data = pd.DataFrame(structured_data)

            # Debug: print actual column names to help fix KeyError
            st.write("Columns in structured_data:", structured_data.columns.tolist())

            if not structured_data.empty:
                st.success("Structured data extracted:")
                st.dataframe(structured_data)
                st.session_state.structured_data = structured_data
            else:
                st.warning("Could not find structured test results in the text.")

    if st.button("💬 Generate Explanations"):
        if 'structured_data' in st.session_state:
            structured_data = st.session_state.structured_data
            with st.spinner("Generating explanations..."):
                explanation_dict = {}
                # Update keys below if your columns differ, use printed column names as guide
                for _, row in structured_data.iterrows():
                    explanation = generate_explanation(
                        test_name=row.get('Test Name', row.get('Test', 'Unknown Test')),
                        value=row.get('Result', row.get('Value', '')),
                        unit=row.get('Unit', ''),
                        normal_range=row.get('Reference Range', row.get('Normal Range', ''))
                    )
                    explanation_dict[row.get('Test Name', row.get('Test', 'Unknown Test'))] = explanation
            st.session_state.explanation_dict = explanation_dict

            for _, row in structured_data.iterrows():
                test_name = row.get('Test Name', row.get('Test', 'Unknown Test'))
                with st.expander(f"🧾 {test_name}"):
                    st.markdown(f"**Result:** {row.get('Result', row.get('Value', ''))} {row.get('Unit', '')} (Normal: {row.get('Reference Range', row.get('Normal Range', ''))})")
                    st.markdown(f"**Category:** {row.get('Category', row.get('Flag', ''))}")
                    st.markdown(f"**Explanation:**\n\n{explanation_dict.get(test_name, 'No explanation available.')}")
        else:
            st.warning("Please structure the lab results first.")

    if st.button("📝 Generate Health Summary & Suggestions"):
        if 'structured_data' in st.session_state:
            structured_data = st.session_state.structured_data
            with st.spinner("Generating health summary..."):
                summary_text, abnormal_tests = generate_summary_and_suggestions(structured_data)
                st.markdown("### Overall Health Summary & Suggestions")
                st.write(summary_text)
                st.session_state.summary_text = summary_text
        else:
            st.warning("Please structure the lab results first.")

    if st.button("📥 Export Summary as PDF"):
        if 'structured_data' in st.session_state and 'explanation_dict' in st.session_state and 'summary_text' in st.session_state:
            structured_data = st.session_state.structured_data
            explanation_dict = st.session_state.explanation_dict
            summary_text = st.session_state.summary_text
            filename = "medical_report_summary.pdf"
            with st.spinner("Generating PDF..."):
                export_to_pdf(structured_data, explanation_dict, summary_text, filename=filename)
            with open(filename, "rb") as f:
                st.download_button(label="Download PDF", data=f, file_name=filename, mime="application/pdf")
        else:
            st.warning("Please generate explanations and health summary first.")

else:
    st.info("Upload a scanned medical report image to start.")
