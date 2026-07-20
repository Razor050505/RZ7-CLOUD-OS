import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

storage_bp = Blueprint('storage', __name__)

# Konfigurasi path upload dinamis berdasarkan username
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB quota per user
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx', 'zip', 'rar', 'mp3', 'mp4'}

def allowed_file(filename):
    """Cek apakah ekstensi file diizinkan"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_folder():
    """Mendapatkan path folder khusus untuk user yang sedang login"""
    user_folder = os.path.join(UPLOAD_FOLDER, current_user.id)
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

@storage_bp.route('/storage')
@login_required
def storage_page():
    """Menampilkan halaman file manager"""
    user_folder = get_user_folder()
    files = []
    
    if os.path.exists(user_folder):
        for f in sorted(os.listdir(user_folder)):  # Sort by name
            f_path = os.path.join(user_folder, f)
            if os.path.isfile(f_path):
                size_mb = round(os.path.getsize(f_path) / (1024 * 1024), 2)
                files.append({
                    'name': f,
                    'size': size_mb,
                    'modified': os.path.getmtime(f_path)
                })
    
    # Hitung total penggunaan storage
    total_used = sum(f['size'] for f in files)
    quota_percent = min(round((total_used / 50) * 100, 1), 100)
    
    return render_template('storage.html', 
                         files=files, 
                         total_used=round(total_used, 2),
                         quota_percent=quota_percent)

@storage_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle upload file dengan validasi keamanan lengkap"""
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang dipilih'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nama file kosong'}), 400
    
    # Validasi tipe file
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipe file tidak diizinkan'}), 400
    
    # Validasi ukuran file
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': 'File melebihi batas 50MB'}), 413
    
    # Cek quota user sebelum upload
    user_folder = get_user_folder()
    current_usage = sum(
        os.path.getsize(os.path.join(user_folder, f)) 
        for f in os.listdir(user_folder) 
        if os.path.isfile(os.path.join(user_folder, f))
    )
    
    if current_usage + file_size > MAX_FILE_SIZE:
        return jsonify({'error': 'Kuota penyimpanan penuh'}), 413
    
    # Sanitasi nama file & hindari overwrite
    filename = secure_filename(file.filename)
    filepath = os.path.join(user_folder, filename)
    
    counter = 1
    original_name = filename
    while os.path.exists(filepath):
        name, ext = os.path.splitext(original_name)
        filepath = os.path.join(user_folder, f"{name}_{counter}{ext}")
        counter += 1
    
    file.save(filepath)
    return jsonify({'message': f'File {os.path.basename(filepath)} berhasil diupload'}), 200

@storage_bp.route('/api/download/<filename>')
@login_required
def download_file(filename):
    """Download file milik user sendiri saja dengan sanitasi path"""
    user_folder = get_user_folder()
    safe_filename = secure_filename(filename)
    safe_path = os.path.join(user_folder, safe_filename)
    
    # Security check: pastikan file berada di dalam folder user
    if not os.path.exists(safe_path) or not safe_path.startswith(user_folder):
        return jsonify({'error': 'File tidak ditemukan atau akses ditolak'}), 404
    
    return send_from_directory(user_folder, safe_filename, as_attachment=True)

@storage_bp.route('/api/delete/<filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    """Hapus file milik user sendiri saja dengan sanitasi path"""
    user_folder = get_user_folder()
    safe_filename = secure_filename(filename)
    safe_path = os.path.join(user_folder, safe_filename)
    
    if not os.path.exists(safe_path) or not safe_path.startswith(user_folder):
        return jsonify({'error': 'File tidak ditemukan atau akses ditolak'}), 404
    
    os.remove(safe_path)
    return jsonify({'message': f'File {safe_filename} berhasil dihapus'}), 200
			