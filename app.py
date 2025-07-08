from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
SVG_FOLDER = 'static/svg_layers/'
ALLOWED_EXTENSIONS = {'kicad_pcb'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SVG_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def export_svg_layers(pcb_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    subprocess.run([
        "kicad-cli", "pcb", "export", "svg", pcb_path,
        "--layers", "Edge.Cuts,F.Silkscreen,User.Drawings,F.Mask",
        "--mode-multi",
        "--output", output_dir,
        "--black-and-white",
        "--exclude-drawing-sheet",
        "--page-size-mode", "2"
    ])



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

            # Clear previous SVGs
            for f in os.listdir(SVG_FOLDER):
                os.remove(os.path.join(SVG_FOLDER, f))

            # Export SVG layers
            export_svg_layers(upload_path, SVG_FOLDER)
            return redirect(url_for('layers'))

    return render_template('index.html')

@app.route('/layers')
def layers():
    svg_files = [f for f in os.listdir(SVG_FOLDER) if f.endswith('.svg')]
    return render_template('layers.html', svg_files=svg_files)

@app.route('/svg/<filename>')
def serve_svg(filename):
    return send_from_directory(SVG_FOLDER, filename)
