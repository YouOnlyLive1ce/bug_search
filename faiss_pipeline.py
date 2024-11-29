from transformers import RobertaTokenizer, RobertaModel
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.docstore.document import Document
import faiss
import torch
import os 
import json

# Embedding class
class SolidityEmbeddings:
    def __init__(self):
        self.tokenizer = RobertaTokenizer.from_pretrained('./roberta_config')
        self.model = RobertaModel.from_pretrained('./roberta_config')
        self.model.eval()

    def __call__(self, text):
        tokens = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**tokens)
        # Mean pool across the sequence dimension for fixed-size embedding
        return outputs.last_hidden_state.mean(dim=1).squeeze(0)
    

def build_vector_store():
    functions_code = []
    repos_code_path = './processed_repositories'
    for root, _, files in os.walk(repos_code_path):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    try:
                        code = json_data["Code"]
                        functions_code.append(code)
                    except :
                        print("no Code")
                        continue
    
    documents = [
        Document(page_content=code, metadata={"source": "codearena"})
        for code in functions_code[:5]
    ]
    embeddings_model = SolidityEmbeddings()
    dim = embeddings_model("int").shape[0]

    index = faiss.IndexFlatL2(dim)
    vector_store = FAISS(
        embedding_function=embeddings_model,
        index=index,
        docstore=InMemoryDocstore({}),
        index_to_docstore_id={},
    )
    vector_store.add_documents(documents=documents)
    return vector_store.as_retriever()

retriever = build_vector_store()

def faiss_search(query):
    results = retriever.get_relevant_documents(query.code)
    if results:
        return results[0].page_content
    else:
        return "No relevant documents found."