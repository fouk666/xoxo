var t = new Array(9);
var myUser = {};
var socket = io.connect('http://' + document.domain + ':' + location.port);

$(document).ready(function () {
    myUser.id = socket.id;
    console.log(myUser.id,': ID');
    socket.emit('addUser', myUser.id);
});

// убираем пользователя при закрытии им вкладки
window.onbeforeunload = function warn(){
    socket.emit('removeUser', myUser.id);
};

function ai() {
  var id = Math.floor(Math.random() * 9);
  t[id] ? ai() : move(id, 'ai');
}

function checkEnd() {
  if (t[0] == 'ai' && t[1] == 'ai' && t[2] == 'ai' || t[0] == 'player' && t[1] == 'player' && t[2] == 'player')  return true;
  if (t[3] == 'ai' && t[4] == 'ai' && t[5] == 'ai' || t[3] == 'player' && t[4] == 'player' && t[5] == 'player')  return true;
  if (t[6] == 'ai' && t[7] == 'ai' && t[8] == 'ai' || t[6] == 'player' && t[7] == 'player' && t[8] == 'player')  return true;
  if (t[0] == 'ai' && t[3] == 'ai' && t[6] == 'ai' || t[0] == 'player' && t[3] == 'player' && t[6] == 'player')  return true;
  if (t[1] == 'ai' && t[4] == 'ai' && t[7] == 'ai' || t[1] == 'player' && t[4] == 'player' && t[7] == 'player')  return true;
  if (t[2] == 'ai' && t[5] == 'ai' && t[8] == 'ai' || t[2] == 'player' && t[5] == 'player' && t[8] == 'player')  return true;
  if (t[0] == 'ai' && t[4] == 'ai' && t[8] == 'ai' || t[0] == 'player' && t[4] == 'player' && t[8] == 'player')  return true;
  if (t[2] == 'ai' && t[4] == 'ai' && t[6] == 'ai' || t[2] == 'player' && t[4] == 'player' && t[6] == 'player')  return true;
  if (t[0] && t[1] && t[2] && t[3] && t[4] && t[5] && t[6] && t[7] && t[8]) return true;
}

function move(id, role) {
    if (t[id]) return false;
    t[id] = role;
    //socket.emit('move',myUser.id);
    socket.on('move', function(myUserID) {
		$("#messages").append('<li>'+msg+'</li>');
		console.log('Received message');
	});
    document.getElementById(id).className = 'cell' + role;
    !checkEnd() ? (role == 'player') ? ai() : null : reset();
}

function reset() {
  alert("Игра окончена!");
  socket.emit('removeUser', myUser.id);
  location.reload();
}
