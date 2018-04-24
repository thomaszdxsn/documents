import socket
import sys


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# 监听一个连接
# 调用`listen()`可以让socket进入"server模式"
sock.listen(1)

while True:
    # 等待连接
    print('waiting for a connection')
    # connection其实是操作系统维持的另一个socket
    connection, client_address = sock.accept()  # 堵塞...
    try:
        print('connection from', client_address)

        # 将数据分段接收
        while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
            if data:
                print('seding data back to the client')
                connection.sendall(data)
            else:
                print('no data from', client_address)
                break
    finally:
        # 清理连接
        connection.close()
