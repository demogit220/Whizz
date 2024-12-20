import os
import pathlib
from dotenv import load_dotenv

import pymupdf4llm
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.prompts.prompts import SimpleInputPrompt
from llama_index.core.response.pprint_utils import pprint_response
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.llms.openai import OpenAI
from flask import Flask, request, jsonify
from sales_ticket import auth_token, create_ticket_utility

app = Flask(__name__)
api_key=os.getenv("OPENAI_API_KEY")

@app.route('/v1/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Invalid request. Please provide a query.'}), 400
    query = data['query']
    global query_engine
    response = query_engine.query(query)
    # retrieved_documents = [node.node.get_text() for node in response.source_nodes]
    # context = "\n".join(retrieved_documents)
    # final_response = f"Context:\n{context}\n\nQuery:\n{query}\n\nAnswer:\n{response.response}"
    return jsonify({'response': response.response})

@app.route("/v1/create_ticket", methods=["POST"])
def create_ticket():
    data = request.get_json()
    try:
        token = auth_token()
        case_id = create_ticket_utility(token, data)

        return jsonify({
            "message": "Ticket created successfully",
            "ticket_id": case_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def load_documents_from_directory_use_pymup(dir_path, save_md=False):
    llama_docs = []  
    
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        
        if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
            if save_md:
            # Save Markdown file with the same name as the original file
                md_text = pymupdf4llm.to_markdown(file_path)
                output_md_path = pathlib.Path(f"md_data_pymup/{file_name}.md")
                output_md_path.write_bytes(md_text.encode())
            llama_reader = pymupdf4llm.LlamaMarkdownReader()
            docs = llama_reader.load_data(file_path)
            llama_docs.extend(docs) 
    
    return llama_docs

def load_documents(dir_path):
    llama_docs = SimpleDirectoryReader(dir_path).load_data(show_progress=True)
    return llama_docs

def save_persistent(index: VectorStoreIndex, dir_path):
    index.storage_context.persist(dir_path)

def load_from_storage(dir_path) -> VectorStoreIndex:
    storage_context = StorageContext.from_defaults(persist_dir=dir_path)
    index = load_index_from_storage(storage_context)
    return index

def load_index(llama_docs):
    index = VectorStoreIndex.from_documents(llama_docs)
    return index

def initalize():
    print("hello from Whizz!")
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5", cache_folder="embeddings")
    Settings.llm = OpenAI(model="gpt-4o-mini")
    persistent_dir = "index_store"
    dir_path = "data/Tarana KA"

    if os.path.isdir(persistent_dir):
        index = load_from_storage(persistent_dir)
    else:
        docs = load_documents_from_directory_use_pymup(dir_path)
        index = load_index(docs)
        save_persistent(index, persistent_dir)
    
    global query_engine
    # query_engine = index.as_query_engine()   
    retriever = VectorIndexRetriever(index)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.70)
    query_engine = RetrieverQueryEngine(retriever=retriever, node_postprocessors=[postprocessor])

if __name__ == "__main__":
    initalize()
    app.run(debug=True)
    