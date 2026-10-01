import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

st.set_page_config(page_title="Hotel Contracts Assistant")

st.title("📄 Hotel Contracts Assistant")

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-2.5-flash")

contracts_folder = "contracts"

pdf_text = ""
pdf_count = 0

if os.path.exists(contracts_folder):

    for pdf_file in os.listdir(contracts_folder):

        if pdf_file.lower().endswith(".pdf"):

            try:

                pdf_count += 1

                pdf_path = os.path.join(
                    contracts_folder,
                    pdf_file
                )

                reader = PdfReader(pdf_path)

                for page in reader.pages:

                    try:

                        text = page.extract_text()

                        if text:
                            pdf_text += (
                                f"\n\nDOCUMENT: {pdf_file}\n{text}"
                            )

                    except:
                        pass

            except:
                st.warning(
                    f"Could not read {pdf_file}"
                )

st.success(f"{pdf_count} PDFs loaded")

question = st.text_input(
    "Ask a question about contracts"
)

if st.button("Ask"):

    if question:

        with st.spinner("Searching contracts..."):

            prompt = f"""
You are a hotel contracts assistant.

Use only the contract information below.

{pdf_text[:50000]}

Question:
{question}
"""

            response = model.generate_content(prompt)

            st.write(response.text)
