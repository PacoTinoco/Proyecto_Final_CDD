from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, current_app
from db_models.model_user import get_user_by_username, User
from db_models.model_api_key import APIKey
import requests
import logging
import tempfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

user_bp = Blueprint('user_bp', __name__)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_trading_params(amount, holding_days):
    try:
        amount = float(amount)
        holding_days = int(holding_days)
        
        if amount <= 0:
            return False, "La cantidad de dinero debe ser mayor que 0"
        if holding_days <= 0:
            return False, "Los días de holding deben ser mayor que 0"
            
        return True, None
    except ValueError:
        return False, "Valores inválidos para cantidad de dinero o días de holding"

@user_bp.route('/interface', methods=['GET', 'POST'])
def interface():
    if 'username' in session:
        user = get_user_by_username(session['username'])
        api_keys = user.api_keys  # Recuperar las API keys

        if request.method == 'POST':
            predictions = send_csv()
            if predictions:
                return render_template('interface.html', user=user, api_keys=api_keys, predictions=predictions)
            else:
                return render_template('interface.html', user=user, api_keys=api_keys)
        else:
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

@user_bp.route('/upload_csv', methods=['POST'])
def send_csv():
    temp_file = None
    try:
        logger.debug("=== Iniciando proceso de upload_csv ===")

        # Validar archivo
        if 'file' not in request.files:
            logger.error("No se encontró archivo en la solicitud")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            logger.error("El archivo esta vacio o no esta en un formato valido")
            return jsonify({'error': 'Invalid file'}), 400

        # Obtener y validar parámetros de trading
        amount = request.form.get('amount', '0')
        holding_days = request.form.get('holding_days', '0')
        
        is_valid, error_message = validate_trading_params(amount, holding_days)
        if not is_valid:
            return jsonify({'error': error_message}), 400

        if file and allowed_file(file.filename):
            try:
                # Crear archivo temporal
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
                file.save(temp_file.name)
                temp_file.close()

                # Obtener modelo seleccionado
                model = request.form.get('model', 'amazon')
                logger.debug(f"Modelo seleccionado: {model}")
                logger.debug(f"Cantidad a invertir: {amount}")
                logger.debug(f"Días de holding: {holding_days}")

                # Enviar al orquestador
                orchestrator_url = 'http://orchestrator:5002/upload'
                
                with open(temp_file.name, 'rb') as f:
                    files = {'file': (file.filename, f, 'text/csv')}
                    data = {
                        'model': model,
                        'amount': amount,
                        'holding_days': holding_days
                    }

                    logger.debug("Realizando solicitud POST al orquestador")
                    response = requests.post(orchestrator_url, files=files, data=data)

                    logger.debug(f"Respuesta del orquestador - Status: {response.status_code}")
                    logger.debug(f"Respuesta del orquestador - Contenido: {response.text}")

                    if response.status_code == 200:
                        predictions = response.json()
                        return jsonify(predictions)
                    else:
                        logger.error(f"Error del orquestador: {response.text}")
                        return jsonify({'error': f'Error del orquestador: {response.text}'}), response.status_code

            except Exception as e:
                logger.error(f"Error en el procesamiento del archivo: {str(e)}", exc_info=True)
                return jsonify({'error': f'Error detallado: {str(e)}'}), 500
            finally:
                # Limpiar archivo temporal
                if temp_file is not None:
                    try:
                        import os
                        if os.path.exists(temp_file.name):
                            os.unlink(temp_file.name)
                    except Exception as e:
                        logger.warning(f"Error al eliminar archivo temporal: {str(e)}")

        logger.error("Tipo de archivo no permitido")
        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        logger.error(f"Error general en upload_csv: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error general: {str(e)}'}), 500