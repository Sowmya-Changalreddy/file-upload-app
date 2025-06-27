from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize DB
def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS files (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            filename TEXT,
                            extension TEXT,
                            upload_date TEXT,
                            description TEXT
                        )""")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        if file:
            filename = file.filename
            extension = os.path.splitext(filename)[1]
            upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            # Save metadata to SQLite
            with sqlite3.connect("database.db") as conn:
                conn.execute("INSERT INTO files (filename, extension, upload_date, description) VALUES (?, ?, ?, ?)",
                             (filename, extension, upload_date, description))
                conn.commit()
            return redirect(url_for('upload_file'))

    # Fetch all uploaded files
    with sqlite3.connect("database.db") as conn:
        cursor = conn.execute("SELECT filename, extension, upload_date, description FROM files ORDER BY id DESC")
        files = cursor.fetchall()

    return render_template('upload.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
