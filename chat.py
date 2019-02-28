from sanic import Sanic
from sanic.response import html
import socketio
import re


sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)


@app.route('/')
async def index(request):
    with open('chat.html') as f:
        return html(f.read())


@sio.on('show username', namespace='/test')
async def test_message(sid, message):
    await sio.emit('my response', {'data': 'user ' + message['data'] + ' has connected.'}, room=sid, namespace='/test')


@sio.on('join room', namespace='/test')
async def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': message['username'] + ' entered room: ' + message['room']},
                   room=message['room'], namespace='/test')


@sio.on('leave room', namespace='/test')
async def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Left room: ' + message['room']},
                   room=sid, namespace='/test')


@sio.on('list rooms', namespace='/test')
async def roomlist(sid):
    rooms = sio.manager.rooms['/test']
    room_str = ''
    for r in rooms:
        # exclude personal rooms
        if r is not None and not re.findall('[a-z0-9]{32}', r):
            room_str += r + ","
    await sio.emit('my response', {'data': 'Rooms list: ' + room_str[0:len(room_str)-1]},
                   room=sid, namespace='/test')


@sio.on('close room', namespace='/test')
async def close(sid, message):
    await sio.emit('my response',
                   {'data': 'Room ' + message['room'] + ' is closing.'},
                   room=message['room'], namespace='/test')
    await sio.close_room(message['room'], namespace='/test')


@sio.on('my room event', namespace='/test')
async def send_room_message(sid, message):
    await sio.emit('my response', {'data': message['data']},
                   room=message['room'], namespace='/test')


@sio.on('disconnect request', namespace='/test')
async def disconnect_request(sid):
    await sio.disconnect(sid, namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')


app.static('/static', './static')


if __name__ == '__main__':
    app.run()
