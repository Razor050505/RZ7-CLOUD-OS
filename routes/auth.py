from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required, current_user
import json
import os

auth_bp = Blueprint('auth', __name__)

# Path ke file users.json
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'users.json')

def get_users():
    """Membaca data user dari JSON"""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, 'r') as f:
        return json.load(f)

class User:
    def __init__(self, username):
        self.id = username
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = get_users()
        for user_data in users:
            if user_data['username'] == username and user_data['password'] == password:
                user = User(username)
                login_user(user)
                flash('Login berhasil! Selamat datang, Razor.', 'success')
                return redirect(url_for('dashboard'))
        
        flash('Username atau password salah.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Jika GET, tampilkan halaman login (kita akan buat HTML-nya nanti)
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))
	