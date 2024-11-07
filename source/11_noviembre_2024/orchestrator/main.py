from flask import Flask, request, jsonify
import requests
import pandas as pd
import logging
import traceback

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def health_check():
    """Ruta de verificación de estado"""
    return jsonify({'status': 'Orchestrator API is running'})

def send_results_to_ui(predictions):
    try:
        ui_results_url = 'http://localhost:5000/interface'
        payload = {'predictions': predictions}
        response = requests.post(ui_results_url, json=payload)
        if response.status_code == 200:
            logger.info("Resultados enviados a la interfaz de usuario correctamente.")
        else:
            logger.error(f"Error al enviar los resultados a la interfaz de usuario: {response.status_code}")
    except Exception as e:
        logger.error(f"Error al enviar los resultados a la interfaz de usuario: {e}")

@app.route('/upload', methods=['POST'])
def handle_upload():
    try:
        logger.debug("=== Iniciando nueva solicitud de upload ===")
        logger.debug(f"Headers recibidos: {dict(request.headers)}")
        logger.debug(f"Form data: {dict(request.form)}")
        logger.debug(f"Files: {request.files}")

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        model = request.form.get('model', 'amazon')

        logger.debug(f"Archivo recibido: {file.filename}")
        logger.debug(f"Modelo seleccionado: {model}")

        df = pd.read_csv(file)
        logger.debug(f"DataFrame cargado con las siguientes columnas: {df.columns}")

        model_url = f'http://localhost:5001/{model}/predict'
        file_content_transformed = df.to_csv(index=False)

        response = requests.post(
            model_url,
            files={'file': (file.filename, file_content_transformed, 'text/csv')}
        )

        if response.status_code == 200:
            logger.debug(f"Archivo enviado exitosamente al modelo: {model_url}")
            predictions = response.json()['prediction']
            #send_results_to_ui(predictions)
            return jsonify({'message': 'Archivo enviado exitosamente al modelo', 'predictions': predictions}), 200
        else:
            logger.error(f"Error al enviar el archivo al modelo: {response.text}")
            return jsonify({'error': f"Error del modelo: {response.text}"}), response.status_code

    except Exception as e:
        logger.error("Error no manejado en handle_upload")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)
