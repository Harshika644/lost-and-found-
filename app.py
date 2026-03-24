from flask import Flask, render_template, request, redirect, session, url_for
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

# ==============================
# Config
# ==============================
app.config['UPLOAD_FOLDER'] = 'static/uploads'
DATA_FILE = 'data.json'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# ==============================
# Load & Save Users
# ==============================
def load_users():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open("data.json", "w") as f:
        json.dump(users, f, indent=4)

# ==============================
# Load & Save People
# ==============================
def load_people():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_people(people):
    with open(DATA_FILE, 'w') as f:
        json.dump(people, f)

# ==============================
# Home
# ==============================
@app.route('/')
def home():
    return render_template('index.html')

# ==============================
# Register
# ==============================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        for user in users:
            if user.get('email') == email:
                return "User already exists!"

        users.append({
            "name": name,
            "email": email,
            "password": password
        })

        save_users(users)
        return redirect('/login')

    return render_template('register.html')

# ==============================
# Login
# ==============================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()

        email = request.form['email']
        password = request.form['password']

        for user in users:
            if user.get('email') == email and user.get('password') == password:
                session['user'] = user.get('name')
                return redirect('/')

        return redirect('/register')

    return render_template('login.html')

# ==============================
# Logout
# ==============================
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ==============================
# Protected Lost Form
# ==============================
@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        people = load_people()

        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        new_id = max([p.get("id", 0) for p in people], default=0) + 1

        new_person = {
            "id": new_id,
            "name": request.form['name'],
            "age": request.form['age'],
            "location": request.form['location'],
            "details": request.form['details'],
            "photo": '/' + photo_path.replace("\\", "/")
        }

        people.append(new_person)
        save_people(people)

        return redirect('/found')

    return render_template('lost_form.html')

# ==============================
# Protected Found Page
# ==============================
@app.route('/found')
def found():
    if 'user' not in session:
        return redirect('/login')

    people = load_people()
    return render_template('found.html', people=people)

# ==============================
# Detail Page
# ==============================
@app.route('/detail/<int:person_id>')
def detail(person_id):
    people = load_people()
    person = next((p for p in people if p['id'] == person_id), None)
    return render_template('detail.html', person=person)

# ==============================
# Run App (Render FIX ✅)
# ==============================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)