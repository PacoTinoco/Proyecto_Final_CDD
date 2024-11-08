from flask import Flask, request, jsonify
import pandas as pd
import ml_model_api_amazon, ml_model_api_google
import logging
import requests
import tempfile
import os

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ML Models API is running'})

#Operacion Interna
def send_results_to_orchestrator(predictions):
    try:
        url = "http://localhost:5002/results"  # URL de tu orquestador (puerto 5002)
        data = {"predictions": predictions}   # Enviar las predicciones como JSON

        response = requests.post(url, json=data)

        if response.status_code == 200:
            print("Resultados enviados al orquestador correctamente.")
        else:
            print(f"Error al enviar los resultados: {response.status_code}")

    except Exception as e:
        print(f"Error al enviar los resultados al orquestador: {e}")

@app.route('/<model_type>/predict', methods=['POST'])
def predict(model_type):
    try:
        # Verificar si se ha recibido un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No file found'}), 400

        file = request.files['file']

        # Verificar si el archivo tiene un nombre
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Leer el archivo CSV en un DataFrame
        df = pd.read_csv(file)

        # Verificar las columnas necesarias
        required_columns = ['Close']  # Asegúrate de que las columnas necesarias estén presentes
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': f'Missing required columns: {required_columns}'}), 400

        # Crear un archivo temporal y escribir el DataFrame
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            df.to_csv(temp_file.name, index=False)

            # Dependiendo del modelo, realizar las predicciones
            if model_type == 'amazon':
                predictions = ml_model_api_amazon.predict_future(temp_file.name)
            elif model_type == 'google':
                predictions = ml_model_api_google.predict_future(temp_file.name)
            else:
                return jsonify({'error': 'Invalid model type'}), 400

        # Eliminar el archivo temporal
        os.remove(temp_file.name)

        # Enviar los resultados al orquestador o realizar otras acciones
        send_results_to_orchestrator(predictions)

        # Devolver las predicciones
        return jsonify({'prediction': predictions})

    except Exception as e:
        # Manejo de excepciones para capturar errores no controlados
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5001)