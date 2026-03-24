from flask import Flask, render_template, request, redirect, session, url_for
import json

app = Flask(__name__)
app.secret_key = "secret123"

# ==============================
# Load users
# ==============================
def load_users():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return []

# ==============================
# Save users
# ==============================
def save_users(users):
    with open("data.json", "w") as f:
        json.dump(users, f, indent=4)

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

        # check if user already exists
        for user in users:
            if user.get('email') == email:
                return "⚠️ User already exists! Please login."

        # add new user
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

        # if login fails → go to register
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
# Protected Routes
# ==============================
@app.route('/lost')
def lost():
    if 'user' not in session:
        return redirect('/login')
    return render_template('lost_form.html')

@app.route('/found')
def found():
    if 'user' not in session:
        return redirect('/login')
    return render_template('found.html')

# ==============================
# Run App
# ==============================
if __name__ == '__main__':
    app.run(debug=True)