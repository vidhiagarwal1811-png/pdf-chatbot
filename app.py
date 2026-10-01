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
# GEMINI CONFIG
# ==================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-3.8-flash")

# ==================================
# LOAD CONTRACTS
# ==================================

contracts_folder = "contracts"

documents = []
pdf_count = 0

if os.path.exists(contracts_folder):

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

                        text = page.extract_text()

                        if text:
                            full_text += text + "\n"

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
# SIDEBAR
# ==================================

with st.sidebar:

    st.title("📚 Contract Library")

    st.success(f"{pdf_count} Contracts Loaded")

    st.divider()

    for doc in sorted(documents, key=lambda x: x["name"]):

        st.write(f"📄 {doc['name']}")

# ==================================
# MAIN PAGE
# ==================================

st.title("📄 Hotel Contracts Assistant")

st.caption(
    "Search hotel contracts, rates, cancellation policies, offers and commercial terms."
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Contracts Loaded",
        pdf_count
    )

with col2:
    st.metric(
        "Knowledge Base",
        "Ready ✅"
    )

st.divider()

# ==================================
# QUESTION
# ==================================

question = st.text_input(
    "Ask a question",
    placeholder="Example: What is the Beach Villa rate in Villa Nautica?"
)

# ==================================
# ASK BUTTON
# ==================================

if st.button("🔍 Search Contracts", use_container_width=True):

    if not question:

        st.warning("Please enter a question.")

    else:

        with st.spinner("Searching contracts..."):

            contract_text = ""

            for doc in documents:

                contract_text += (
                    f"\n\nDOCUMENT: {doc['name']}\n"
                    f"{doc['content'][:8000]}"
                )

            prompt = f"""
You are an expert hotel contracting assistant.

You must answer ONLY using information available in the contracts.

Instructions:

1. Never make up an answer.
2. If information is unavailable, say:
   "Information not found in available contracts."
3. Keep answers concise and professional.
4. Always provide source document names.
5. Mention only the documents actually used.

CONTRACTS:

{contract_text[:60000]}

QUESTION:

{question}

FORMAT RESPONSE EXACTLY AS:

Answer:
<answer>

Source:
<source document names>
"""

            try:

                response = model.generate_content(prompt)

                st.markdown("## ✅ Answer")

                st.markdown(response.text)

            except Exception as e:

                st.error(f"Error: {e}")

# ==================================
# FOOTER
# ==================================

st.divider()

st.caption(
    "Hotel Contracts Assistant | Powered by Gemini"
)
