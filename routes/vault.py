import os
import json
import base64
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

vault_bp = Blueprint('vault', __name__)

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
VAULT_DB_PATH = os.path.join(BASE_DIR, 'database', 'vaults.json')
OBFUSCATION_KEY = b'rz7-cloud-os-v04-android-ide-safe-key=='

def _xor_obfuscate(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def encrypt_key(plain_text: str) -> str:
    return base64.b64encode(_xor_obfuscate(plain_text.encode(), OBFUSCATION_KEY)).decode()

def decrypt_key(encrypted_text: str) -> str:
    try:
        encrypted = base64.b64decode(encrypted_text.encode())
        return _xor_obfuscate(encrypted, OBFUSCATION_KEY).decode()
    except Exception:
        return ""

def load_vault_db():
    if not os.path.exists(VAULT_DB_PATH):
        os.makedirs(os.path.dirname(VAULT_DB_PATH), exist_ok=True)
        save_vault_db({})
        return {}
    with open(VAULT_DB_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_vault_db(data):
    os.makedirs(os.path.dirname(VAULT_DB_PATH), exist_ok=True)
    with open(VAULT_DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)

@vault_bp.route('/vault')
@login_required
def vault_page():
    try:
        db = load_vault_db()
        user_vault = db.get(current_user.id, [])
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
    except Exception as e:
        print(f"[VAULT ERROR]: {str(e)}")
        return render_template('vault.html', entries=[]), 200

@vault_bp.route('/api/vault/add', methods=['POST'])
@login_required
def add_vault_entry():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        api_key = data.get('api_key', '').strip()
        
        if not name or not api_key:
            return jsonify({'error': 'Nama dan API Key wajib diisi'}), 400
        
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
        return jsonify({'message': 'API Key berhasil disimpan'}), 200
    except Exception as e:
        print(f"[ADD VAULT ERROR]: {str(e)}")
        return jsonify({'error': 'Gagal menyimpan data'}), 500

@vault_bp.route('/api/vault/delete/<entry_id>', methods=['DELETE'])
@login_required
def delete_vault_entry(entry_id):
    try:
        db = load_vault_db()
        user_vault = db.get(current_user.id, [])
        new_vault = [e for e in user_vault if e['id'] != entry_id]
        
        if len(new_vault) == len(user_vault):
            return jsonify({'error': 'Entry tidak ditemukan'}), 404
            
        db[current_user.id] = new_vault
        save_vault_db(db)
        return jsonify({'message': 'Entry berhasil dihapus'}), 200
    except Exception as e:
        print(f"[DELETE VAULT ERROR]: {str(e)}")
        return jsonify({'error': 'Gagal menghapus data'}), 500

@vault_bp.route('/api/vault/reveal/<entry_id>')
@login_required
def reveal_vault_entry(entry_id):
    try:
        db = load_vault_db()
        user_vault = db.get(current_user.id, [])
        entry = next((e for e in user_vault if e['id'] == entry_id), None)
        
        if not entry:
            return jsonify({'error': 'Entry tidak ditemukan'}), 404
            
        plain_key = decrypt_key(entry['encrypted_key'])
        if not plain_key:
            return jsonify({'error': 'Gagal mendekripsi kunci'}), 500
            
        return jsonify({'api_key': plain_key}), 200
    except Exception as e:
        print(f"[REVEAL VAULT ERROR]: {str(e)}")
        return jsonify({'error': 'Gagal menampilkan kunci'}), 500
			