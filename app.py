import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
test
# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Hotel Contracts Assistant",
    page_icon="📄",
    layout="wide"
)

# ==========================================
# CONTRACTS FOLDER
# ==========================================

contracts_folder = "contracts"

if not os.path.exists(contracts_folder):
    os.makedirs(contracts_folder)

# ==========================================
# GEMINI CONFIG
# ==========================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-3.8-flash")

# ==========================================
# LOAD CONTRACTS
# ==========================================

@st.cache_data
def load_contracts(folder):

    documents = []

    for pdf_file in os.listdir(folder):

        if pdf_file.lower().endswith(".pdf"):

            try:

                pdf_path = os.path.join(folder, pdf_file)

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

            except:
                pass

    return documents


documents = load_contracts(contracts_folder)

pdf_count = len(documents)

contract_names = sorted(
    [doc["name"] for doc in documents]
)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("📚 Contract Library")

    st.metric(
        "Contracts Loaded",
        pdf_count
    )

    st.divider()

    # --------------------
    # UPLOAD CONTRACT
    # --------------------

    st.subheader("📤 Upload Contract")

    uploaded_file = st.file_uploader(
        "Choose PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        save_path = os.path.join(
            contracts_folder,
            uploaded_file.name
        )

        if not os.path.exists(save_path):

            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            load_contracts.clear()

            st.success(
                f"{uploaded_file.name} uploaded successfully"
            )

            st.rerun()

        else:

            st.warning(
                "Contract already exists."
            )

    st.divider()

    # --------------------
    # CONTRACT LIST
    # --------------------

    st.subheader("📄 Available Contracts")

    for doc in contract_names:

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"📄 {doc}")

        with col2:

            if st.button(
                "🗑️",
                key=f"delete_{doc}"
            ):

                st.session_state["delete_file"] = doc

# ==========================================
# DELETE CONTRACT
# ==========================================

if "delete_file" in st.session_state:

    st.warning(
        f"Delete contract: {st.session_state['delete_file']} ?"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("✅ Confirm Delete"):

            try:

                file_path = os.path.join(
                    contracts_folder,
                    st.session_state["delete_file"]
                )

                os.remove(file_path)

                load_contracts.clear()

                del st.session_state["delete_file"]

                st.success(
                    "Contract deleted successfully."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Delete failed: {e}"
                )

    with col2:

        if st.button("❌ Cancel"):

            del st.session_state["delete_file"]

            st.rerun()

# ==========================================
# MAIN PAGE
# ==========================================

st.title("📄 Hotel Contracts Assistant")

st.caption(
    "Search across hotel contracts, offers, rate sheets and commercial agreements."
)

question = st.text_input(
    "Ask a question",
    placeholder="Example: What is the cancellation policy for Villa Nautica?"
)

# ==========================================
# SEARCH
# ==========================================

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

            relevant_docs = []

            question_words = question.lower().split()

            for doc in documents:

                score = 0

                text = doc["content"].lower()

                for word in question_words:

                    if len(word) > 3 and word in text:
                        score += 1

                if score > 0:
                    relevant_docs.append((score, doc))

            relevant_docs.sort(
                key=lambda x: x[0],
                reverse=True
            )

            contract_text = ""

            for score, doc in relevant_docs:

                contract_text += (
                    f"\n\nDOCUMENT: {doc['name']}\n"
                    f"{doc['content'][:4000]}"
                )

            if not contract_text:

                st.warning(
                    "No matching contract found."
                )

            else:

                prompt = f"""
You are an expert hotel contracts assistant.

Use ONLY the information below.

Rules:
1. Never make up information.
2. If information is missing, say:
Information not found in available contracts.
3. Mention source document names.

Question:
{question}

Contracts:
{contract_text[:30000]}

Provide Answer and Source.
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

                    st.error(str(e))

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Hotel Contracts Assistant | Powered by Gemini"
)
