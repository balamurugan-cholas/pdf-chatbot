from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import fitz
import openai
from dotenv import load_dotenv
from transformers import pipeline
import google.generativeai as genai
from flask import g
from datetime import datetime

app = Flask(__name__)
app.secret_key = '17b2005'

##load env
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model = genai.GenerativeModel("gemini-1.5-flash")

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROFILE_PIC_FOLDER'] = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'pdf'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

##Ensuring the upload and profile pciture folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROFILE_PIC_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

##Users/Admin database initialization
def init_user_db():
    with sqlite3.connect('users.db', timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'admin')),
                profile_pic TEXT
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    pdf_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('chat.html', chat_log=session.get('chat_log', []),
                            extracted_text=session.get('extracted_text', ""),
                            pdf_files=pdf_files)

'''@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['pdf']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        extracted_text = extract_text_from_pdf(file_path)

        session['chat_log'] = []
        session['extracted_text'] = extracted_text[:300]
        return render_template('chat.html', chat_log=[], extracted_text=extracted_text)
    
    else:
        flash('Invalid file type. Please upload a PDF file.')
        return redirect(url_for('index'))'''

@app.route('/select', methods=['POST'])
def select_pdf():
    selected_pdf = request.form.get('selected_pdf')
    if not selected_pdf:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], selected_pdf)
    extracted_text = extract_text_from_pdf(file_path)
    session['chat_log'] = []
    session['extracted_text'] = extracted_text[:300]
    return render_template('chat.html', chat_log=[], extracted_text=extracted_text, pdf_files=os.listdir(app.config['UPLOAD_FOLDER']))

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('message', '').strip()
    if not user_input.strip():
        return redirect(url_for('index'))
    
    extracted_text = session.get('extracted_text', "")
    chat_log = session.get('chat_log', [])

    ##Getting the current time
    current_time = datetime.now().strftime("%I:%M %p")

    ##Append user input with timestamp to chat log
    chat_log.append({'role': 'user', 'content': user_input, 'time': current_time})

    ##prepare the prompt
    answer = generate_answer(user_input, extracted_text)

    ##Append the answer to chat log
    chat_log.append({'role': 'assistant', 'content': answer, 'time': datetime.now().strftime("%I:%M %p")})
    session['chat_log'] = chat_log
    return render_template('chat.html', chat_log=chat_log, extracted_text=extracted_text, pdf_files=os.listdir(app.config['UPLOAD_FOLDER']))

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()
    return text

qa_pipeline = pipeline('question-answering')

def generate_answer(user_input, extracted_text):
    try:
        context = extracted_text.strip()
        if not context:
            return "No valid content found in the uploaded PDF."
        
        prompt = f"Context:\n{context[:4000]}\n\nQuestion: {user_input}\nAnswer:"

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/register', methods=['GET', 'POST'])    
@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'register':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role', 'user')
            profile_pic = request.files.get('profile_pic')

            if not username or not password:
                flash('Username and password are required.')
                return redirect(url_for('account'))

            hashed_password = generate_password_hash(password)
            profile_pic_path = None

            if profile_pic and profile_pic.filename != '':
                if profile_pic.filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS:
                    pic_filename = secure_filename(profile_pic.filename)
                    profile_pic_path = os.path.join(app.config['PROFILE_PIC_FOLDER'], pic_filename)
                    profile_pic.save(profile_pic_path)
                else:
                    flash('Invalid Image type, please upload a PNG, JPG, JPEG, or GIF image.')
                    return redirect(url_for('account'))

            try:
                with sqlite3.connect('users.db', timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO users (username, password, role, profile_pic)
                        VALUES (?, ?, ?, ?)
                    ''', (username, hashed_password, role, profile_pic_path))
                    conn.commit()
                    flash('Registration successful! Please login.')
                    return redirect(url_for('account'))
            except sqlite3.IntegrityError:
                flash('Username already exists. Please choose a different username.')
                return redirect(url_for('account'))

        elif form_type == 'login':
            username = request.form['username']
            password = request.form['password']

            with sqlite3.connect('users.db', timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, password, role, profile_pic FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()

                if user and check_password_hash(user[2], password):
                    session['user'] = {
                        'id': user[0],
                        'username': user[1],
                        'role': user[3],
                        'profile_pic': user[4]
                    }
                    flash('Login successful!')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid username or password.', 'danger')
                    return redirect(url_for('account'))  

    return render_template('account.html')

def is_admin():
    return session.get('user') and session['user'].get('role') == 'admin'

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('index'))
    
    ##Uploaded PDF files
    if request.method == 'POST':
        pdf = request.files.get('pdf_file')
        if not pdf or not allowed_file(pdf.filename):
            flash('Invalid file type. Please upload a PDF file.', 'danger')
        elif pdf:
            filename = secure_filename(pdf.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf.save(file_path)
            flash(f"{filename} uploaded successfully.", 'success')
        else:
            flash('No file selected.', 'danger')

    pdf_files = os.listdir(app.config['UPLOAD_FOLDER'])

    with sqlite3.connect('users.db', timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role FROM users')
        users = cursor.fetchall()

        return render_template('admin.html', users=users, pdf_files=pdf_files)

@app.route('/delete_pdf/<filename>', methods=['POST'])
def delete_pdf(filename):
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'PDF file "{filename}" deleted successfully.')
    else:
        flash(f'PDF file "{filename}" not found.', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))
    
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('index'))
    
    try:
        with sqlite3.connect('users.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()

            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('admin_dashboard'))
            
            if user[0] == 'admin':
                flash('Cannot delete the admin user.', 'danger')
                return redirect(url_for('admin_dashboard'))
            
        ##Deleting users profile 
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        flash('User deleted successfully.', 'success')
        
    except sqlite3.Error as e:
        flash(f'An error occurred while deleting the user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/promote_user/<int:user_id>', methods=['POST'])
def promote_user(user_id):
    if not is_admin():
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('index'))
    
    try:
        with sqlite3.connect('users.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()

            if not user:
                flash('User not found.', 'danger')
            elif user[0] == 'admin':
                flash('User is already an admin.', 'warning')
            else:
                cursor.execute('UPDATE users SET role = ? WHERE id = ?', ('admin', user_id))
                conn.commit()
                flash('User promoted to admin successfully.', 'success')
    except sqlite3.Error as e:
        flash(f'An error occurred while promoting the user: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))       


if __name__ == '__main__':
    init_user_db()
    app.run(debug=True)