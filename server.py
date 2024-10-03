import socket
import struct
import threading
import time
import sys

# Definições das mensagens
MSG_OI = 0
MSG_TCHAU = 1
MSG_MSG = 2
MSG_ERRO = 3

# Configurações do servidor
server_ip = "0.0.0.0"
server_port = 12345

# Inicializa o socket UDP do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

# Lista de clientes conectados: {id_cliente: (endereço, nome)}
clients = {}

# Função para enviar mensagem ao cliente
def send_message(msg_type, origin_id, dest_id, addr, username="", message=""):
    message_size = len(message)
    packet = struct.pack("!IIII", msg_type, origin_id, dest_id, message_size)
    packet += username.encode().ljust(20, b'\x00')
    packet += message.encode().ljust(140, b'\x00')
    server_socket.sendto(packet, addr)

# Função para tratar mensagens recebidas
def handle_message(data, addr):
    try:
        # Extrai os campos inteiros da mensagem
        msg_type, origin_id, dest_id, msg_size = struct.unpack("!IIII", data[:16])
        username = data[16:36].decode().strip('\x00')

        # Valida a mensagem e extrai o texto, se necessário
        if msg_size > 0:
            if len(data) >= 36 + msg_size:
                message = data[36:36+msg_size].decode(errors='replace')
            else:
                print(f"Erro: Mensagem incompleta recebida de {addr}.")
                return
        else:
            message = ""

        # Lida com os diferentes tipos de mensagens
        if msg_type == MSG_OI:
            if origin_id in clients:
                print(f"Cliente {origin_id} já está conectado.")
                send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "ID já em uso.")
            else:
                # Registra novo cliente
                clients[origin_id] = (addr, username)
                print(f"Cliente {origin_id} ({username}) conectado.")
                send_message(MSG_OI, 0, origin_id, addr, "Servidor", "Conexão aceita.")
        
        elif msg_type == MSG_TCHAU:
            if origin_id in clients:
                print(f"Cliente {origin_id} ({username}) desconectado.")
                del clients[origin_id]
            else:
                print(f"Mensagem TCHAU recebida de cliente não registrado: {origin_id}")

        elif msg_type == MSG_MSG:
            if origin_id not in clients:
                send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "ID de origem não registrado.")
                return
            print(f"Mensagem de {origin_id} para {dest_id}: {message}")
            
            # Envia a mensagem para o destinatário correto
            if dest_id == 0:
                # Envia para todos os clientes
                for client_id, (client_addr, _) in clients.items():
                    send_message(MSG_MSG, origin_id, client_id, client_addr, username, message)
            elif dest_id in clients:
                send_message(MSG_MSG, origin_id, dest_id, clients[dest_id][0], username, message)
            else:
                send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "ID de destino não encontrado.")

        else:
            print(f"Tipo de mensagem desconhecido: {msg_type}")
            send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "Tipo de mensagem desconhecido.")
    
    except struct.error as e:
        print(f"Erro ao desempacotar a mensagem: {e}")
    except UnicodeDecodeError as e:
        print(f"Erro de decodificação de texto: {e}")

# Thread para receber e tratar mensagens
def receive_messages():
    while True:
        data, addr = server_socket.recvfrom(1024)
        handle_message(data, addr)

# Thread para enviar mensagens de status a cada minuto
def send_server_status():
    start_time = time.time()
    while True:
        time.sleep(60)
        elapsed_time = time.time() - start_time
        status_message = f"Servidor ativo há {elapsed_time:.0f} segundos. Clientes conectados: {len(clients)}."
        print(status_message)

        # Envia mensagem de status a todos os clientes
        for client_id, (client_addr, _) in clients.items():
            send_message(MSG_MSG, 0, client_id, client_addr, "Servidor", status_message)

# Iniciar threads
threading.Thread(target=receive_messages, daemon=True).start()
threading.Thread(target=send_server_status, daemon=True).start()

print(f"Servidor iniciado em {server_ip}:{server_port}.")

# Manter o servidor ativo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Encerrando servidor.")
    server_socket.close()
    sys.exit(0)
