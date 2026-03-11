# 📝 Flask Realtime Docs

A real-time collaborative document editor built with **Flask** and **Flask-SocketIO**. Multiple users can edit the same document simultaneously with changes syncing live across all connected clients.

## 🚀 Features

- Real-time document editing with WebSockets
- Multi-user collaboration (changes sync instantly)
- Clean and minimal UI
- Lightweight Flask backend

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-SocketIO
- **Frontend:** HTML, CSS, JavaScript
- **Real-time:** WebSockets (Socket.IO)

## 📁 Project Structure

```
flask-realtime-docs/
├── static/
│   └── css/           # Stylesheets
├── templates/         # HTML templates
├── app.py             # Main Flask application
├── requirements.txt
└── .gitignore
```

## ⚙️ Installation & Setup

```bash
# 1. Clone the repo
git clone https://github.com/Anandh2002/flask-realtime-docs.git
cd flask-realtime-docs

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

Open multiple tabs to see real-time collaboration in action!

## 🔌 How It Works

1. A user opens the document in their browser
2. Any edits are emitted via **Socket.IO** to the Flask server
3. The server broadcasts the changes to all other connected clients
4. All clients update their document view instantly

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
