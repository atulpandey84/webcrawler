from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from crawler import crawl_website, generate_insights_stream
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=True)
    messages = db.relationship('Message', backref='session', lazy=True, cascade="all, delete-orphan")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    query = request.args.get('q', '')
    if query:
        sessions = Session.query.filter(Session.url.contains(query)).order_by(Session.id.desc()).all()
    else:
        sessions = Session.query.order_by(Session.id.desc()).all()
    return jsonify([{'id': s.id, 'url': s.url} for s in sessions])

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    session = Session.query.get_or_404(session_id)
    messages = [{'role': m.role, 'content': m.content} for m in session.messages]
    return jsonify({'id': session.id, 'url': session.url, 'messages': messages})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    url = data.get('url')
    session_id = data.get('session_id')
    user_prompt = data.get('prompt')
    model = data.get('model', 'llama3')
    recursive = data.get('recursive', False)

    if not session_id and not url:
        return jsonify({'error': 'URL or Session ID is required'}), 400

    if session_id:
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        content = session.content
    else:
        # New session
        try:
            content = crawl_website(url, recursive=recursive)
            if not content:
                return jsonify({'error': 'Failed to extract content from website'}), 500

            session = Session.query.filter_by(url=url).first()
            if not session:
                session = Session(url=url, content=content)
                db.session.add(session)
                db.session.commit()
            else:
                session.content = content # Update content
                db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    chat_history = [{'role': m.role, 'content': m.content} for m in session.messages]

    def generate():
        full_response = ""
        for chunk in generate_insights_stream(session.content, model, user_prompt, chat_history):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        # Save history
        user_msg = Message(session_id=session.id, role='user', content=user_prompt)
        ai_msg = Message(session_id=session.id, role='assistant', content=full_response)
        db.session.add(user_msg)
        db.session.add(ai_msg)
        db.session.commit()

        yield f"data: {json.dumps({'done': True, 'session_id': session.id})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
