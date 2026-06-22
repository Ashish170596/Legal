import streamlit as st
import google.genai as genai
from pypdf import PdfReader
import os

# Configure the Streamlit page layout
st.set_page_config(page_title="Office Legal Judgment Summarizer", layout="wide")
st.title("⚖️ Automated Legal Judgment & Case Analyzer")
st.write("Upload any legal document or judgment PDF for an automated, structural breakdown.")

# ==========================================
# 🔒 CLOUD SECURITY SETUP
# This safely pulls your key from Streamlit Cloud's private settings
# so it is never exposed in your public code.
# ==========================================
try:
    OFFICE_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    OFFICE_API_KEY = None
# ==========================================

def extract_text_from_pdf(pdf_file):
    """Extracts text content from the uploaded PDF file."""
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# Main file uploader
uploaded_file = st.file_uploader("Upload Judgment or Case File PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Reading PDF text..."):
        judgment_text = extract_text_from_pdf(uploaded_file)
    
    if not judgment_text.strip():
        st.error("Could not extract text from this PDF. It might be a scanned image rather than a text PDF.")
    else:
        st.success(f"Successfully loaded document ({len(judgment_text)} characters).")
        
        # Trigger analysis on button click
        if st.button("Analyze Document Now"):
            
            if not OFFICE_API_KEY:
                st.error("Setup Error: The API key is missing from the Streamlit Secrets dashboard. Please add it in the app's advanced settings.")
            else:
                with st.spinner("Analyzing legal arguments and rulings..."):
                    try:
                        # Initialize the client using the secured office key
                        client = genai.Client(api_key=OFFICE_API_KEY)
                        
                        # Comprehensive prompt to handle both judgments and case files
                        prompt = f"""
                        You are an expert appellate lawyer and senior legal researcher. Analyze the following legal text (which may be a court judgment or a case file) and extract the critical parameters structurally.

                        Rules:
                        - Maintain absolute factual accuracy. Do not hallucinate case names, numbers, or provisions.
                        - If a section is not applicable or not found in the text, explicitly state "Not mentioned in the document".

                        Provide the output using clean Markdown formatting under these exact headers:

                        ## 🏛️ Case Overview
                        - **Case Name / Title:** [Extract exact parties, e.g., Appellant vs Respondent]
                        - **Case Number / Citation:** [Extract registration number, citation, or dynamic ID]
                        - **Court / Authority:** [Name of the court or authority that delivered this document]

                        ## 🔍 Legal Issues & Controversies
                        ### Primary Issues
                        [Enumerate the exact legal questions, disputes, or controversies that need to be decided]

                        ## 🗣️ Arguments Raised
                        ### 1. Arguments of the Appellants / Petitioners / Complainants
                        [Detail the major legal grounds, statutory provisions relied upon, and core contentions raised]

                        ### 2. Arguments of the Respondents / Defendants / Opposition
                        [Detail the written statements, rebuttals, counter-arguments, and defenses raised]

                        ## ⚖️ Judicial Analysis & Application
                        [Detail how the court or authority systematically analyzed the legal concepts, doctrines, or provisions, and how it applied them specifically to the facts of this case]

                        ## 📌 Core Legal Principle (Ratio Decidendi)
                        [State the exact binding legal rationale or principle of law established by this decision. Leave blank if it is a running case file rather than a final judgment]

                        ## 🏁 Final Order / Status
                        [What was the final decision or current status? State the operative order clearly, e.g., allowed, dismissed, pending next hearing]

                        ---
                        **Document Content:**
                        {judgment_text}
                        """
                        
                        # Fast, high-capacity model that runs smoothly and instantly
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                        )
                        
                        st.markdown("---")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")
else:
    st.info("Ready for use. Please drag and drop a PDF file above to begin.")