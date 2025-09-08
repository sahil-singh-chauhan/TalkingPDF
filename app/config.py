import os
from dotenv import load_dotenv

def load_env():
    load_dotenv()  # Load from .env file
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    os.environ['OPENAI_API_BASE'] = os.getenv('OPENAI_API_BASE')
