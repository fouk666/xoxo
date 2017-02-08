from app import app, socketio
from flask import render_template
from flask_socketio import emit, send

# ��������� �������� � �����
@app.route('/')
def game():
    return render_template('game.html')

users = [] # ������ ���� �������
state_game = [] # ��������� �������� ���� � ��������� ������� (0 - ����� �� �����, 1 - ����� ������ �����, 2 - ����� ������ �����)
player1 = '' # ID ������ 1
player2 = '' # ID ������ 2
current_userID = '' # �� ��� ������� ���
role = '' # player1 ��� player2

# ������� ��� ����������
def set_current_userID(newID):
    global current_userID
    current_userID = newID

def set_player1(newPl1):
    global player1
    player1 = newPl1

def set_player2(newPl2):
    global player2
    player2 = newPl2

# ������������� ������� � ���������� �������� ����
state_game = [[0] * 10 for i in range(10)]

# ��������� ��������� �������� ����
def set_state_game():
    global state_game
    state_game = [[0] * 10 for i in range(10)]

# �������, ����������� ������ �� ������������ �������-������
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

# �������� ����� ���� � �������� ������ ������ �� ������� - 5 ������� � ���
# 1. �������� �� �����������
# 2. �������� �� ���������
# 3. �������� �� ����������
def check_end(player):

    for i in range(10):
        count = 0
        for j in range(10):
            if state_game[i][j] == player:
                count+=1
            else:
                count=0
            if count == 5:
                print('horiz: ', count)
                return True

    trasp_state_game = list(zip(*state_game))
    for i in range(10):
        count = 0
        for j in range(10):
            if trasp_state_game[i][j] == player:
                count+=1
            else:
                count=0
            if count == 5:
                print('vert: ', count)
                return True

    for row in diags(state_game):
        for i in range(len(row)):
            if row[i] == player:
                count+=1
            else:
                count=0
            if count == 5:
                print('diag: ', count)
                return True

    return False

# �������� �� �����
def check_draw():
    return any(0 in row for row in state_game)


# ���������� ������� ����������� ������������
@socketio.on('connect')
def connect():
    print('User Connected')
    if len(users) >= 2:
        #�������� ��������� �������� ������� ����
        print('So many users!')

# ���������� ������� ���������� ������������
@socketio.on('removeUser')
def remove_user(userID):
    print('User Disconnected: ', userID)
    users.remove(userID)
    print('count users: ', len(users))

# ���������� ������� ���������� ������������ � ������ �� �������
@socketio.on('addUser')
def add_user(user):
    print('new user: ', user)
	# ���� ������� ��� ���, ��������� ������������, ������ ��� player1
    if len(users) == 0:
        users.append(user)
        player1 = user['id']
        set_player1(player1)
        set_current_userID(player1)
        print('!!!curID', current_userID)
        send(user['id']+' player1', json=True, broadcast=False)
        print('added user: ', user)
        print('count users: ', len(users))
	# ����� ���� ����� ���� ����, ��������� ������������, ������ ��� player2
    else:
        if len(users) == 1:
            users.append(user)
            player2 = user['id']
            set_player2(player2)
            send({'setNicknameEnemy': 1, 'player1': users[0]['nickname']}, json=True, broadcast=True)
            send({'setNicknameEnemy': 2, 'player2': users[1]['nickname']}, json=True, broadcast=True)
            print('added user: ', user)
            print('count users: ', len(users))
        # ����� ������������ ����� ������
        else:
            if len(users) >= 2:
                print(user['id'])
                send(user['id'], json=True, broadcast=False)

#���������� ������� ���� ������
#���� �����, ��������� ���, �������� ���, ��� ������ ������ ������,
#���������� ��������� ������� � ID ����, ��� �����
#�������� �������� ������, �� ��� ������� ���
#��������� ���������� ����
@socketio.on('move')
def move(userID,cellID):
    if len(users) < 2:
        return
    cellX = cellID // 10
    cellY = cellID % 10
    if userID == current_userID and state_game[cellX][cellY] == 0:
        print('move: ', userID)
        print('sending after move: ', str(userID)+' move '+str(cellID)+'player1: ', player1)
        print('userID == player1 -> ', str(userID) == str(player1))
        if str(userID) == str(player1):
            state_game[cellX][cellY] = 1
            print('state_game[',cellX,'][',cellY,'] = 1')
            send({'role': 'player1', 'cellID': cellID}, json=True, broadcast=True)
            if check_end(1):
                send({'winner': users[0]['nickname']}, json=True, broadcast=True)
                print('check_end 1')
                users.clear()
                set_state_game()
                return
        else:
            if str(userID) == str(player2):
                state_game[cellX][cellY] = 2
                print('state_game[',cellX,'][',cellY,'] = 2')
                send({'role': 'player2', 'cellID': cellID}, json=True, broadcast=True)
                if check_end(2):
                    send({'winner': users[1]['nickname']}, json=True, broadcast=True)
                    print('check_end 2')
                    users.clear()
                    set_state_game()
                    return

        if not check_draw():
            send({'draw': 1}, json=True, broadcast=True)
            users.clear()
            set_state_game()
            return

        if current_userID == player1:
            set_current_userID(player2)
            print('pl2 ', current_userID)
        else:
            set_current_userID(player1)
            print('pl1', current_userID)

#���������� ������� "���������" �������� ����
@socketio.on('message')
def handle_message(msg):
	print('Message: ' + msg)
	send(msg, broadcast=True)
