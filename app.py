import os
from flask import Flask, render_template, jsonify, redirect, url_for, Response
from flask_login import LoginManager, current_user, login_required

# Import Blueprints
from routes.auth import auth_bp
from routes.storage import storage_bp
from routes.vault import vault_bp

# Konfigurasi Path Absolut (Kunci agar Render tidak bingung)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend')

# Inisialisasi Flask App
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path='/static'
)
app.secret_key = 'rz7-secret-key-change-later-in-production'

# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(storage_bp)
app.register_blueprint(vault_bp)

# User Loader untuk Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from routes.auth import User
    return User(user_id)

# Helper function: Fallback baca file HTML manual jika render_template gagal
def safe_render_template(template_name, **context):
    try:
        return render_template(template_name, **context)
    except Exception as e:
        print(f"[TEMPLATE ERROR] Gagal render {template_name}: {str(e)}")
        # Coba baca file secara manual sebagai fallback
        template_path = os.path.join(TEMPLATE_DIR, template_name)
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            # Render Jinja2 manual
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
            template = env.get_template(template_name)
            return template.render(**context)
        return Response(f"Template {template_name} not found!", status=404)

# Routes Utama
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return safe_render_template('index.html')

@app.route('/status')
def status():
    return jsonify({"status": "online", "version": "v0.4 Alpha - API Vault Active"})

if __name__ == '__main__':
    app.run(debug=True)
	