import socket
import random
import time
from datetime import datetime
import struct  # 导入用于打包和解包二进制数据的struct库

# 配置
server_ip = '0.0.0.0'  # 监听所有接口
server_port = 12323
drop_rate = 0.5  # 发送失败率设为50%,更容易出现丢包,大量数据下实际丢包率应为0.5*0.5*0.5=0.125

# 初始化服务器socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建一个UDP socket
server_socket.bind((server_ip, server_port))  # 将socket绑定到指定的IP地址和端口


# 创建响应报文的辅助函数
def create_response(seq_no, version):
    system_time = datetime.now().strftime('%H-%M-%S')  # 获取当前系统时间，并格式化为"小时-分钟-秒"
    # 打包响应报文，包含序列号、版本号和系统时间，时间部分用0填充至200字节
    response = struct.pack('!H B 200s', seq_no, version, system_time.encode().ljust(200, b'\x00'))
    return response  # 返回打包好的响应报文


# 解析客户端报文的辅助函数
def parse_packet(packet):
    # 解包客户端报文，按照"2字节序列号, 1字节版本号, 200字节数据"的格式
    seq_no, version, data = struct.unpack('!H B 200s', packet)
    return seq_no, version, data.decode('utf-8').strip()  # 返回序列号、版本号和数据（去掉填充的空白）


print(f"服务器在 {server_ip}:{server_port} 上监听")  # 打印服务器启动信息

try:
    while True:  # 无限循环，持续监听和处理客户端请求
        data, client_address = server_socket.recvfrom(2048)  # 接收来自客户端的报文，最大接收2048字节
        seq_no, version, client_data = parse_packet(data)  # 解析接收到的报文

        print(f"收到来自 {client_address} 的数据包 - 序号: {seq_no}, 版本: {version}, 数据: {client_data}")  # 打印接收到的报文信息

        if random.random() > drop_rate:  # 随机生成一个0到1之间的浮点数，如果大于丢包率则不丢包
            response = create_response(seq_no, version)  # 创建响应报文
            server_socket.sendto(response, client_address)  # 发送响应报文给客户端
            server_time = datetime.now().strftime('%H:%M:%S')  # 获取当前系统时间，并格式化为"小时:分钟:秒"
            print(f"响应客户端 {client_address} - 序号: {seq_no}, 版本: {version}, 服务器时间: {server_time}")  # 打印响应信息
        else:
            print(f"丢弃客户端 {client_address} 的数据包 - 序号: {seq_no}")  # 如果随机数小于等于丢包率，则丢弃报文并打印丢弃信息

except KeyboardInterrupt:  # 捕获键盘中断（如Ctrl+C）
    print("服务器关闭中...")  # 打印服务器关闭中的信息

finally:
    server_socket.close()  # 关闭服务器socket
    print("服务器已关闭")  # 打印服务器已关闭的信息
