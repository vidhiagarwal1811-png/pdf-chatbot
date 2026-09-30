import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

st.title("PDF Chatbot")

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

uploaded_files = st.file_uploader(
    "Upload PDF(s)",
    type="pdf",
    accept_multiple_files=True
)

pdf_text = ""

if uploaded_files:
    for file in uploaded_files:
        reader = PdfReader(file)

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pdf_text += text

question = st.text_input("Ask a question")

if st.button("Ask"):

    if uploaded_files and question:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Answer the question using only this PDF content:

                    {pdf_text[:50000]}

                    Question:
                    {question}
                    """
                }
            ]
        )

        st.write(response.choices[0].message.content)
