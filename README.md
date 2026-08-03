# 🎓 EKC AI Helpdesk Chatbot

An AI-powered college helpdesk chatbot developed for **Eranad Knowledge City Technical Campus (EKCTC)**. The chatbot assists students by answering queries related to admissions, KTU regulations, courses, scholarships, placements, campus facilities, and more.

---

## 🚀 Features

- AI-powered intent recognition using TF-IDF and cosine similarity
- FastAPI backend for handling chatbot requests
- SQLite database for storing chatbot responses
- Modern and responsive chat interface
- Speech-to-text support
- Dark mode
- Typewriter animation for bot responses
- Quick suggestion buttons for common queries

---

## 🛠️ Technologies Used

- Python
- FastAPI
- Scikit-learn
- SQLite
- HTML5
- CSS3
- JavaScript

---

## 📂 Project Structure

```
EKC-AI-Helpdesk-Chatbot/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── nlp_engine.py
│   ├── chatbot.db
│   ├── intents.json
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── EKC.png
│
├── training/
│   └── train_model.py
│
├── screenshots/
│
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/EKC-AI-Helpdesk-Chatbot.git
```

### Install dependencies

```bash
pip install -r backend/requirements.txt
```

### Run the FastAPI server

```bash
uvicorn backend.main:app --reload
```

Open `frontend/index.html` in your browser.

---

## 💬 Sample Queries

- How can I get admission?
- What are the courses offered?
- Tell me about KTU.
- What is the fee structure?
- What scholarships are available?
- Where can I check my results?
- Tell me about placements.
- Is hostel available?

---

## 📸 Screenshots

Add screenshots of your chatbot interface here.

Example:

- Home Screen
- Chat Interface
- Dark Mode
- Voice Input

---

## 🔮 Future Enhancements

- Integration with Large Language Models (LLMs)
- Multi-language support
- Admin dashboard
- Live college database integration
- Authentication and user accounts
- Mobile application

---

## 👨‍💻 Author

**Zakariya Shamsudin**

B.Tech Computer Science Engineering

---

## 📄 License

This project is licensed under the MIT License.
