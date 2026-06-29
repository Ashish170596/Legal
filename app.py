import streamlit as st
import tempfile
import os
from google import genai

# Setup the Page
st.set_page_config(page_title="Legal Judgment Analyzer", page_icon="⚖️")
st.title("⚖️ Automated Legal Judgment & Case Analyzer")
st.write("Upload any legal document, including scanned photocopies. The AI will extract a detailed, professional brief.")

# Connect to Gemini securely
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Upload Box
uploaded_file = st.file_uploader("Upload Judgment or Case File PDF", type=["pdf"])

if uploaded_file is not None:
    if st.button("Analyze Document Now"):
        with st.spinner("Processing scanned document through OCR... This may take a minute."):
            
            # 1. Save the file temporarily to the server
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_filepath = temp_file.name
                
            try:
                # 2. Upload the raw PDF directly to Gemini's Vision engine
                gemini_file = client.files.upload(file=temp_filepath)
                
                # 3. Your strict legal instructions
                prompt = """
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
                * **Commercial/Matrimonial Context:** Detail the nature of the parties' businesses or relationships, prior history, and the exact subject matter of the dispute.
                * **Genesis of the Dispute:** Explain exactly how, when, and why the cause of action arose. Detail the specific actions taken by the Defendant/Respondent that compelled the Plaintiff to approach the court.
                * **Prior Use & Registration Details:** State the claimed dates of user, registration classes, or dates of execution of relevant deeds/instruments.

                ### 3. PROCEDURAL HISTORY & RELIEF SOUGHT
                * Track the exact legal journey of this case up to this specific order.
                * Detail the precise provisions of law invoked.
                * Specify the exact interim or final reliefs being claimed by the moving party.

                ### 4. CORE LEGAL ISSUES & CONTROVERSIES
                * Formulate the precise points of law and fact framed or identified by the court for adjudication. Frame them as deep, formal legal issues, linking them directly to statutory provisions.

                ### 5. EXHAUSTIVE ARGUMENTS BY THE PLAINTIFF/APPELLANT
                * Provide a comprehensive, multi-paragraph breakdown of the moving party's arguments.
                * Detail their statutory interpretations, allegations of prejudice, and judicial precedents relied upon.

                ### 6. EXHAUSTIVE ARGUMENTS BY THE DEFENDANT/RESPONDENT
                * Provide a matching, deep analysis of the defense.
                * Detail their counter-claims, statutory exceptions taken, jurisdictional objections, and judicial precedents relied upon.

                ### 7. JUDICIAL ANALYSIS, STATUTORY INTERPRETATION & EVALUATION
                * This must be the deepest section of the analysis. Detail the court's step-by-step reasoning.
                * Explain how the court interpreted specific statutory provisions and how it weighed the evidence presented by both sides.

                ### 8. RATIO DECIDENDI (The Core Legal Principle)
                * Isolate and explicitly state the binding legal principle established or reinforced by this judgment. Define the exact rule of law that will serve as a precedent for future cases.

                ### 9. FINAL OPERATIVE ORDER & DIRECTIONS
                * State the exact final ruling of the court (e.g., dismissed, allowed, partially allowed).
                * Detail any specific timelines, monetary costs, undertakings, or procedural directions imposed by the court on either party.
                """
                
                # 4. Ask Gemini to analyze the uploaded file using the prompt
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[gemini_file, prompt]
                )
                
                # 5. Display the deep analysis
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
            finally:
                # 6. Clean up the temporary file from the server securely
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
