import socket
import struct  # 导入用于打包和解包二进制数据的struct库
import select  # 导入用于多路复用I/O操作的select库

# 服务器配置
server_ip = '0.0.0.0'  # 监听所有接口
server_port = 12323  # 服务器端口号

# 初始化服务器socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建一个TCP socket
server_socket.bind((server_ip, server_port))  # 将socket绑定到指定的IP地址和端口
server_socket.listen(5)  # 开始监听传入连接，最多允许5个连接排队

inputs = [server_socket]  # 初始化输入列表，包括服务器socket
clients = {}  # 存储客户端信息的字典


# 创建报文的辅助函数
def create_packet(packet_type, *args):
    if packet_type == 2:  # 创建类型为2的报文
        return struct.pack('!H', packet_type)  # 打包报文类型
    elif packet_type == 4:  # 创建类型为4的报文
        length = len(args[0])  # 获取数据长度
        return struct.pack('!H I', packet_type, length) + args[0].encode('utf-8')  # 打包报文类型和长度，并附加数据
    return b''  # 返回空字节串

print(f"服务器在 {server_ip}:{server_port} 上监听")  # 打印服务器启动信息

while True:  # 无限循环，持续监听和处理客户端请求
    readable, _, _ = select.select(inputs, [], [])  # 使用select监控输入列表中的socket，等待可读的socket
    for s in readable:  # 遍历所有可读的socket
        if s is server_socket:  # 如果是服务器socket，表示有新的客户端连接
            client_socket, addr = server_socket.accept()  # 接受客户端连接
            print(f"Connection from {addr}")  # 打印客户端地址
            inputs.append(client_socket)  # 将新连接的客户端socket添加到输入列表
            clients[client_socket] = {'state': 'init', 'chunks': 0}  # 初始化客户端信息
        else:  # 如果是客户端socket，表示有数据可读
            data = s.recv(2048)  # 接收数据，最多2048字节
            if not data:  # 如果没有数据，表示客户端已关闭连接
                print(f"Closing connection {s.getpeername()}")  # 打印关闭连接的客户端地址
                inputs.remove(s)  # 从输入列表中移除客户端socket
                del clients[s]  # 从客户端字典中删除该客户端
                s.close()  # 关闭客户端socket
            else:  # 如果有数据可读
                client = clients[s]  # 获取该客户端的信息
                if client['state'] == 'init':  # 如果客户端处于初始化状态
                    packet_type, num_chunks = struct.unpack('!H I', data)  # 解包报文，获取报文类型和块数
                    if packet_type == 1:  # 如果报文类型为1（初始化报文）
                        client['chunks'] = num_chunks  # 存储块数
                        response_packet = create_packet(2)  # 创建类型为2的响应报文
                        s.sendall(response_packet)  # 发送响应报文
                        client['state'] = 'processing'  # 更新客户端状态为处理中
                elif client['state'] == 'processing':  # 如果客户端处于处理中状态
                    packet_type, length = struct.unpack('!H I', data[:6])  # 解包报文类型和数据长度
                    chunk = data[6:].decode('utf-8')  # 解包数据并解码为字符串
                    reversed_chunk = chunk[::-1]  # 将数据块反转
                    response_packet = create_packet(4, reversed_chunk)  # 创建类型为4的响应报文，包含反转后的数据
                    s.sendall(response_packet)  # 发送响应报文

server_socket.close()  # 关闭服务器socket
