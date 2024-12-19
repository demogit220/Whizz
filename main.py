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

api_key=os.getenv("OPENAI_API_KEY")


def load_documents(dir_path, file_path="./data_demo/constitutionofindiaacts.pdf", save_md_file=True, use_pymup=True):
    if use_pymup:
        if save_md_file:
            md_text = pymupdf4llm.to_markdown(file_path)
            pathlib.Path("output.md").write_bytes(md_text.encode())
        llama_reader = pymupdf4llm.LlamaMarkdownReader()
        llama_docs = llama_reader.load_data(file_path)
    else:
        llama_docs = SimpleDirectoryReader(dir_path).load_data(show_progress=True)
    return llama_docs

def save_persistent(index: VectorStoreIndex, dir_path="index_store"):
    index.storage_context.persist(dir_path)

def load_from_storage(dir_path="index_store") -> VectorStoreIndex:
    storage_context = StorageContext.from_defaults(persist_dir=dir_path)
    index = load_index_from_storage(storage_context)
    return index

def load_index(llama_docs):
    index = VectorStoreIndex.from_documents(llama_docs)
    return index

def query_llm(query: str, index: VectorStoreIndex):
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response

if __name__ == "__main__":
    print("hello from Whizz!")
    print(api_key)

    # system_prompt="""You are a Q&A assistant. Your goal is to answer questions as accurately as possible based on the instructions and context provided."""
    # query_wrapper_prompt=SimpleInputPrompt("<|USER|>{query_str}<|ASSISTANT|>")
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5", cache_folder="embeddings")
    Settings.llm = OpenAI(model="gpt-4o-mini")
    # breakpoint()
    if os.path.isdir("index_store"):
        index = load_from_storage()
    else:
        docs = load_documents(dir_path="data/Tarana KA",use_pymup=False)
        index = load_index(docs)
        save_persistent(index)
    retriever = VectorIndexRetriever(index,similarity_top_k=4)
    postprocessor = SimilarityPostprocessor(similarity_cutoff=0.65)
    query_engine=RetrieverQueryEngine(retriever, node_postprocessors=[postprocessor])
    response = query_engine.query("How to connect a BN to TCS?")
    pprint_response(response, show_source=True)

