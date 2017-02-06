from flask import Flask
from flask_socketio import SocketIO

# создаем экземпляр класса Flask
app = Flask(__name__)
# создаем экземпляр класса SocketIO
socketio = SocketIO(app)

from app.views import home
