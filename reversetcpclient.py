import os
import socket
import struct
import random
import sys
import time

# 检查命令行参数
if len(sys.argv) != 6:  # 如果命令行参数数量不等于6，打印用法并退出
    print(f"用法: {sys.argv[0]} <server_ip> <server_port> <Lmin> <Lmax> <file_path>")
    sys.exit(1)  # 退出程序

try:
    # 从命令行参数获取服务器IP、端口、最小和最大块长度以及文件路径
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    Lmin = int(sys.argv[3])
    Lmax = int(sys.argv[4])
    file_path = sys.argv[5]
except ValueError as e:
    print(f"参数错误: {e}")
    print(f"用法: {sys.argv[0]} <server_ip> <server_port> <Lmin> <Lmax> <file_path>")
    sys.exit(1)

# 检查服务器IP是否有效
try:
    socket.inet_aton(server_ip)
except socket.error:
    print(f"无效的服务器IP地址: {server_ip}")
    sys.exit(1)

# 检查端口号是否在有效范围内
if not (0 <= server_port <= 65535):
    print(f"无效的端口号: {server_port}. 端口号应在0到65535之间。")
    sys.exit(1)

# 检查Lmin和Lmax是否为正整数且Lmin小于等于Lmax
if Lmin <= 0 or Lmax <= 0 or Lmin > Lmax:
    print(f"无效的块长度: Lmin={Lmin}, Lmax={Lmax}. 块长度应为正整数且Lmin应小于等于Lmax。")
    sys.exit(1)

# 检查文件路径是否存在且可读
if not os.path.isfile(file_path):
    print(f"文件不存在或不可读: {file_path}")
    sys.exit(1)

# 检查文件是否为空
if os.path.getsize(file_path) == 0:
    print(f"文件为空: {file_path}")
    sys.exit(1)

# 参数验证通过，继续执行程序
print(f"服务器IP: {server_ip}")
print(f"端口号: {server_port}")
print(f"块长度范围: {Lmin}-{Lmax}")
print(f"文件路径: {file_path}")

# 读取文件并分块
try:
    with open(file_path, 'r') as file:
        data = file.read()
except IOError as e:
    print(f"读取文件时出错: {e}")
    sys.exit(1)


chunks = []  # 用于存储数据块的列表
i = 0
while i < len(data):  # 循环将数据分块
    length = random.randint(Lmin, Lmax)  # 随机生成块的长度
    chunk = data[i:i + length]  # 获取数据块
    chunks.append(chunk)  # 将数据块添加到列表中
    i += length  # 更新索引

# 初始化客户端socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建一个TCP socket
client_socket.connect((server_ip, server_port))  # 连接到服务器


# 创建报文的辅助函数
def create_packet(packet_type, *args):
    if packet_type == 1:  # 创建类型为1的报文（初始化报文）
        return struct.pack('!H I', packet_type, args[0])  # 打包报文类型和块数量
    elif packet_type == 3:  # 创建类型为3的报文（请求反转报文）
        length = len(args[0])  # 获取数据长度
        return struct.pack('!H I', packet_type, length) + args[0].encode('utf-8')  # 打包报文类型和长度，并附加数据
    return b''  # 返回空字节串


# 发送Initialization报文
init_packet = create_packet(1, len(chunks))  # 创建初始化报文，包含块数量
client_socket.sendall(init_packet)  # 发送初始化报文

# 等待Agree报文
response = client_socket.recv(2)  # 接收服务器的响应
packet_type = struct.unpack('!H', response)[0]  # 解包响应，获取报文类型
if packet_type != 2:  # 如果报文类型不是2（同意报文），打印错误信息并退出
    print("Unexpected packet type")
    sys.exit(1)  # 退出程序

# 发送Reverse Request报文并接收响应
reversed_data = []  # 用于存储反转后的数据块
for i, chunk in enumerate(chunks):  # 遍历所有数据块
    request_packet = create_packet(3, chunk)  # 创建请求反转报文
    client_socket.sendall(request_packet)  # 发送请求反转报文
    time.sleep(3)  # 等待3秒，方便观察多个client连接的情况
    response = client_socket.recv(6 + len(chunk))  # 接收服务器的响应
    response_type, response_length = struct.unpack('!H I', response[:6])  # 解包响应类型和长度
    reversed_chunk = response[6:].decode('utf-8')  # 获取反转后的数据块并解码
    reversed_data.append(reversed_chunk)  # 将反转后的数据块添加到列表
    print(f"第{i + 1}块: {reversed_chunk}")  # 打印反转后的数据块

# 保存反转后的内容到文件
with open('reversed_output.txt', 'w') as file:  # 打开文件以写入模式
    file.write(''.join(reversed_data))  # 将反转后的数据写入文件

client_socket.close()  # 关闭客户端socket
