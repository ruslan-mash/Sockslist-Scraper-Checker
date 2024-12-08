# локальный сервер для подключения по local ip к найденным прокси
# протокол socks5 без аутентификации

# import socket
# import threading
# import struct
# import random
# import socks
#
# LOCAL_IP = '127.0.0.1'
# LOCAL_PORT = 12121
#
# # Читаем список SOCKS5-прокси из файла
# socks5_proxies = []
# with open('socks5_proxies.txt', 'r') as file:
#     socks5_proxies = [line.strip() for line in file.readlines()]
#
# # Обработка входящих соединений от клиента
# def handle_client(client_socket):
#     try:
#         # Принятие запроса от клиента
#         client_socket.recv(262)
#
#         # Отправить ответ: аутентификация не требуется
#         client_socket.sendall(b"\x05\x00")
#
#         # Получаем запрос на соединение
#         version, cmd, _, address_type = struct.unpack("!BBBB", client_socket.recv(4))
#
#         # Обработка различных типов адресов
#         if address_type == 1:  # IPv4
#             client_socket.recv(4)  # Пропускаем IP-адрес
#         elif address_type == 3:  # доменное имя
#             domain_length = client_socket.recv(1)[0]
#             client_socket.recv(domain_length)  # Пропускаем имя хоста
#         else:
#             client_socket.sendall(b"\x05\x08")  # Ошибка адреса
#             client_socket.close()
#             return
#
#         # Пропускаем порт назначения
#         client_socket.recv(2)
#
#         # Случайным образом выбираем прокси из списка
#         proxy = random.choice(socks5_proxies)
#         proxy_ip, proxy_port = proxy.split(":")
#         proxy_port = int(proxy_port)
#
#         # Устанавливаем соединение с выбранным прокси-сервером через SOCKS5
#         remote_socket = socks.socksocket()
#         remote_socket.setproxy(socks.SOCKS5, proxy_ip, proxy_port)
#         try:
#             remote_socket.connect((proxy_ip, proxy_port))
#         except socket.error as e:
#             client_socket.sendall(b"\x05\x05")  # Ошибка соединения
#             client_socket.close()
#             remote_socket.close()
#             return
#
#         # Отправляем клиенту успешный ответ
#         client_socket.sendall(b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack("!H", 1080))
#
#         # Начинаем пересылку данных между клиентом и прокси
#         threading.Thread(target=forward, args=(client_socket, remote_socket)).start()
#         threading.Thread(target=forward, args=(remote_socket, client_socket)).start()
#
#     except Exception as e:
#         print(f"Error handling client: {e}")
#     finally:
#         try:
#             client_socket.close()
#         except:
#             pass  # Если сокет уже закрыт, игнорируем ошибку
#
#
# # Пересылка данных между клиентом и прокси
# def forward(source, destination):
#     try:
#         while True:
#             if source.fileno() == -1 or destination.fileno() == -1:
#                 break  # Если сокет закрыт, выходим из цикла
#             data = source.recv(4096)
#             if len(data) == 0:
#                 break
#             destination.sendall(data)
#     except Exception as e:
#         print(f"Error forwarding data: {e}")
#     finally:
#         try:
#             if not source._closed:
#                 source.close()
#             if not destination._closed:
#                 destination.close()
#         except:
#             pass  # Если сокет уже закрыт, игнорируем ошибку
#
#
# # Запуск прокси-сервера
# def start_server():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((LOCAL_IP, LOCAL_PORT))
#     server.listen(5)
#     print(f"Сервер слушает {LOCAL_IP}:{LOCAL_PORT}")
#
#     while True:
#         client_socket, addr = server.accept()
#         print(f"Принято соединение от {addr}")
#         threading.Thread(target=handle_client, args=(client_socket,)).start()
#
#
# if __name__ == "__main__":
#     start_server()
