from app import app, socketio
from flask import render_template
from flask_socketio import emit, send

# загружаем страницу с игрой
@app.route('/')
def game():
    return render_template('game.html')

users = [] # список всех игроков
stateGame = [] # состояние игрового поля в двумерном массиве (0 - никто не ходил, 1 - ходил первый игрок, 2 - ходил второй игрок)
player1 = '' # ID игрока 1
player2 = '' # ID игрока 2
currentUserID = '' # за кем текущий ход
role = '' # player1 или player2

# сеттеры для переменных
def setCurrentUserID(newID):
    global currentUserID
    currentUserID = newID

def setPlayer1(newPl1):
    global player1
    player1 = newPl1

def setPlayer2(newPl2):
    global player2
    player2 = newPl2

# инициализация массива с состоянием игрового поля
stateGame = [[0] * 10 for i in range(10)]

# обнуление состояния игрового поля
def setStateGame():
    global stateGame
    stateGame = [[0] * 10 for i in range(10)]

# функция, разбивающая список на диагональные объекты-строки
def diags(matrix):
    x = len(matrix[0])

    yield [matrix[i][i] for i in range(x)]
    yield [matrix[i][x - 1 - i] for i in range(x)]
    for i in range(1, x):
        row1 = []
        row2 = []
        row3 = []
        row4 = []
        for j in range(i):
            row1.append(matrix[x - i + j][j])
            row2.append(matrix[j][x - i + j])

            row3.append(matrix[j][i-1 - j])
            row4.append(matrix[x - 1 - j][x - i + j])
        yield row1
        yield row2
        yield row3
        yield row4

# проверка конца игры с условием победы одного из игроков - 5 значков в ряд
# 1. проверка по горизонтали
# 2. проверка по вертикали
# 3. проверка по диагоналям
def checkEnd(player):

    for i in range(10):
        count = 0
        for j in range(10):
            if (stateGame[i][j] == player):
                count+=1
            else:
                count=0
            if (count == 5):
                print('horiz: ', count)
                return True

    traspStateGame = list(zip(*stateGame))
    for i in range(10):
        count = 0
        for j in range(10):
            if (traspStateGame[i][j] == player):
                count+=1
            else:
                count=0
            if (count == 5):
                print('vert: ', count)
                return True

    for row in diags(stateGame):
        for i in range(len(row)):
            if (row[i] == player):
                count+=1
            else:
                count=0
            if (count == 5):
                print('diag: ', count)
                return True

    return False

# проверка на ничью
def checkDraw():
    return any(0 in row for row in stateGame)


# обработчик события подключения пользователя
@socketio.on('connect')
def connect():
    print('User Connected')
    # if (player1!=0)and((player2!=0)):
    if (len(users) >= 2):
        #добавить обработку ожидания игроком игры
        print('So many users!')

# обработчик события отключения пользователя
@socketio.on('removeUser')
def removeUser(userID):
    print('User Disconnected: ', userID)
    users.remove(userID)
    print('count users: ', len(users))

# обработчик события добавления пользователя в список на сервере
@socketio.on('addUser')
def addUser(user):
	# если игроков еще нет, добавляем пользователя, делаем его player1
    if(len(users) == 0):
        users.append(user)
        player1 = user['id']
        setPlayer1(player1)
        setCurrentUserID(player1)
        print('!!!curID', currentUserID)
        send(user['id']+' player1', json=True, broadcast=False)
        print('added user: ', user)
        print('count users: ', len(users))
	# иначе если игрок один есть, добавляем пользователя, делаем его player2
    else:
        if(len(users) == 1):
            users.append(user)
            player2 = user['id']
            setPlayer2(player2)
            send({'setNicknameEnemy': 1, 'player1': users[0]['nickname']}, json=True, broadcast=True)
            send({'setNicknameEnemy': 2, 'player2': users[1]['nickname']}, json=True, broadcast=True)
            print('added user: ', user)
            print('count users: ', len(users))
        # иначе дисконнектим этого игрока
        else:
            if (len(users) >= 2):
                print(user['id'])
                send(user['id'], json=True, broadcast=False)

#обработчик события хода игрока
#если игрок, делающего ход, является тем, кто сейчас должен ходить,
#отправляем сообщение игрокам с ID того, кто ходит
#изменяем текущего игрока, за кем текущий ход
#проверяем завершения игры
@socketio.on('move')
def move(userID,cellID):
    if (len(users) < 2):
        return
    cellX = cellID//10
    cellY = cellID%10
    if ((userID == currentUserID)and(stateGame[cellX][cellY] == 0)):
        print('move: ', userID)
        print('sending after move: ', str(userID)+' move '+str(cellID)+'player1: ', player1)
        print('userID == player1 -> ', str(userID) == str(player1))
        if (str(userID) == str(player1)):
            stateGame[cellX][cellY] = 1
            print('stateGame[',cellX,'][',cellY,'] = 1')
            send({'role': 'player1', 'cellID': cellID}, json=True, broadcast=True)
            if (checkEnd(1)):
                send({'winner': users[0]['nickname']}, json=True, broadcast=True)
                print('checkEnd 1')
                users.clear()
                setStateGame()
                return
        else:
            if (str(userID) == str(player2)):
                stateGame[cellX][cellY] = 2
                print('stateGame[',cellX,'][',cellY,'] = 2')
                send({'role': 'player2', 'cellID': cellID}, json=True, broadcast=True)
                if (checkEnd(2)):
                    send({'winner': users[1]['nickname']}, json=True, broadcast=True)
                    print('checkEnd 2')
                    users.clear()
                    setStateGame()
                    return

        if (not checkDraw()):
            send({'draw': 1}, json=True, broadcast=True)
            users.clear()
            setStateGame()
            return

        if (currentUserID == player1):
            setCurrentUserID(player2)
            print('pl2 ', currentUserID)
        else:
            setCurrentUserID(player1)
            print('pl1', currentUserID)





#обработчик события "отправить" игрового чата
@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg, broadcast=True)
