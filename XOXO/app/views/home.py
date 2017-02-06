from app import app, socketio
from flask import render_template
from flask_socketio import emit, send

@app.route('/')
def game():
    return render_template('game.html')

users = []
player1 = 0
player2 = 0
currentUserID = 0

@socketio.on('connect')
def connect():
    print('User Connected')
    # print('count users: ', len(users))

@socketio.on('removeUser')
def removeUser(userID):
    print('User Disconnected: ', userID)
    users.remove(userID)
    print('count users: ', len(users))

@socketio.on('addUser')
def addUser(userID):
    if(len(users) == 0):
        users.append(userID)
        player1 = userID
        curentUserID = player1
        print('added user: ', userID)
        print('count users: ', len(users))
    else:
        if(len(users) == 1):
            users.append(userID)
            player2 = userID
            print('added user: ', userID)
            print('count users: ', len(users))


@socketio.on('move')
def move(userID):
    if (checkMove(userID)):
        print('move: ', userID)
        send(userID, broadcast=True)
        if (currentUserID == player1):
            currentUserID == player2
        else:
            currentUserID == player1

def checkMove(userID):
    if(userID == currentUserID):
        return True
    else:
        return False