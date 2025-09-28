from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Ordner für hochgeladene Dateien
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Startseite mit Upload-Formular
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('pdf_file')
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return f'''
                <p>Datei erfolgreich hochgeladen!</p>
                <a href="/uploads/{filename}" target="_blank">PDF anzeigen</a>
            '''
        else:
            return '<p>Bitte nur PDF-Dateien hochladen.</p>'
    return '''
        <h2>PDF hochladen</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="pdf_file" accept=".pdf">
            <button type="submit">Hochladen</button>
        </form>
    '''

# Route zum Abrufen der PDF-Dateien
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Port-Handling für Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
