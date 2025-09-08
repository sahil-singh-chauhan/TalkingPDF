from langchain_community.document_loaders import UnstructuredPDFLoader
import os

def load_pdf(file_path):
    loader = UnstructuredPDFLoader(file_path)
    return loader.load()

def clean_temp_file(file_path):
    os.remove(file_path)
