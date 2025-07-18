from flask import Flask, render_template, request, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder to store uploaded photos
app.config['UPLOAD_FOLDER'] = 'static/uploads'
MAX_FILES = 50  # Limit the number of photos to keep

# File to save data
DATA_FILE = 'data.json'

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Create data.json file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Clean up old files in uploads
def cleanup_uploads():
    files = sorted(
        [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in os.listdir(app.config['UPLOAD_FOLDER'])],
        key=os.path.getctime
    )
    while len(files) > MAX_FILES:
        os.remove(files[0])
        files.pop(0)

# Load people data from JSON
def load_people():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Save people data to JSON
def save_people(people):
    with open(DATA_FILE, 'w') as f:
        json.dump(people, f)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Lost person form page
@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if request.method == 'POST':
        people = load_people()
        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        cleanup_uploads()  # Clean older photos to avoid 507

        # Generate a unique ID
        new_id = max([p["id"] for p in people], default=-1) + 1

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
        return redirect(url_for('found'))

    return render_template('lost_form.html')

# Show all found people
@app.route('/found')
def found():
    people = load_people()
    return render_template('found.html', people=people)

# Lost & Found hub page (optional routing)
@app.route('/lostfound')
def lostfound():
    return render_template('index.html')

# Individual detail page
@app.route('/detail/<int:person_id>')
def detail(person_id):
    people = load_people()
    person = next((p for p in people if p['id'] == person_id), None)
    return render_template('detail.html', person=person)

# Run the app
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port, debug=True)





