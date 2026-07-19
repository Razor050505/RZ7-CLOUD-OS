from flask import Flask, render_template, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from routes.auth import auth_bp
import os

app = Flask(__name__, template_folder='frontend', static_folder='frontend')
app.secret_key = 'rz7-secret-key-change-later' # Ganti dengan secret key yang aman nanti

# Inisialisasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprint
app.register_blueprint(auth_bp)

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
    return render_template('index.html') # Mengarah ke frontend/index.html yang sudah ada

@app.route('/status')
def status():
    return jsonify({"status": "online", "version": "v0.2 Alpha"})

if __name__ == '__main__':
    app.run(debug=True)
	