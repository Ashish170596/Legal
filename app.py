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
                        You are an expert legal annotator and senior counsel specializing in Indian civil, commercial, and matrimonial jurisprudence. Your task is to extract an exhaustive, highly detailed, and professionally rigorous analysis of the provided judgment. 

Do not use shallow summaries or brief one-liners. Use comprehensive paragraphs and structured, deep legal prose fit for a practicing advocate's brief.

Structure your analysis exactly into the following strict sections:

### 1. CASE OVERVIEW
* **Full Case Title/Style:** Include all parties, structural alignments, and cross-suits.
* **Citation & Case Numbers:** Complete official citations and application numbers.
* **Court & Bench:** Exact forum, jurisdiction, and the name of the Hon'ble Judge(s).
* **Date of Judgment/Order:** Full date.

### 2. COMPREHENSIVE FACTS OF THE CASE (Detailed Narrative)
* Provide an exhaustive background of the dispute. Do not summarize this in bullets; write a thorough factual narrative.
* **Commercial/Matrimonial Context:** Detail the nature of the parties' businesses or relationships, prior history, and the exact subject matter of the dispute (e.g., specific trademarks, packaging elements, properties, or matrimonial history).
* **Genesis of the Dispute:** Explain exactly how, when, and why the cause of action arose. Detail the specific actions taken by the Defendant/Respondent that compelled the Plaintiff to approach the court.
* **Prior Use & Registration Details:** State the claimed dates of user, registration classes, or dates of execution of relevant deeds/instruments.

### 3. PROCEDURAL HISTORY & RELIEF SOUGHT
* Track the exact legal journey of this case up to this specific order.
* Detail the precise provisions of law invoked (e.g., Order XXXIX Rules 1 & 2 CPC, Section 29 of Trademarks Act, Section 13 of HMA, etc.).
* Specify the exact interim or final reliefs being claimed by the moving party.

### 4. CORE LEGAL ISSUES & CONTROVERSIES
* Formulate the precise points of law and fact framed or identified by the court for adjudication. Frame them as deep, formal legal issues, linking them directly to statutory provisions.

### 5. EXHAUSTIVE ARGUMENTS BY THE PLAINTIFF/APPELLANT
* Provide a comprehensive, multi-paragraph breakdown of the moving party's arguments.
* Detail their statutory interpretations, allegations of prejudice or bad faith, and the specific evidentiary parameters or packaging/factual similarities they highlighted.
* List all major judicial precedents relied upon by their counsel.

### 6. EXHAUSTIVE ARGUMENTS BY THE DEFENDANT/RESPONDENT
* Provide a matching, deep analysis of the defense.
* Detail their counter-claims, statutory exceptions taken, jurisdictional objections, or highlighting of stark factual dissimilarities.
* List all major judicial precedents relied upon by the defense.

### 7. JUDICIAL ANALYSIS, STATUTORY INTERPRETATION & EVALUATION
* This must be the deepest section of the analysis. Detail the court's step-by-step reasoning.
* Explain how the court interpreted specific statutory provisions and legal tests (e.g., tests for deceptive similarity, initial interest confusion, or standard of proof).
* Analyze how the court treated conflicting precedents and how it weighed the evidence presented by both sides.

### 8. RATIO DECIDENDI (The Core Legal Principle)
* Isolate and explicitly state the binding legal principle established or reinforced by this judgment. Define the exact rule of law that will serve as a precedent for future cases.

### 9. FINAL OPERATIVE ORDER & DIRECTIONS
* State the exact final ruling of the court (e.g., dismissed, allowed, partially allowed).
* Detail any specific timelines, monetary costs, undertakings, or procedural directions imposed by the court on either party.
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
