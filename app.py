from flask import Flask, render_template, jsonify, redirect, url_for, send_from_directory
from flask_login import LoginManager, current_user, login_required
from routes.auth import auth_bp
from routes.storage import storage_bp  # Import blueprint storage baru
import os

# Konfigurasi path yang kompatibel dengan Render
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path='/static'
)
app.secret_key = 'rz7-secret-key-change-later'

# Inisialisasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprint (Auth & Storage)
app.register_blueprint(auth_bp)
app.register_blueprint(storage_bp)  # Register blueprint storage

# User Loader untuk Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from routes.auth import User
    return User(user_id)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"[ERROR] Template not found, trying fallback: {e}")
        index_path = os.path.join(TEMPLATE_DIR, 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                return f.read()
        return "Dashboard file missing!", 500

@app.route('/status')
def status():
    return jsonify({"status": "online", "version": "v0.3 Alpha - Cloud Storage Active"})

if __name__ == '__main__':
    app.run(debug=True)
	