from app import app, socketio

# запускаем сервер
if __name__ == '__main__':
    socketio.run(app)
