import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="Hotel Contracts Assistant",
    page_icon="📄",
    layout="wide"
)

# ==================================
# HEADER
# ==================================

st.title("📄 Hotel Contracts Assistant")
st.caption("Search hotel contracts, rates, policies and commercial terms")

# ==================================
# GEMINI CONFIG
# ==================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-3.8-flash"
)

# ==================================
# LOAD CONTRACTS
# ==================================

contracts_folder = "contracts"

documents = []
pdf_count = 0

if os.path.exists(contracts_folder):

    with st.spinner("Loading contracts..."):

        for pdf_file in os.listdir(contracts_folder):

            if pdf_file.lower().endswith(".pdf"):

                try:

                    pdf_path = os.path.join(
                        contracts_folder,
                        pdf_file
                    )

                    reader = PdfReader(pdf_path)

                    full_text = ""

                    for page in reader.pages:

                        try:

                            page_text = page.extract_text()

                            if page_text:
                                full_text += page_text + "\n"

                        except:
                            pass

                    documents.append(
                        {
                            "name": pdf_file,
                            "content": full_text
                        }
                    )

                    pdf_count += 1

                except Exception:
                    pass

# ==================================
# DASHBOARD
# ==================================

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Contracts Loaded",
        pdf_count
    )

with col2:
    st.metric(
        "Knowledge Base",
        "Ready"
    )

# ==================================
# QUESTION BOX
# ==================================

question = st.text_input(
    "Ask a question",
    placeholder="Example: What is the Beach Villa rate in Villa Nautica?"
)

# ==================================
# ASK BUTTON
# ==================================

if st.button("🔍 Search Contracts"):

    if not question:

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner("Searching contracts..."):

            combined_text = ""

            source_docs = []

            for doc in documents:

                combined_text += (
                    f"\n\nDOCUMENT: {doc['name']}\n"
                    f"{doc['content'][:8000]}"
                )

                source_docs.append(doc["name"])

            prompt = f"""
You are an expert hotel contracting assistant.

Rules:

1. Use ONLY information present in the contracts.
2. If the answer cannot be found, say:
   "Information not found in available contracts."
3. Give concise business-friendly answers.
4. Mention source document names used.

CONTRACTS:

{combined_text[:60000]}

QUESTION:

{question}

RESPONSE FORMAT:

Answer:
<answer>

Sources:
- document name
"""

            try:

                response = model.generate_content(
                    prompt
                )

                st.success("Answer Generated")

                st.subheader("Answer")

                st.write(response.text)

                with st.expander(
                    "📄 Available Source Documents"
                ):

                    for doc in source_docs:

                        st.write(f"• {doc}")

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

# ==================================
# CONTRACT LIBRARY
# ==================================

with st.expander("📚 Contract Library"):

    for doc in documents:

        st.write(
            f"📄 {doc['name']}"
        )
