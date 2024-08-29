from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
# 给flask绑定socket实例
socketio = SocketIO(app, engineio_logger=True)
# 定义路由
@app.route('/')
def index():
    return render_template('index.html')
# 拿到用户指令，发送给小车
@socketio.on('move')
def handle_move(json):
    print('received json: ' + str(json))
    emit('move', json, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host = '0.0.0.0', port = 5000, debug = True)