from flask import Blueprint, render_template, session, redirect, url_for, request
from models.model_user import get_user_by_username, User
from models.model_api_key import APIKey
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/interface')
def interface():
    if 'username' in session:
        user = get_user_by_username(session['username'])
        api_keys = user.api_keys  # Recuperar las API keys
        return render_template('interface.html', user=user, api_keys=api_keys)
    return redirect(url_for('auth_bp.login_route'))

@user_bp.route('/profile')
def profile():
    if 'username' in session:
        user = get_user_by_username(session['username'])
        api_keys = user.api_keys  # Obtener las claves actualizadas
        return render_template('profile.html', user=user, api_keys=api_keys)  # Asegúrate de pasar las api_keys
    return redirect(url_for('auth_bp.login_route'))



@user_bp.route('/save_api_key', methods=['POST'])
def save_api_key():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth_bp.login_route'))

    api_key = request.form['api_key']
    broker = request.form['broker']

    # Buscar el objeto User para la referencia
    user = User.objects.get(id=user_id)

    # Guardar la nueva clave de API
    new_api_key = APIKey(user=user, api_key=api_key, broker=broker)
    new_api_key.save()

    user.api_keys.append(new_api_key)  # Añadir la clave a la lista de claves del usuario
    user.save()

    return redirect(url_for('user_bp.profile'))


@user_bp.route('/delete_api_key/<id>', methods=['POST'])
def delete_api_key(id):
    # Eliminar la clave de API
    api_key = APIKey.objects(id=id).first()  # Busca primero la API key para eliminarla del usuario
    if api_key:
        user = User.objects.get(id=session.get('user_id'))
        user.api_keys.remove(api_key)
        user.save()
        api_key.delete()
    return redirect(url_for('user_bp.profile'))

@user_bp.route('/select_api_key', methods=['POST'])
def select_api_key():
    api_key_id = request.form['api_key_id']
    # Aquí puedes almacenar la API key seleccionada en la sesión o manejarla como prefieras
    api_key = APIKey.objects.get(id=api_key_id)

    # Guardar la API key seleccionada en la sesión
    session['selected_api_key'] = api_key.api_key

    return redirect(url_for('user_bp.interface'))

@user_bp.route('/select_stock', methods=['POST'])
def select_stock():
    stock = request.form.get('stock')
    # Aquí puedes manejar la lógica para el stock seleccionado
    print(f"Stock seleccionado: {stock}")  # Solo para verificar
    return redirect(url_for('user_bp.index'))


### 10-02-24
@user_bp.route('/start_trading', methods=['POST'])
def start_trading():
    algorithm = request.form['algorithm']
    api_key_id = request.form['api_key_id']
    amount = request.form['amount']
    units = request.form['units']
    duration = request.form['duration']

    # Aquí colocarías la lógica para iniciar el proceso de trading
    # Puedes usar un temporizador para ejecutar las órdenes basadas en la duración

    return redirect(url_for('user_bp.interface'))


@user_bp.route('/stop_trading', methods=['POST'])
def stop_trading():
    # Lógica para detener el proceso de trading
    return redirect(url_for('user_bp.interface'))
