import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager

# Import Blueprints
from routes.auth import auth_bp
from routes.storage import storage_bp
from routes.vault import vault_bp

# Inisialisasi App
# PENTING: Arahkan template_folder ke 'frontend' dan static_folder ke 'static'
app = Flask(__name__, 
            template_folder='frontend', 
            static_folder='static')

app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key-change-this-in-production')

# Konfigurasi Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(storage_bp)
app.register_blueprint(vault_bp)

# User Loader (Contoh sederhana, sesuaikan dengan logic auth.py Anda)
@login_manager.user_loader
def load_user(user_id):
    # Implementasi load user Anda di sini
    pass

if __name__ == '__main__':
    app.run(debug=True)
	