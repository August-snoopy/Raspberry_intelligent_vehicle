from socketio import sio

@sio.on('move')
def racv_move(data):
    print('move', data)
    # sio.emit('move', data)

if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    sio.wait()