import os
import subprocess
import streamlit as st
import google.generativeai as genai
import chromadb

from pypdf import PdfReader
from chromadb.utils import embedding_functions

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
# GEMINI
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

    docs = []

    for pdf_file in os.listdir(folder):

        if pdf_file.lower().endswith(".pdf"):

            docs.append(pdf_file)

    return sorted(docs)


contract_names = load_contracts(contracts_folder)

pdf_count = len(contract_names)

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

    # ----------------------
    # UPLOAD
    # ----------------------

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

                f.write(
                    uploaded_file.getbuffer()
                )

            load_contracts.clear()

            st.success(
                f"{uploaded_file.name} uploaded successfully"
            )

        else:

            st.warning(
                "Contract already exists."
            )

    st.divider()

    # ----------------------
    # REBUILD DATABASE
    # ----------------------

    st.subheader("🔄 Knowledge Base")

    if st.button(
        "Rebuild Database",
        use_container_width=True
    ):

        with st.spinner(
            "Building ChromaDB..."
        ):

            try:

                result = subprocess.run(
                    ["python", "build_db.py"],
                    capture_output=True,
                    text=True
                )

                st.code(result.stdout)

                if result.stderr:
                    st.code(result.stderr)

                st.success(
                    "✅ Database Rebuilt Successfully"
                )

            except Exception as e:

                st.error(str(e))

    st.divider()

    # ----------------------
    # CONTRACT LIST
    # ----------------------

    st.subheader("📄 Available Contracts")

    for doc in contract_names:

        col1, col2 = st.columns([4, 1])

        with col1:

            st.write(
                f"📄 {doc}"
            )

        with col2:

            if st.button(
                "🗑️",
                key=f"delete_{doc}"
            ):

                st.session_state[
                    "delete_file"
                ] = doc

# ==========================================
# DELETE CONTRACT
# ==========================================

if "delete_file" in st.session_state:

    st.warning(
        f"Delete contract: {st.session_state['delete_file']} ?"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "✅ Confirm Delete"
        ):

            try:

                file_path = os.path.join(
                    contracts_folder,
                    st.session_state[
                        "delete_file"
                    ]
                )

                os.remove(file_path)

                load_contracts.clear()

                del st.session_state[
                    "delete_file"
                ]

                st.success(
                    "Contract deleted successfully"
                )

                st.rerun()

            except Exception as e:

                st.error(str(e))

    with col2:

        if st.button(
            "❌ Cancel"
        ):

            del st.session_state[
                "delete_file"
            ]

            st.rerun()

# ==========================================
# MAIN SCREEN
# ==========================================

st.title(
    "📄 Hotel Contracts Assistant"
)

st.caption(
    "Search hotel contracts using ChromaDB + Gemini"
)

question = st.text_input(
    "Ask a contract-related question",
    placeholder="Example: What is the early bird offer for Furaveri?"
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

        try:

            with st.spinner(
                "Searching contracts..."
            ):

                client = chromadb.PersistentClient(
                    path="./chroma_db"
                )

                embedding_func = (
                    embedding_functions.SentenceTransformerEmbeddingFunction(
                        model_name="all-MiniLM-L6-v2"
                    )
                )

                collection = client.get_collection(
                    name="contracts",
                    embedding_function=embedding_func
                )

                results = collection.query(
                    query_texts=[question],
                    n_results=10
                )

                context = ""

                sources = []

                for doc, meta in zip(
                    results["documents"][0],
                    results["metadatas"][0]
                ):

                    context += doc + "\n\n"

                    source_text = (
                        f"{meta['source']} "
                        f"(Page {meta['page']})"
                    )

                    if source_text not in sources:

                        sources.append(
                            source_text
                        )

                prompt = f"""
You are an expert hotel contracts assistant.

Rules:

1. Use ONLY the context below.
2. Never make up information.
3. If information is missing say:
   Information not found in available contracts.
4. Keep answers concise and professional.

Question:
{question}

Context:
{context}
"""

                response = model.generate_content(
                    prompt
                )

                st.markdown(
                    "## ✅ Answer"
                )

                st.write(
                    response.text
                )

                st.markdown(
                    "### 📄 Sources"
                )

                for source in sources:

                    st.write(
                        f"• {source}"
                    )

        except Exception as e:

            st.error(
                str(e)
            )

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Powered by ChromaDB + Gemini"
)
