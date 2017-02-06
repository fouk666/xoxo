from app import app, socketio
from flask import render_template
from flask_socketio import emit, send

# загружаем страницу с игрой
@app.route('/')
def game():
    return render_template('game.html')

users = [] # список всех игроков
player1 = 0 # ID игрока 1
player2 = 0 # ID игрока 2
currentUserID = 0 # за кем текущий ход 

# обработчик события подключения пользователя
@socketio.on('connect')
def connect():
    print('User Connected')
    # print('count users: ', len(users))

# обработчик события отключения пользователя
@socketio.on('removeUser')
def removeUser(userID):
    print('User Disconnected: ', userID)
    users.remove(userID)
    print('count users: ', len(users))
	
# обработчик события добавления пользователя в список на сервере
@socketio.on('addUser')
def addUser(userID):
	# если игроков еще нет, добавляем пользователя, делаем его player1
    if(len(users) == 0):
        users.append(userID)
        player1 = userID
        curentUserID = player1
        print('added user: ', userID)
        print('count users: ', len(users))
	# иначе если игрок один есть, добавляем пользователя, делаем его player2
    else:
        if(len(users) == 1):
            users.append(userID)
            player2 = userID
            print('added user: ', userID)
            print('count users: ', len(users))

'''
обработчик события хода игрока
если игрок, делающего ход, является тем, кто сейчас должен ходить,
отправляем сообщение игрокам с ID того, кто ходит
изменяем текущего игрока, за кем текущий ход
'''
@socketio.on('move')
def move(userID):
    if (userID == currentUserID):
        print('move: ', userID)
		#TODO
        send(userID, broadcast=True)
        if (currentUserID == player1):
            currentUserID == player2
        else:
            currentUserID == player1
