import socket
import struct
import threading
import time
import sys

# Definições dos tipos de mensagens
MSG_OI = 0      # Mensagem de identificação (início de conexão)
MSG_TCHAU = 1   # Mensagem para encerrar conexão
MSG_MSG = 2     # Mensagem de texto
MSG_ERRO = 3    # Mensagem de erro enviada pelo servidor

# Configurações do servidor
if len(sys.argv) < 2:
    print("Uso: server.py <Porta>")
    sys.exit(1)
else:
    server_port = int(sys.argv[1])

# Obtém o IP da máquina
hostname = socket.gethostname()
server_ip = socket.gethostbyname(hostname)
print(f"Servidor iniciado em {server_ip}:{server_port}")

# Inicializa o socket UDP do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

# Dicionário para manter clientes conectados {id_cliente: (endereço, nome)}
clients = {}

# Função para enviar mensagens aos clientes
def send_message(msg_type, origin_id, dest_id, addr, username="", message=""):
    message_size = len(message)
    packet = struct.pack("!IIII", msg_type, origin_id, dest_id, message_size)
    packet += username.encode().ljust(20, b'\x00')  # Garante 20 caracteres no nome
    packet += message.encode().ljust(140, b'\x00')  # Garante até 140 caracteres na mensagem
    server_socket.sendto(packet, addr)
    print(f"Enviado: {msg_type}, {origin_id}, {dest_id}, {message_size}, {username}, {message}")

# Função para processar mensagens recebidas dos clientes
def handle_message(data, addr):
    try:
        # Desempacota os dados da mensagem
        msg_type, origin_id, dest_id, msg_size = struct.unpack("!IIII", data[:16])
        username = data[16:36].decode().strip('\x00')
        message = data[36:36 + msg_size].decode(errors='replace')

        # Processa mensagens de acordo com o tipo
        if msg_type == MSG_OI:
            # Verifica se o cliente já está conectado
            if origin_id in clients:
                send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "ID já em uso.")
            else:
                # Adiciona cliente à lista
                clients[origin_id] = (addr, username)
                print(f"Cliente {origin_id} ({username}) conectado.")
                send_message(MSG_OI, 0, origin_id, addr, "Servidor", "Conexão aceita.")
        
        elif msg_type == MSG_TCHAU:
            # Remove o cliente da lista
            if origin_id in clients:
                print(f"Cliente {origin_id} desconectado.")
                del clients[origin_id]
            else:
                print(f"Cliente {origin_id} tentou se desconectar sem estar registrado.")

        elif msg_type == MSG_MSG:

            # lst: lista de clientes conectados
            if message == "lst":
                client_list = {client_id: client_data[1] for client_id, client_data in clients.items()}
                print(client_list)
                client_list = "\nLista de clientes conectados:\n"+str(client_list).replace("{","").replace("}","").replace(", ","\n").replace(":"," - ").replace(" '","").replace("'","")
                send_message(MSG_MSG, 0, origin_id, addr, "Servidor", str(client_list))
                return

            # Envia a mensagem para todos (broadcast) ou para um cliente específico
            if origin_id not in clients:
                send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "ID de origem não registrado.")
                return

            print(f"Mensagem de {origin_id} para {dest_id}: {message}")

            # Enviar mensagem de broadcast para todos os clientes, exceto o remetente
            if dest_id == 0:  # Broadcast para todos 
                for client_id, (client_addr, _) in clients.items():
                    send_message(MSG_MSG, origin_id, 0, client_addr, username, message)
                    
            elif dest_id in clients:  # Mensagem privada
                send_message(MSG_MSG, origin_id, dest_id, clients[dest_id][0], username, message)
            else:
                send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "ID de destino não encontrado ou inválido.")

        else:
            # Mensagem desconhecida
            send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "Tipo de mensagem desconhecido.")
    
    except struct.error as e:
        print(f"Erro ao desempacotar a mensagem: {e}")
    except UnicodeDecodeError as e:
        print(f"Erro ao decodificar texto: {e}")

# Função para receber mensagens dos clientes
def receive_messages():
    while True:
        data, addr = server_socket.recvfrom(1024)
        handle_message(data, addr)
        

# Função para enviar status do servidor periodicamente (a cada minuto)
def send_server_status():
    start_time = time.time()
    while True:
        time.sleep(60)
        elapsed_time = time.time() - start_time
        status_message = f"Servidor ativo há {elapsed_time:.0f} segundos. Clientes conectados: {len(clients)}."
        print(status_message)

        # Envia status para todos os clientes
        for client_id, (client_addr, _) in clients.items():
            send_message(MSG_MSG, 0, client_id, client_addr, "Servidor", status_message)

# Inicia a thread para enviar status do servidor
threading.Thread(target=send_server_status, daemon=True).start()

# Inicia a função principal de recepção de mensagens
receive_messages()