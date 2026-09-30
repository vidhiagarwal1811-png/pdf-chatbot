import os
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

st.set_page_config(page_title="Contracts Assistant")

st.title("📄 Hotel Contracts Assistant")

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

pdf_text = ""

contracts_folder = "contracts"

pdf_count = 0

if os.path.exists(contracts_folder):

    for pdf_file in os.listdir(contracts_folder):

        if pdf_file.lower().endswith(".pdf"):

            pdf_count += 1

            pdf_path = os.path.join(
                contracts_folder,
                pdf_file
            )

            reader = PdfReader(pdf_path)

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    pdf_text += (
                        f"\n\nDOCUMENT: {pdf_file}\n"
                        f"{text}"
                    )

st.success(f"{pdf_count} contracts loaded")

question = st.text_input(
    "Ask a question about contracts"
)

if st.button("Ask"):

    if question:

        with st.spinner("Searching contracts..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
You are a hotel contracting assistant.

Use only the contract content below.

{pdf_text[:100000]}

Question:
{question}
"""
                    }
                ]
            )

            st.write(
                response.choices[0].message.content
            )
