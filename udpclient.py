import socket
import sys
import time
import struct
import random

# 检查命令行参数
if len(sys.argv) != 3:
    print(f"用法: python {sys.argv[0]} <server_ip> <server_port>")
    sys.exit(1)

try:
    # 从命令行参数获取服务器IP、端口
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
except ValueError as e:
    print(f"参数错误: {e}")
    print(f"用法: {sys.argv[0]} <server_ip> <server_port>")
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

timeout = 0.1
num_packets = 12  # 要发送的报文数量
version = 2  # 报文版本号

# 初始化客户端socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建一个UDP socket
client_socket.settimeout(timeout)  # 设置socket的超时时间


# 创建报文的辅助函数
def create_packet(seq_no, version, data):
    return struct.pack('!H B 200s', seq_no, version, data.encode('utf-8'))  # 按照指定格式打包报文


# 解析报文的辅助函数
def parse_packet(packet):
    seq_no, version, data = struct.unpack('!H B 200s', packet)  # 按照指定格式解包报文
    return seq_no, version, data.decode('utf-8').strip()  # 返回解包后的字段


received_packets = 0  # 接收到的报文数量
rtts = []  # 存储RTT的列表
start_time = None  # 记录开始时间
end_time = None  # 记录结束时间

for seq_no in range(1, num_packets + 1):  # 循环发送num_packets个报文
    data = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=200))  # 生成200个随机字母组成的数据
    packet = create_packet(seq_no, version, data)  # 创建报文
    attempts = 0  # 重传次数

    while attempts < 3:  # 每个报文最多重传3次
        client_socket.sendto(packet, (server_ip, server_port))  # 发送报文
        try:
            if start_time is None:
                start_time = time.time()  # 记录第一次发送的开始时间
            start = time.time()  # 记录发送时间
            response, addr = client_socket.recvfrom(2048)  # 接收服务器的响应
            end = time.time()  # 记录接收时间
            rtt = (end - start) * 1000  # 计算RTT，以毫秒为单位
            received_seq_no, received_version, received_data = parse_packet(response)  # 解析服务器响应的报文
            server_time = received_data[0:8].strip()  # 获取服务器时间
            print(f"序列号: {received_seq_no}, 服务器IP:{server_ip}, 端口:{server_port}, RTT = {rtt:.2f} ms, 服务器时间 = {server_time}")
            rtts.append(rtt)  # 将RTT加入列表
            received_packets += 1  # 接收的报文数加1
            if end_time is None:
                end_time = time.time()  # 记录第一次接收的结束时间
            else:
                end_time = max(end_time, time.time())  # 更新结束时间
            break  # 成功接收到响应，退出重传循环
        except socket.timeout:  # 超时处理
            attempts += 1  # 增加重传次数
            print(f"序列号: {seq_no}, 请求超时")
        if attempts == 3:  # 如果重传3次都失败
            print(f"序列号: {seq_no}, 重传失败")

# 汇总信息
if received_packets > 0:
    max_rtt = max(rtts)  # 最大RTT
    min_rtt = min(rtts)  # 最小RTT
    avg_rtt = sum(rtts) / len(rtts)  # 平均RTT
    rtt_std_dev = (sum((x - avg_rtt) ** 2 for x in rtts) / len(rtts)) ** 0.5  # RTT标准差
    total_response_time = end_time - start_time if end_time and start_time else 0  # 服务器总响应时间
    print(
        f"汇总:\n接收的报文数: {received_packets}\n丢包率: {(1 - received_packets / num_packets) * 100:.2f}%\n最大RTT: {max_rtt:.2f} ms\n最小RTT: {min_rtt:.2f} ms\n平均RTT: {avg_rtt:.2f} ms\nRTT标准差: {rtt_std_dev:.2f} ms\n服务器总响应时间: {total_response_time:.2f} s")
else:
    print("未接收到任何报文。")

client_socket.close()  # 关闭socket
