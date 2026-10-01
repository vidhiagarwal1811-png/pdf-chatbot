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

                text = ""

                for page in reader.pages:

                    try:
                        page_text = page.extract_text()

                        if page_text:
                            text += page_text + "\n"

                    except:
                        pass

                documents.append(
                    {
                        "name": pdf_file,
                        "content": text
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
                f.write(
                    uploaded_file.getbuffer()
                )

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
    # REBUILD DATABASE
    # --------------------

    st.subheader("🔄 Knowledge Base")

    if st.button(
        "Rebuild Database",
        use_container_width=True
    ):

        with st.spinner(
            "Building ChromaDB..."
        ):

            try:

                subprocess.run(
                    ["python", "build_db.py"],
                    capture_output=True,
                    text=True
                )

                st.success(
                    "✅ Database Rebuilt"
                )

            except Exception as e:

                st.error(str(e))

    st.divider()

    # --------------------
    # CONTRACT LIST
    # --------------------

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

            file_path = os.path.join(
                contracts_folder,
                st.session_state["delete_file"]
            )

            try:

                os.remove(file_path)

                load_contracts.clear()

                del st.session_state[
                    "delete_file"
                ]

                st.rerun()

            except Exception as e:

                st.error(str(e))

    with col2:

        if st.button("❌ Cancel"):

            del st.session_state[
                "delete_file"
            ]

            st.rerun()

# ==========================================
# MAIN PAGE
# ==========================================

st.title(
    "📄 Hotel Contracts Assistant"
)

st.caption(
    "Search contracts using ChromaDB + Gemini"
)

question = st.text_input(
    "Ask a contract-related question"
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
            "Searching knowledge base..."
        ):

            try:

                client = chromadb.PersistentClient(
                    path="chroma_db"
                )

                embedding_func = (
                    embedding_functions
                    .SentenceTransformerEmbeddingFunction(
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

                sources = set()

                for doc, meta in zip(
                    results["documents"][0],
                    results["metadatas"][0]
                ):

                    context += doc + "\n\n"

                    sources.add(
                        meta["source"]
                    )

                prompt = f"""
You are an expert hotel contracts assistant.

Use ONLY the information provided.

If information is missing,
say:

Information not found in available contracts.

QUESTION:
{question}

CONTEXT:
{context}

Provide a concise business answer.
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

                for source in sorted(sources):

                    st.write(
                        f"• {source}"
                    )

            except Exception as e:

                st.error(str(e))

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Powered by ChromaDB + Gemini"
)
