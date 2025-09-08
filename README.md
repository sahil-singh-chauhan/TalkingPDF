# TalkingPDF (Flask)

Chat with any PDF in a fast, modern Flask web app. Upload a document, then ask natural-language questions. Answers are grounded in the PDF via retrieval-augmented generation (RAG).

## Features
- Clean, professional UI with a 50/50 split: PDF preview on the left, chat on the right
- Independent scrolling for PDF and chat (no page scroll)
- Suggestion cards for quick prompts
- Markdown rendering (bold, tables, lists, code) for clear answers
- Subtle “thinking” indicator while answers are generated
- Smooth, non-blocking chat updates via fetch (no page reload)
- Overlay toasts for status messages that don’t shift layout

## Architecture
- UI: Flask + Jinja templates + vanilla JS/CSS (no frontend framework)
- Backend: Flask app serving routes and a JSON API for Q&A
- Retrieval: LangChain with Chroma vector store and `SentenceTransformer` embeddings
- LLM: `langchain_openai.ChatOpenAI` (configurable via `.env`)
- PDF parsing: `unstructured` loader (requires Poppler installed on the system)

Directory overview
- `app/main.py`: Flask app (routes, session handling, upload, Q&A API)
- `app/templates/`: HTML templates (`base.html`, `index.html`, `chat.html`)
- `app/static/`: CSS and uploads (`styles.css`, `uploads/`)
- `app/utils.py`: PDF loading helpers
- `app/retriever.py`: Chunking, embeddings, Chroma, retriever + chain factory
- `app/prompts.py`: Query expansion and chat prompts
- `app/memory.py`: Conversation memory for the chain
- `app/config.py`: Environment loading

## Data Flow / Pipeline
1. Upload
   - User selects a PDF in the chat page and uploads
   - Server saves it under `app/static/uploads/<filename>.pdf` for in-browser preview
2. Load & Chunk
   - `unstructured` loads the PDF into `Document` objects
   - `RecursiveCharacterTextSplitter` splits content into overlapping chunks
3. Embed & Index
   - `SentenceTransformer` embeddings are computed for each chunk
   - Chunks are stored in a Chroma vector database (in-memory by default)
4. Retrieve
   - `MultiQueryRetriever` expands the user question with `query_prompt` and retrieves relevant chunks
5. Generate
   - `ConversationalRetrievalChain` sends the question + retrieved context to the LLM using `chat_prompt`
   - Conversation history is preserved with `ConversationBufferMemory`
6. Render
   - Response is returned to the client as Markdown and rendered into HTML for a clean, formatted answer

## Requirements
- Python 3.10+
- Poppler installed and on PATH (required by `unstructured`)
- Internet access for embeddings/LLM if using hosted endpoints

Python dependencies: see `requirements.txt`.

## Setup
1) Create and activate a virtual environment
```
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate
```

2) Install dependencies
```
pip install -r requirements.txt
```

3) Install Poppler (for PDF parsing, mentioned in the requirements file.) 

4) Configure environment variables: create `.env` in project root
```
OPENAI_API_KEY=your_key_here
OPENAI_API_BASE=https://api.openai.com/v1
FLASK_SECRET_KEY=some_random_string
```

5) Run the app
```
python -m app.main
```
Then open `http://localhost:5000`.

## Usage
- Home page: brief cover/CTA
- Chat page (`/chat`):
  - Upload a PDF → it shows on the left
  - Ask a question on the right (or click a suggestion)
  - The AI shows a “thinking” indicator, then renders a Markdown answer smoothly

## Configuration
- Model: change the model in `app/retriever.py` within `ChatOpenAI` initialization
- Embeddings: adjust the sentence-transformer model in `SentenceTransformerEmbeddingsWrapper`
- Chunking: tweak `chunk_size` / `chunk_overlap` in `create_retriever`
- Prompts: edit `app/prompts.py` to change query expansion or answer formatting

## Security
- Uploaded PDFs are stored under `app/static/uploads/` for preview. For production, consider:
  - Limiting file size / type
  - Virus scanning and storage outside the web root
  - Time-based cleanup of old uploads

