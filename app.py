import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

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

            st.success(
                f"{uploaded_file.name} uploaded successfully"
            )

            st.rerun()

        else:

            st.warning(
                "A contract with this name already exists."
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
# DELETE CONFIRMATION
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

            contract_text = ""

            for doc in documents:

                contract_text += (
                    f"\n\nDOCUMENT: {doc['name']}\n"
                    f"{doc['content'][:5000]}"
                )

            prompt = f"""
You are an expert hotel contracts assistant.

RULES:

1. Use ONLY the contracts below.
2. Never make up information.
3. If not found, say:
   Information not found in available contracts.
4. Always mention the source contract(s).
5. Keep responses professional and concise.

CONTRACTS:

{contract_text[:60000]}

QUESTION:

{question}

FORMAT:

Answer:
<answer>

Source:
<contract name(s)>
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

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Hotel Contracts Assistant | Powered by Gemini"
)
