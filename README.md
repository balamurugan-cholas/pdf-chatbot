<<<<<<< HEAD
# pdf-chatbot
PDF Chatbot is a Flask-based web application that lets users interact with PDFs using AI. Admins can upload PDF files, and users can select any uploaded file to ask questions. The app extracts text using PyMuPDF (fitz) and uses Google’s Gemini 1.5 model to generate accurate, context-aware answers.
=======
# PDF ChatBot with Admin Panel (Flask + Gemini API)

This is a Flask-based chatbot web application that allows admins to upload PDF files, and users to select and extract content from these PDFs. Users can then chat with an AI assistant powered by Google's Gemini API based on the content. The application also includes admin functionalities to manage users and uploaded PDFs.

## Features

### 🔐 Authentication
- User registration with profile picture upload
- Secure login/logout using hashed passwords
- Admin role for managing access

### 🧠 Chatbot (Gemini)
- Extracts text from uploaded PDF files
- Users can ask questions and get contextual answers
- Integrated with Google Gemini API for response generation

### 🗃 Admin Panel
- Upload and delete PDF files
- View registered users and delete/promote users
- Clean and modern UI using Bootstrap 5

## Technologies Used

- Python 3 – Core programming language
- Flask – Web framework for backend routing and session management
- SQLite – Lightweight database for storing user data
- Werkzeug – For secure password hashing and file handling
- PyMuPDF (fitz) – To extract text from PDF documents
- Google Generative AI (Gemini via google.generativeai) – For answering user questions from PDFs
- OpenAI API – Optionally used for generating AI responses
- HuggingFace Transformers – (Optional) for QA tasks using local models
- python-dotenv – For managing environment variables like API keys
- HTML5, Bootstrap 5, and Bootstrap Icons – For responsive frontend design

## Project Structure

```
pdf chatbot/
│
├── static/
│   └── profile_pics/
│   └── uploads/
│
├── templates/
│   └── account.html
│   └── chat.html
│   └── admin.html
│
├── app.py
├── users.db
├── requirements.txt
├── .env
├── .gitgnore
└── README.md
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/balamurugan-cholas/pdf-chatbot.git
cd chatbot
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

Create a `.env` file in the root directory and add your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

### 5. Run the App

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

<<<<<<< HEAD
---

## 📬 Author

**Balamurugan Cholan**  
[GitHub](https://github.com/balamurugan-cholas)  
[LinkedIn](https://in.linkedin.com/in/bala-murugan-6b73a7369)  
[Instagram](https://www.instagram.com/post_maram/)

---

=======
>>>>>>> b8c4a7c (First Push: PDF Chatbot)
## License

This project is open-source and free to use.

---

<<<<<<< HEAD
Built using Flask, Google Gemini, and Bootstrap to deliver smart, secure AI interactions.
=======
Built using Flask, Google Gemini, and Bootstrap to deliver smart, secure AI interactions.
>>>>>>> b8c4a7c (First Push: PDF Chatbot)
>>>>>>> a2cf4cb (First Push: PDF Chatbot)
