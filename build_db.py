import os
import chromadb

from pypdf import PdfReader
from chromadb.utils import embedding_functions

contracts_folder = "contracts"

client = chromadb.PersistentClient(
    path="chroma_db"
)

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

try:
    client.delete_collection("contracts")
except:
    pass

collection = client.create_collection(
    name="contracts",
    embedding_function=embedding_func
)

doc_id = 0

for pdf_file in os.listdir(contracts_folder):

    if pdf_file.lower().endswith(".pdf"):

        pdf_path = os.path.join(
            contracts_folder,
            pdf_file
        )

        reader = PdfReader(pdf_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

        chunks = [
            text[i:i+1500]
            for i in range(0, len(text), 1500)
        ]

        for chunk in chunks:

            collection.add(
                documents=[chunk],
                metadatas=[
                    {
                        "source": pdf_file
                    }
                ],
                ids=[str(doc_id)]
            )

            doc_id += 1

print("Database Built")
