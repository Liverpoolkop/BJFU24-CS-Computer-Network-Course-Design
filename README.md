# BJFU24-CS-Computer-Network-Course-Design
# UDP Server and Client
这是一个简单的 UDP 服务器和客户端示例项目，用于演示基本的 UDP 通信和报文处理。
服务器接收客户端发送的报文，并根据一定的丢包率模拟网络丢包，客户端则发送多个报文并计算往返时间（RTT）。
# 文件结构
udpserver.py - 服务器端代码
udpclient.py - 客户端代码
# 运行环境
Python 3.6 及以上
操作系统：Windows, macOS, Linux
# 安装
在运行代码之前，请确保已安装 Python 3.6 及以上版本。如果未安装，请前往 Python 官网 下载并安装。
# 使用方法
1.运行服务器端
打开终端或命令提示符。
运行以下命令启动服务器：
python udpserver.py
2.运行客户端
打开终端或命令提示符。
运行以下命令启动客户端，替换 <server_ip> 和 <server_port> 为实际的服务器 IP 和端口：
python udpclient.py <server_ip> <server_port>
例如：python udpclient.py 127.0.0.1 12323
# 配置选项
服务器：udpserver.py
server_ip：服务器监听的 IP 地址，默认为 '0.0.0.0'，表示监听所有接口。
server_port：服务器监听的端口，默认为 12323。
drop_rate：模拟网络丢包率，默认为 0.5（即 50% 的概率丢包）。
客户端：udpclient.py
timeout：客户端接收超时时间，默认为 0.1 秒。
num_packets：客户端发送的报文数量，默认为 12。
version：报文版本号，默认为 2。
# 注意事项
确保在运行客户端之前，服务器已经启动并正在监听指定的 IP 和端口。
请根据实际需要调整 server_port 和 drop_rate 参数，以适应不同的网络环境。
客户端默认发送 12 个报文，每个报文的最大重传次数为 3 次，超时时间为 0.1 秒，可以根据需要进行调整。

# Reverse TCP Server 和 Reverse UDP Client
该项目包含两个主要组件：reversetcpserver 和 reverseudpclient。
reversetcpserver 是一个反转字符串的 TCP 服务器
而 reverseudpclient 是一个向服务器发送字符串并接收反转字符串的 UDP 客户端。
# 文件结构
reversetcpserver.py - 服务器端代码
reverseudpclient.py - 客户端代码
test.txt - 测试用文本文件
# 运行环境
Python 3.6 及以上
操作系统：Windows, macOS, Linux
# 安装
在运行代码之前，请确保已安装 Python 3.6 及以上版本。如果未安装，请前往 Python 官网 下载并安装。
# 使用方法
1.运行服务器端
打开终端或命令提示符。
运行以下命令启动服务器：
python reversetcpserver.py
2.运行客户端
打开终端或命令提示符。
运行以下命令启动客户端：
python reverseudpclient.py <server_ip> <server_port> <Lmin> <Lmax> <file_path>
例如：python reverseudpclient.py 127.0.0.1 12323 5 10 sample.txt
# 配置选项
服务器端：reversetcpserver.py
server_ip：服务器监听的 IP 地址，默认为 '0.0.0.0'，表示监听所有接口。
server_port：服务器监听的端口，默认为 12323。
客户端：reverseudpclient.py
运行客户端时需要提供以下命令行参数：
server_ip: 服务器 IP 地址
server_port: 服务器端口号
Lmin: 最小块长度
Lmax: 最大块长度
file_path: 待处理文件路径
# 注意事项
确保在运行客户端之前，服务器已经启动并正在监听指定的 IP 和端口。
确保参数设置正确
