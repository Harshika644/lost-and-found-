from flask import Flask, render_template, request, redirect, session
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

# ==============================
# FILE CONFIG
# ==============================
USER_FILE = 'users.json'
PEOPLE_FILE = 'people.json'
UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create folders/files if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

for file in [USER_FILE, PEOPLE_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)

# ==============================
# USER FUNCTIONS
# ==============================
def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ==============================
# PEOPLE FUNCTIONS
# ==============================
def load_people():
    try:
        with open(PEOPLE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_people(people):
    with open(PEOPLE_FILE, "w") as f:
        json.dump(people, f, indent=4)

# ==============================
# ROUTES
# ==============================

@app.route('/')
def home():
    return render_template('index.html')

# ------------------------------
# REGISTER
# ------------------------------
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

# ------------------------------
# LOGIN
# ------------------------------
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

# ------------------------------
# LOGOUT
# ------------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ------------------------------
# LOST (ADD PERSON)
# ------------------------------
@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        people = load_people()

        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(path)

        new_id = max([p.get("id", 0) for p in people], default=0) + 1

        new_person = {
            "id": new_id,
            "name": request.form['name'],
            "age": request.form['age'],
            "location": request.form['location'],
            "details": request.form['details'],
            "photo": '/' + path.replace("\\", "/")
        }

        people.append(new_person)
        save_people(people)

        return redirect('/found')

    return render_template('lost_form.html')

# ------------------------------
# FOUND PAGE
# ------------------------------
@app.route('/found')
def found():
    if 'user' not in session:
        return redirect('/login')

    people = load_people()
    return render_template('found.html', people=people)

# ------------------------------
# DETAIL PAGE
# ------------------------------
@app.route('/detail/<int:person_id>')
def detail(person_id):
    people = load_people()
    person = next((p for p in people if p['id'] == person_id), None)
    return render_template('detail.html', person=person)

# ------------------------------
# RUN (Render compatible)
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
