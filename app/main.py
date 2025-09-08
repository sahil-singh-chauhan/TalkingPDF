from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from app.config import load_env
from app.utils import load_pdf, clean_temp_file
from app.retriever import create_retriever, create_chain
from app.prompts import query_prompt, chat_prompt
from app.memory import create_memory
import os
import tempfile
import markdown as md

load_env()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me")

# Uploads path for PDF preview
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory cache for per-session state
SESSION_STATE = {}

def get_session_id():
    if 'sid' not in session:
        session['sid'] = os.urandom(16).hex()
    return session['sid']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET'])
def chat():
    sid = get_session_id()
    state = SESSION_STATE.get(sid, {
        'history': [],
        'generated': ["Hello! Upload a PDF and ask me anything about it 🤗"],
        'past': ["Hey! 👋"],
        'chain': None,
        'pdf_url': None
    })
    SESSION_STATE[sid] = state
    suggestions = [
        "Summarize the key points of this section.",
        "List important definitions and terms.",
        "What are the main arguments and evidence?"
    ]
    # render markdown to HTML for past generated messages
    rendered_generated = [md.markdown(m, extensions=["tables", "fenced_code", "sane_lists"]) for m in state['generated']]
    return render_template('chat.html', past=state['past'], generated_html=rendered_generated, pdf_url=state.get('pdf_url'), suggestions=suggestions)

@app.route('/upload', methods=['POST'])
def upload():
    sid = get_session_id()
    if 'pdf' not in request.files:
        flash('No file part')
        return redirect(url_for('chat'))
    file = request.files['pdf']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('chat'))

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    try:
        data = load_pdf(save_path)
        retriever = create_retriever(data, query_prompt)
        memory = create_memory()
        chain = create_chain(retriever, memory, chat_prompt)

        state = SESSION_STATE.get(sid, {
            'history': [],
            'generated': ["Hello! Upload a PDF and ask me anything about it 🤗"],
            'past': ["Hey! 👋"],
            'chain': None,
            'pdf_url': None
        })
        state['chain'] = chain
        state['pdf_url'] = url_for('static', filename=f'uploads/{filename}')
        SESSION_STATE[sid] = state
        flash('PDF uploaded and processed successfully!')
    except Exception as e:
        flash(f'Failed to process PDF: {e}')

    return redirect(url_for('chat'))

@app.route('/ask', methods=['POST'])
def ask():
    # Non-JS fallback: process and redirect
    sid = get_session_id()
    question = request.form.get('question', '').strip()
    state = SESSION_STATE.get(sid)
    if not state or state.get('chain') is None:
        flash('Please upload a PDF file first.')
        return redirect(url_for('chat'))
    if not question:
        flash('Please enter a question.')
        return redirect(url_for('chat'))
    response = state['chain'].invoke(question)
    state['past'].append(question)
    answer_text = response.get('answer') if isinstance(response, dict) else str(response)
    state['generated'].append(answer_text)
    SESSION_STATE[sid] = state
    return redirect(url_for('chat'))

@app.route('/api/ask', methods=['POST'])
def api_ask():
    sid = get_session_id()
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    state = SESSION_STATE.get(sid)
    if not state or state.get('chain') is None:
        return jsonify({"error": "Please upload a PDF file first."}), 400
    if not question:
        return jsonify({"error": "Please enter a question."}), 400
    response = state['chain'].invoke(question)
    answer_text = response.get('answer') if isinstance(response, dict) else str(response)
    # Persist
    state['past'].append(question)
    state['generated'].append(answer_text)
    SESSION_STATE[sid] = state
    # Render markdown to HTML for client
    answer_html = md.markdown(answer_text, extensions=["tables", "fenced_code", "sane_lists"])
    return jsonify({"question": question, "answer": answer_html})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=True)
