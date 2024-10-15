import socket
import struct
import threading
import sys

# Definições dos tipos de mensagens
MSG_OI = 0      # Mensagem para se identificar no servidor
MSG_TCHAU = 1   # Mensagem para desconectar do servidor
MSG_MSG = 2     # Mensagem de texto entre clientes
MSG_ERRO = 3    # Mensagem de erro retornada pelo servidor
PROMPT_MESSAGE = ''

# Verifica se os parâmetros foram passados corretamente
if len(sys.argv) < 5:
    print("Uso: client.py <ID> <Nome> <IP do Servidor> <Porta>\n")
    sys.exit(1)

# Define o ID do cliente, nome de usuário, IP e porta do servidor
user_id = int(sys.argv[1])
username = sys.argv[2][:20].ljust(20, '\x00')  # Garantir tamanho de 20 caracteres para o nome
server_ip = sys.argv[3]
server_port = int(sys.argv[4])

# Inicializa o socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Função para enviar mensagens ao servidor
def send_message(msg_type, dest_id=0, message=""):
    # Monta a estrutura da mensagem
    message_size = len(message)
    packet = struct.pack("!IIII", msg_type, user_id, dest_id, message_size)
    packet += username.encode()  # Adiciona o nome do usuário
    packet += message.encode()   # Adiciona o texto da mensagem
    # Envia a mensagem para o servidor
    client_socket.sendto(packet, (server_ip, server_port))
    print(f"Enviado: {msg_type}, {user_id}, {dest_id}, {message_size}, {username}, {message}")

# Função para receber e exibir mensagens do servidor
def receive_messages():
    while True:
        try:
            data, _ = client_socket.recvfrom(1024)
            msg_type, origin_id, dest_id, msg_size = struct.unpack("!IIII", data[:16])
            origin_name = data[16:36].decode().strip('\x00')
            message = data[36:36 + msg_size].decode()

            print(f"Recebido: {msg_type}, {origin_id}, {dest_id}, {msg_size}, {origin_name}, {message}") # Para debug
            if msg_type == MSG_MSG:
                if origin_id == 0:
                    print(f"[Servidor] {message}")  
                elif dest_id == 0:  # Broadcast para todos
                    if origin_id == user_id:
                        print(f"[Broadcast (Você)] {origin_name}: {message}")
                    else:
                        print(f"[Broadcast] {origin_name}: {message}")  
                elif dest_id == user_id:  # Mensagem privada
                    print(f"[Privado] {origin_name}: {message}")
                else:
                   print(f"[Mensagem desconhecida] {message}")

            elif msg_type == MSG_ERRO:
                print(f"[ERRO] {message}")
            elif msg_type == MSG_OI:
                print(f"[Servidor] Conexão aceita: {message}")
            else:
                print(f"[Mensagem desconhecida] {message}")

            print(PROMPT_MESSAGE)

        except struct.error:
            print("Erro ao desempacotar mensagem.")
            break
        except UnicodeDecodeError:
            print("Erro ao decodificar mensagem.")
            break
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break

# Envia a mensagem de identificação "OI" para o servidor
send_message(MSG_OI)
print("Conectado ao servidor.")

# Inicia uma thread para receber mensagens do servidor
threading.Thread(target=receive_messages, daemon=True).start()

# Loop principal para enviar mensagens
try:
    while True:
        try:
            # Usuário entra o ID do destinatário
            PROMPT_MESSAGE = "\n--- MENU ---\nlst - lista usuários online\n0 - envia mensagem para todos\nnúmero - envia mensagem para usuário específico\n"
            dest = input(PROMPT_MESSAGE+"\n")

            # pede pro servidor enviar lista de usuários
            if dest == "lst":
                send_message(MSG_MSG, 0, "lst")
                continue

            dest_id = int(dest)
            if dest_id < 0:
                print("[ERRO] ID de destino inválido. Tente novamente.")
                continue  # Volta a pedir o ID

            # Só pede a mensagem se o ID for válido
            PROMPT_MESSAGE = "Digite sua mensagem:"
            msg = input(PROMPT_MESSAGE+"\n")
            if msg.strip() == "":  # Verifica se a mensagem não é vazia
                print("[ERRO] Mensagem vazia. Tente novamente.")
                continue

            # Envia a mensagem para o servidor
            send_message(MSG_MSG, dest_id, msg)
        except ValueError:
            print("ID inválido. Tente novamente.")
            continue
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            break
except KeyboardInterrupt:
    # Se o usuário interromper, envia mensagem de "TCHAU" e encerra
    send_message(MSG_TCHAU)
    print("Desconectado do servidor.")
    client_socket.close()
    sys.exit(0)
finally:
    client_socket.close()
    sys.exit(0)
