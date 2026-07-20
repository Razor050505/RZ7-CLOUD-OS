import os
import json
import base64
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

vault_bp = Blueprint('vault', __name__)

# Konfigurasi path database vault
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
VAULT_DB_PATH = os.path.join(BASE_DIR, 'database', 'vaults.json')

# Secret key untuk obfuscation (Di production nanti ganti ke AES-256)
OBFUSCATION_KEY = b'rz7-cloud-os-v04-android-ide-safe-key=='

def _xor_obfuscate(data: bytes, key: bytes) -> bytes:
    """XOR simple obfuscation compatible with all Python environments"""
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def encrypt_key(plain_text: str) -> str:
    """Encrypt API key using Base64 + XOR"""
    encrypted = _xor_obfuscate(plain_text.encode(), OBFUSCATION_KEY)
    return base64.b64encode(encrypted).decode()

def decrypt_key(encrypted_text: str) -> str:
    """Decrypt API key from Base64 + XOR"""
    try:
        encrypted = base64.b64decode(encrypted_text.encode())
        return _xor_obfuscate(encrypted, OBFUSCATION_KEY).decode()
    except Exception:
        return ""

def load_vault_db():
    """Memuat database vault dari file JSON"""
    if not os.path.exists(VAULT_DB_PATH):
        return {}
    with open(VAULT_DB_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_vault_db(data):
    """Menyimpan database vault ke file JSON"""
    os.makedirs(os.path.dirname(VAULT_DB_PATH), exist_ok=True)
    with open(VAULT_DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)

@vault_bp.route('/vault')
@login_required
def vault_page():
    """Menampilkan halaman API Vault Manager"""
    db = load_vault_db()
    user_vault = db.get(current_user.id, [])
    
    # Dekripsi semua entry untuk ditampilkan (dengan masking)
    decrypted_entries = []
    for entry in user_vault:
        plain_key = decrypt_key(entry['encrypted_key'])
        masked_key = plain_key[:8] + '****' + plain_key[-4:] if len(plain_key) > 12 else '****'
        decrypted_entries.append({
            'id': entry['id'],
            'name': entry['name'],
            'masked_key': masked_key,
            'created_at': entry['created_at']
        })
            
    return render_template('vault.html', entries=decrypted_entries)

@vault_bp.route('/api/vault/add', methods=['POST'])
@login_required
def add_vault_entry():
    """Menambahkan entry baru dengan obfuscation"""
    data = request.get_json()
    name = data.get('name', '').strip()
    api_key = data.get('api_key', '').strip()
    
    if not name or not api_key:
        return jsonify({'error': 'Nama dan API Key wajib diisi'}), 400
    
    # Obfuscate API Key sebelum disimpan
    encrypted_key = encrypt_key(api_key)
    
    db = load_vault_db()
    if current_user.id not in db:
        db[current_user.id] = []
    
    new_entry = {
        'id': str(len(db[current_user.id]) + 1),
        'name': name,
        'encrypted_key': encrypted_key,
        'created_at': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    db[current_user.id].append(new_entry)
    save_vault_db(db)
    
    return jsonify({'message': 'API Key berhasil disimpan dengan proteksi'}), 200

@vault_bp.route('/api/vault/delete/<entry_id>', methods=['DELETE'])
@login_required
def delete_vault_entry(entry_id):
    """Menghapus entry vault milik user sendiri"""
    db = load_vault_db()
    user_vault = db.get(current_user.id, [])
    
    new_vault = [e for e in user_vault if e['id'] != entry_id]
    
    if len(new_vault) == len(user_vault):
        return jsonify({'error': 'Entry tidak ditemukan'}), 404
    
    db[current_user.id] = new_vault
    save_vault_db(db)
    
    return jsonify({'message': 'Entry berhasil dihapus'}), 200

@vault_bp.route('/api/vault/reveal/<entry_id>')
@login_required
def reveal_vault_entry(entry_id):
    """Dekripsi dan kembalikan API Key asli"""
    db = load_vault_db()
    user_vault = db.get(current_user.id, [])
    
    entry = next((e for e in user_vault if e['id'] == entry_id), None)
    if not entry:
        return jsonify({'error': 'Entry tidak ditemukan'}), 404
    
    plain_key = decrypt_key(entry['encrypted_key'])
    if not plain_key:
        return jsonify({'error': 'Gagal mendekripsi kunci'}), 500
        
    return jsonify({'api_key': plain_key}), 200
		