import socket
import struct
import threading
import sys

# Definições das mensagens
MSG_OI = 0
MSG_TCHAU = 1
MSG_MSG = 2
MSG_ERRO = 3

# Parâmetros do cliente
if len(sys.argv) < 5:
    print("Uso: cliente.py <ID> <Nome> <IP do Servidor> <Porta>")
    sys.exit(1)

user_id = int(sys.argv[1])
username = sys.argv[2][:20].ljust(20, '\x00')  # Garantir tamanho de 20 caracteres
server_ip = sys.argv[3]
server_port = int(sys.argv[4])

# Inicialização do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Função para enviar mensagem ao servidor
def send_message(msg_type, dest_id=0, message=""):
    message_size = len(message)
    packet = struct.pack("!IIII", msg_type, user_id, dest_id, message_size)
    packet += username.encode()
    packet += message.encode()
    client_socket.sendto(packet, (server_ip, server_port))

# Thread para receber e exibir mensagens
def receive_messages():
    while True:
        data, _ = client_socket.recvfrom(1024)
        msg_type, origin_id, dest_id, msg_size = struct.unpack("!IIII", data[:16])
        origin_name = data[16:36].decode().strip('\x00')
        message = data[36:36+msg_size].decode()

        if msg_type == MSG_MSG:
            if dest_id == 0:
                print(f"[Broadcast] {origin_name}: {message}")
            else:
                print(f"[Privado de {origin_name}]: {message}")
        elif msg_type == MSG_ERRO:
            print(f"[ERRO]: {message}")
        else:
            print(f"[Mensagem desconhecida] {message}")

# Envio da mensagem de OI
send_message(MSG_OI)
print("Conectado ao servidor.")

# Iniciar thread para receber mensagens
threading.Thread(target=receive_messages, daemon=True).start()

# Loop para envio de mensagens
try:
    while True:
        dest = input("Digite o ID do destinatário (0 para todos): ")
        dest_id = int(dest)
        msg = input("Digite sua mensagem: ")
        send_message(MSG_MSG, dest_id, msg)
except KeyboardInterrupt:
    # Enviar mensagem de TCHAU e encerrar
    send_message(MSG_TCHAU)
    print("Desconectado do servidor.")
    client_socket.close()
    sys.exit(0)
