from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, join_room, leave_room, emit
import os
import json



app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///docs.db'   # dev only
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")  # allow local testing

# -------------------------
# Models
# -------------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    # We'll store HTML content for simplicity (Quill can paste HTML)
    content = db.Column(db.Text, default="")


# -------------------------
# Auth
# -------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            return "Email already registered", 400
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user); db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return "Invalid credentials", 401
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# -------------------------
# Document routes
# -------------------------

@app.route('/')
@login_required
def index():
    docs = Document.query.all()
    return render_template('index.html', docs=docs)

@app.route('/create', methods=['POST'])
@login_required
def create_doc():
    title = request.form.get('title','Untitled').strip()
    doc = Document(title=title, content="")
    db.session.add(doc)
    db.session.commit()
    return redirect(url_for('editor', doc_id=doc.id))

@app.route('/doc/<int:doc_id>')
@login_required
def editor(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return render_template('editor.html', doc=doc, user_id=current_user.id)

# -------------------------
# Socket.IO events for real-time collaboration
# -------------------------

@socketio.on('join')
def on_join(data):
    room = str(data['doc_id'])
    join_room(room)
    doc = Document.query.get(data['doc_id'])
    emit('load_document', {'content': doc.content}, room=request.sid)


@socketio.on('leave')
def on_leave(data):
    room = str(data['doc_id'])
    leave_room(room)


@socketio.on('editor_update')
def on_editor_update(data):
    room = str(data['doc_id'])
    doc = Document.query.get(data['doc_id'])
    doc.content = data['content']
    db.session.commit()
    emit('remote_update', {'content': data['content']}, room=room, include_self=False)


@socketio.on('title_update')
def on_title_update(data):
    doc = Document.query.get(data['doc_id'])
    if doc:
        doc.title = data['title'].strip()
        db.session.commit()
        # Broadcast to ALL clients (not just in one doc room) so index & editor both get it
        emit('remote_title_update', {
            'doc_id': doc.id,
            'title': doc.title
        }, broadcast=True, include_self=False)



if __name__=="__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)