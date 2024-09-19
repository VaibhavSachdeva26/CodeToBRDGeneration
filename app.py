from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Retrieve the text input for project requirements
        project_requirements = request.form['project_requirements']

        # Handle file uploads
        uploaded_files = request.files.getlist('files[]')
        saved_files = []
        for file in uploaded_files:
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                saved_files.append(file_path)

        # Here you would process the input and generate the BRD document using LLMs or some AI model

        # For now, let's assume you have generated a BRD and saved it as 'BRD_document.txt'
        with open('BRD_document.txt', 'w') as f:
            f.write(f"Generated BRD based on requirements: {project_requirements}\n")
            f.write(f"Attached files: {', '.join(saved_files)}\n")

        return redirect(url_for('view_brd'))

    return render_template('index.html')


# View/Edit/Download the BRD Document
@app.route('/brd', methods=['GET', 'POST'])
def view_brd():
    brd_content = ''
    with open('BRD_document.txt', 'r') as f:
        brd_content = f.read()

    if request.method == 'POST':
        # Save edits made to the BRD document
        new_brd_content = request.form['brd_content']
        with open('BRD_document.txt', 'w') as f:
            f.write(new_brd_content)

        return redirect(url_for('view_brd'))

    return render_template('brd.html', brd_content=brd_content)


# Download the BRD document
@app.route('/download_brd')
def download_brd():
    path = 'BRD_document.txt'
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
