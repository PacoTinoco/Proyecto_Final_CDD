from flask import Blueprint, render_template, request, redirect, url_for, session
from db_models.model_user import create_user, get_user_by_username

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/create_user', methods=['GET', 'POST'])
def create_user_route():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if create_user(username, email, password):
            return redirect(url_for('auth_bp.index'))
        return "Error: Usuario ya existe o datos no válidos"
    return render_template('create_user.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        user = get_user_by_username(username_or_email)
        if user and password == user.password:
            session['username'] = user.username
            session['user_id'] = str(user.id)  # Guarda el ID del usuario en la sesión
            return redirect(url_for('user_bp.interface'))
        return "Credenciales incorrectas"
    return render_template('login.html')



@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth_bp.index'))

