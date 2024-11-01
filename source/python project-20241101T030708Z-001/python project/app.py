from flask import Flask
from mongoengine import connect
from flask_socketio import SocketIO
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp

app = Flask(__name__)
app.secret_key = 'clave secreta'

# Conexión a MongoDB
connect(db='proycd-oto2024', host='localhost', port=27017)

# Inicializa SocketIO
socketio = SocketIO(app)

# Registrar los Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

# Evento de conexión para pruebas
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

# Simulación de ganancias/pérdidas para la gráfica
@socketio.on('request_update')
def handle_request_update():
    import random
    # Simulación de datos de ganancias/pérdidas
    profit_loss = random.uniform(-100, 100)  # Reemplaza con los cálculos reales
    socketio.emit('update_chart', {'profit_loss': profit_loss})

# Ejecutar la aplicación
if __name__ == '__main__':
    socketio.run(app, debug=True)
