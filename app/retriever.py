from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
from typing import List
from langchain_core.embeddings import Embeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI

class SentenceTransformerEmbeddingsWrapper(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

def create_retriever(data, query_prompt):
    splitter = RecursiveCharacterTextSplitter(chunk_size=8000, chunk_overlap=100)
    chunks = splitter.split_documents(data)
    model_name = "latterworks/ollama-embeddings"
    embeddings_model = SentenceTransformerEmbeddingsWrapper(model_name)
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings_model,
        collection_name="apirag"
    )
    llm = ChatOpenAI(model= "openai/gpt-oss-20b:free", temperature = 0.6)
    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(),
        llm,
        prompt=query_prompt,
    )
    return retriever

def create_chain(retriever, memory, prompt):
    from langchain.chains import ConversationalRetrievalChain
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model= "openai/gpt-oss-20b:free", temperature = 0.6)
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )
