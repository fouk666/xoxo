var myUser = {}; // игрок
var checkMe = false;
var checkLog = false; // для отсеивания системных сообщений в чат
var socket = io.connect('http://' + document.domain + ':' + location.port);

var n = 99;
var middle = 59;
var s = 0;

addCells(n,s);

function addCells(n,s) {
    for (var i = s; i <= n; i++) {
        var div = document.createElement('div');
        div.className = 'cell';
        div.id = i;
        div.onclick = function(i) {
            return function() {move(i);}
        }(i);
        table.appendChild(div);
    }
}

// ход игрока
function move(id) {
    if (id > middle) {
        var strings = div((id-middle),10)+1;
        middle += strings * 10;
        s = n; s++;
        n += strings * 10;
        //addCells(n,s);
        socket.emit('move',myUser.id,id,n,s,middle, strings);
    } else
        if (id <= middle)
            socket.emit('move',myUser.id,id,-1,-1,-1,-1);
}

function div(val, by){
    return (val - val % by) / by;
}

var nickname = prompt('Введите свой ник: ', makeid());
console.log('nick: '+nickname);
if (nickname == null)
    nickname = makeid();
myUser.nickname = nickname;
console.log('userNick: '+myUser.nickname);
alert('Ваш ник: ' + nickname);

// присваивание пользователю id сокета
// добавляем пользователя на сервер
$(document).ready(function () {
    myUser.id = socket.id;
    console.log('myUser.id: ', myUser.id);
    socket.emit('addUser', myUser);
});

// убираем пользователя при закрытии им вкладки
window.onbeforeunload = function warn(){
    socket.emit('removeUser', myUser.id);
    socket.disconnect();
};

function makeid() {
    var text = '';
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

// ход компьютера
//function ai() {
//    var id = Math.floor(Math.random() * 100);
//    t[id] ? ai() : move(id, 'ai');
//}

// окончание игры
function reset(winner) {
    socket.emit('removeUser', myUser.id);
    disconnect();
    alert(('*** ' + winner + ' ***'));
}

//---------------------------ЧАТ-----------------------------


socket.on('connect', function() {
    checkLog = true;
    socket.send('|~  ' + '<span class="nickname-bold">' +  myUser.nickname + '</span>' + ' has connected  ~|');
});

function disconnect() {
    checkLog = true;
    socket.send('|~  ' + '<span class="nickname-bold">' + myUser.nickname + '</span>' + ' has disconnected!  ~|');
    socket.disconnect();
    console.log('3 disc');
    location.reload();
}
socket.on('message', function(msg) {
    console.log('input move msg: ', msg);
    if (msg !== myUser.id) {
        if (checkLog){
            $("#messages").append('<li>' + msg + '</li>');
            checkLog = false;
            console.log('-------------------LOG MESSAGE------------------------');
            return;
        } else
            if (parseInt(msg['n'],10) > 0) {
                console.log('n = ',parseInt(msg['n'],10),'. s = ',parseInt(msg['s'],10), '. m = ',parseInt(msg['middle'],10));
                if (n != parseInt(msg['n'],10)) {
                    n = parseInt(msg['n'],10);
                    s = parseInt(msg['s'],10);
                    middle = parseInt(msg['middle'],10);
                }
                addCells(n,s);
            } else
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
                                        console.log('msgID', msg);
                                        if ((checkMe)&&(!checkLog)&&(myUser.enemy != undefined)) {
                                            $("#messages").append('<li>' + '<span class="nickname-bold">' + myUser.nickname + '</span>' + ': ' + msg + '</li>');
                                            checkMe = false;
                                        } else
                                            if (parseInt(msg['reset'],10) == 1)
                                                reset('Противник сдался!');
                                            else
                                                if ((!checkMe)&&(!checkLog)&&(myUser.enemy != undefined))
                                                    $("#messages").append('<li>' + '<span class="nickname-bold">' + myUser.enemy + '</span>' + ': ' + msg + '</li>');
                                                else
                                                    $("#messages").append('<li>' + msg + '</li>');
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
