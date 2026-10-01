import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# ======================================
# PAGE CONFIG
# ======================================

st.set_page_config(
    page_title="Hotel Contracts Assistant",
    page_icon="📄",
    layout="wide"
)

# ======================================
# CREATE CONTRACTS FOLDER IF NEEDED
# ======================================

contracts_folder = "contracts"

if not os.path.exists(contracts_folder):
    os.makedirs(contracts_folder)

# ======================================
# GEMINI CONFIG
# ======================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-3.8-flash")

# ======================================
# LOAD PDFS
# ======================================

documents = []

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

        except Exception:
            pass

pdf_count = len(documents)

# ======================================
# SIDEBAR
# ======================================

with st.sidebar:

    st.title("📚 Contract Library")

    uploaded_file = st.file_uploader(
        "📤 Upload New Contract",
        type=["pdf"]
    )

    if uploaded_file is not None:

        save_path = os.path.join(
            contracts_folder,
            uploaded_file.name
        )

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(
            f"✅ {uploaded_file.name} uploaded successfully"
        )

        st.rerun()

    st.divider()

    st.metric(
        "Contracts",
        pdf_count
    )

    st.divider()

    for doc in sorted(
        documents,
        key=lambda x: x["name"]
    ):
        st.write(f"📄 {doc['name']}")

# ======================================
# MAIN SCREEN
# ======================================

st.title("📄 Hotel Contracts Assistant")

st.caption(
    "Search across hotel contracts, offers, rate sheets and commercial agreements"
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Contracts Loaded",
        pdf_count
    )

with col2:
    st.metric(
        "System Status",
        "Ready ✅"
    )

st.divider()

question = st.text_input(
    "Ask a question",
    placeholder="Example: What is the cancellation policy for Furaveri Maldives?"
)

# ======================================
# SEARCH
# ======================================

if st.button(
    "🔍 Search Contracts",
    use_container_width=True
):

    if not question:

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching contracts..."
        ):

            all_contract_text = ""

            for doc in documents:

                all_contract_text += (
                    f"\n\nDOCUMENT: {doc['name']}\n"
                    f"{doc['content'][:5000]}"
                )

            prompt = f"""
You are an expert Hotel Contracts Assistant.

Rules:

1. Use ONLY the information present in the contracts.
2. Do not make up information.
3. If not found, reply:
   Information not found in available contracts.
4. Always mention the exact source document(s).

CONTRACTS:

{all_contract_text[:60000]}

QUESTION:

{question}

RESPONSE FORMAT:

Answer:
<answer>

Source:
<document name(s)>
"""

            try:

                response = model.generate_content(
                    prompt
                )

                st.markdown("## ✅ Answer")

                st.write(
                    response.text
                )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

# ======================================
# FOOTER
# ======================================

st.divider()

st.caption(
    "Powered by Gemini AI"
)
