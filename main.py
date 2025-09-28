from flask import Flask, request, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Ordner für hochgeladene Dateien
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Startseite mit Upload-Formular und Dateiliste
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = ''
    if request.method == 'POST':
        file = request.files.get('pdf_file')
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            message = f'<p>Datei <strong>{filename}</strong> erfolgreich hochgeladen!</p>'
        else:
            message = '<p>Bitte nur PDF-Dateien hochladen.</p>'

    # Liste aller Dateien im Upload-Ordner
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    file_links = ''
    for f in files:
        file_links += f'''
            <li>
                {f} –
                <a href="/uploads/{f}" target="_blank">Anzeigen</a> |
                <a href="/download/{f}">Herunterladen</a>
            </li>
        '''

    return f'''
        <h2>PDF hochladen</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="pdf_file" accept=".pdf">
            <button type="submit">Hochladen</button>
        </form>
        {message}
        <h3>Hochgeladene Dateien:</h3>
        <ul>
            {file_links if file_links else '<li>Keine Dateien vorhanden.</li>'}
        </ul>
    '''

# Route zum Anzeigen der PDF-Dateien
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route zum Herunterladen der PDF-Dateien
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Port-Handling für Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)