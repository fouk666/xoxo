var myUser = {}; // игрок
var socket = io.connect('http://' + document.domain + ':' + location.port);

do {
    var nickname = prompt('Введите свой ник: ', makeid());
    console.log('nick: '+nickname);
    if (nickname == null)
        nickname = makeid();
    myUser.nickname = nickname;
    console.log('userNick: '+myUser.nickname.toString());
} while (nickname == '');
alert('Ваш ник: ' + nickname);

// присваивание пользователю id сокета
// добавляем пользователя на сервер
$(document).ready(function () {
    // если не будет сокета, добавить генерацию ID
    myUser.id = socket.id;
    console.log('myUser.id: ', myUser.id);
    socket.emit('addUser', myUser);
});

// убираем пользователя при закрытии им вкладки
window.onbeforeunload = function warn(){
    socket.send('|~  '+myUser.nickname.toString() + ' has disconnected!  ~|');
    socket.emit('removeUser', myUser.id);
};

function makeid() {
    var text = '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

// ход игрока
function move(id) {
    socket.emit('move',myUser.id,id);
}

// ход компьютера
//function ai() {
//    var id = Math.floor(Math.random() * 100);
//    t[id] ? ai() : move(id, 'ai');
//}

// окончание игры
function reset(winner) {
    socket.send(myUser.nickname.toString()+' has disconnected!');
    alert(('*** ' + winner + ' ***'));
    socket.emit('removeUser', myUser.id);
    location.reload();
}

//---------------------------ЧАТ-----------------------------
var checkMe = false;

socket.on('connect', function() {
    socket.send('|~  ' + '<span class="nickname-bold">' +  myUser.nickname + '</span>' + ' has connected  ~|');
});

function disconnect() {
    socket.send('|~  ' + '<span class="nickname-bold">' + myUser.nickname + '</span>' + ' has disconnected!  ~|');
    socket.disconnect();
    console.log('3 disc');
}
socket.on('message', function(msg) {
    console.log('input move msg: ', msg);
    console.log('parseINT: ', parseInt(msg['cellID'],10) >= 0);
    if (msg !== myUser.id) {
        if ((msg == myUser.id + ' player1')||(msg == myUser.id + ' player2')) {
            var arr = msg.split(' ');
            myUser.role = arr[1];
            console.log('role: ', myUser.role);
        } else
            if (parseInt(msg['setNicknameEnemy'],10) == 1) {
                if (msg['player1'] != myUser.nickname)
                    myUser.enemy = msg['player1'];
            } else
                if (parseInt(msg['setNicknameEnemy'],10) == 2) {
                    if (msg['player2'] != myUser.nickname)
                        myUser.enemy = msg['player2'];
                } else
                    if (msg['winner'] != null) {
                        var winner = msg['winner'];
                        if (winner == myUser.nickname)
                            reset('Ты победил!');
                        else
                            reset('Ты проиграл :\'(');
                    } else
                        if (parseInt(msg['draw'],10) == 1) {
                            reset('Ничья...');
                        } else
                            if (parseInt(msg['cellID'],10) >= 0) {
                                var localRole = myUser.role;
                                if (msg['role'] != myUser.role)
                                    localRole = msg['role'];
                                console.log('LOCAL ROLE: ', localRole);
                                var id = msg['cellID'];
                                document.getElementById(id).className = localRole;
                            } else {
                                console.log('msgID', msg)
                                if ((checkMe)&&(myUser.enemy != undefined)) {
                                    $("#messages").append('<li>' + '<span class="nickname-bold">' + myUser.nickname + '</span>' + ': ' + msg + '</li>');
                                    checkMe = false;
                                }
                                else
                                    if ((!checkMe)&&(myUser.enemy != undefined))
                                        $("#messages").append('<li>' + '<span class="nickname-bold">' + myUser.enemy + '</span>' + ': ' + msg + '</li>');
                                    else
                                        $("#messages").append('<li>' + msg + '</li>');
                                console.log('Received message');
                            }
    } else disconnect();
});

$('#sendbutton').on('click', function sendButton() {
    var msg = $('#myMessage').val().trim();
    console.log('msg = ' + msg);
    if (msg !== '')
        socket.send($('#myMessage').val());
    $('#myMessage').val('');
    checkMe = true;
});
