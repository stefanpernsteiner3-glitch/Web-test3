from flask import Flask, request, redirect, url_for, send_from_directory, session
import os
import time
from werkzeug.utils import secure_filename

# 🔧 Konfiguration
app = Flask(__name__)
app.secret_key = 'Main_schlüssel'  # Für Sitzungsverwaltung
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Max. 10 MB Upload

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx'}
PASSWORD = 'perniws'  # Dein Passwort

# 🔐 Login mit exponentieller Wartezeit
@app.route('/', methods=['GET', 'POST'])
def login():
    fail_count = session.get('fail_count', 0)
    last_fail = session.get('last_fail', 0)
    now = time.time()

    # Wartezeit berechnen
    if fail_count > 0:
        wait_time = min(2 ** fail_count, 300)  # Max. 5 Minuten
        if now - last_fail < wait_time:
            remaining = int(wait_time - (now - last_fail))
            return f'<p>Zu viele Fehlversuche. Bitte warte {remaining} Sekunden.</p>'

    if request.method == 'POST':
        entered = request.form.get('password')
        if entered == PASSWORD:
            session['authenticated'] = True
            session['fail_count'] = 0
            return redirect(url_for('upload_file'))
        else:
            session['fail_count'] = fail_count + 1
            session['last_fail'] = now
            return '<p>Falsches Passwort!</p>'

    return '''
        <h2>Passwort erforderlich</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Passwort eingeben">
            <button type="submit">Login</button>
        </form>
    '''

# 📤 Upload-Seite mit Dateiliste und Löschfunktion
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    message = ''
    if request.method == 'POST':
        file = request.files.get('pdf_file')
        if file:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                message = f'<p>Datei <strong>{filename}</strong> erfolgreich hochgeladen!</p>'
            else:
                message = '<p>Ungültiger Dateityp. Erlaubt sind: PDF, Word, Excel, PowerPoint.</p>'

    # Dateiliste anzeigen
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    file_links = ''
    for f in files:
        file_links += f'''
            <li>
                {f} –
                <a href="/uploads/{f}" target="_blank">Anzeigen</a> |
                <a href="/download/{f}">Herunterladen</a>
                <form method="POST" action="/delete/{f}" style="display:inline;">
                    <button type="submit">Löschen</button>
                </form>
            </li>
        '''

    return f'''
        <h2>Datei hochladen</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="pdf_file" accept=".pdf,.docx,.pptx,.xlsx">
            <button type="submit">Hochladen</button>
        </form>
        {message}
        <h3>Hochgeladene Dateien:</h3>
        <ul>
            {file_links if file_links else '<li>Keine Dateien vorhanden.</li>'}
        </ul>
        <a href="/logout">Logout</a>
    '''

# 📂 Datei anzeigen
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 📥 Datei herunterladen
@app.route('/download/<filename>')
def download_file(filename):
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# 🗑️ Datei löschen
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return redirect(url_for('upload_file'))
    else:
        return f'<p>Datei nicht gefunden.</p><a href="/upload">Zurück</a>'

# 🚪 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 🚀 Port-Handling für Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)