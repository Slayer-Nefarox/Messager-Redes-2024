import socket
import struct
import threading
import time
from tkinter import Tk, Label, Listbox, END, Button, Entry

# Definição dos tipos de mensagens
MSG_OI = 0      # Identificação de conexão
MSG_TCHAU = 1   # Encerrar conexão
MSG_MSG = 2     # Mensagem de texto
MSG_ERRO = 3    # Mensagem de erro
MSG_LISTA_CLIENTES = 4

class ServerApp:
    def __init__(self):
        self.clients = {}  # Dicionário para armazenar clientes conectados {id_cliente: (endereço, nome)}
        self.server_socket = None  # Socket do servidor
        self.start_gui()  # Inicia a interface gráfica

    def start_gui(self):
        """Método que inicializa a interface gráfica do servidor"""
        self.window = Tk()
        self.window.title("Servidor")

        # Detecta o IP automaticamente
        hostname = socket.gethostname()  # Obtém o nome do host
        ip_address = socket.gethostbyname(hostname)  # Obtém o IP da máquina

        # Entrada para o IP do servidor, preenchido automaticamente
        self.label_ip = Label(self.window, text="IP do Servidor:")
        self.label_ip.pack()
        self.entry_ip = Entry(self.window)
        self.entry_ip.insert(0, ip_address)  # Preenche o IP automaticamente
        self.entry_ip.pack()

        # Entrada para a porta do servidor, sugerida automaticamente (porta maior que 1234)
        self.label_port = Label(self.window, text="Porta (maior que 1234):")
        self.label_port.pack()
        self.entry_port = Entry(self.window)
        self.entry_port.insert(0, "1235")  # Sugere a porta 1235 por padrão
        self.entry_port.pack()

        # Botão para iniciar o servidor
        self.start_button = Button(self.window, text="Iniciar Servidor", command=self.start_server)
        self.start_button.pack()

        # Exibição de clientes conectados
        self.label_clients = Label(self.window, text="Clientes conectados:")
        self.label_clients.pack()

        self.client_list = Listbox(self.window)
        self.client_list.pack(fill="both", expand=True)

        # Botão para desligar o servidor
        self.shutdown_button = Button(self.window, text="Desligar Servidor", command=self.shutdown_server)
        self.shutdown_button.pack()

        # Configura fechamento da janela
        self.window.protocol("WM_DELETE_WINDOW", self.shutdown_server)
        self.window.mainloop()

    def start_server(self):
        """Inicia o servidor e escuta conexões"""
        try:
            # Obtém o IP e a porta da interface gráfica
            ip = self.entry_ip.get().strip()
            port = int(self.entry_port.get())

            # Verifica se a porta é maior que 1234
            if port <= 1234:
                self.update_status("[ERRO] A porta deve ser maior que 1234.")
                return

            # Criação do socket do servidor (UDP)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((ip, port))

            # Desabilita o botão de iniciar servidor após a execução
            self.start_button.config(state="disabled")

            # Inicia threads para receber mensagens e enviar status do servidor
            threading.Thread(target=self.receive_messages, daemon=True).start()
            threading.Thread(target=self.send_server_status, daemon=True).start()

            self.update_status(f"Servidor iniciado em {ip}:{port}")  # Atualiza o status na interface
        except Exception as e:
            self.update_status(f"[ERRO] Falha ao iniciar o servidor: {e}")

    def send_message(self, msg_type, origin_id, dest_id, addr, username="", message=""):
        """Método para enviar mensagens para os clientes"""
        message_size = len(message)  # Tamanho da mensagem
        # Empacota a mensagem para enviar em formato binário
        packet = struct.pack("!IIII", msg_type, origin_id, dest_id, message_size)
        packet += username.encode().ljust(20, b'\x00')  # Nome com 20 caracteres
        packet += message.encode().ljust(140, b'\x00')  # Mensagem com até 140 caracteres
        self.server_socket.sendto(packet, addr)  # Envia o pacote para o cliente

    def handle_message(self, data, addr):
        """Método para tratar diferentes tipos de mensagens recebidas dos clientes"""
        try:
            # Desempacota a mensagem recebida
            msg_type, origin_id, dest_id, msg_size = struct.unpack("!IIII", data[:16])
            username = data[16:36].decode().strip('\x00')  # Nome do cliente
            message = data[36:36 + msg_size].decode(errors='replace')  # Mensagem de texto

            # Trata diferentes tipos de mensagens
            if msg_type == MSG_OI: # Conecta o client
                self.handle_connection(origin_id, username, addr)
            elif msg_type == MSG_TCHAU: # Desconecta o client
                self.handle_disconnection(origin_id)
            elif msg_type == MSG_MSG: # Envia a mensagem para o client correto
                self.handle_client_message(origin_id, dest_id, username, message)
            elif msg_type == MSG_LISTA_CLIENTES: # Envia a lista de clientes conectados
                client_list = ', '.join([f" {id}: {name}" for id, (_, name) in self.clients.items()])
                self.send_message(MSG_MSG, 0, origin_id, addr, "Servidor", "Clientes conectados:" + client_list)

            else:
                # Envia uma mensagem de erro se o tipo for desconhecido
                self.send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "Tipo de mensagem desconhecido.")
        except Exception as e:
            print(f"Erro ao tratar a mensagem: {e}")

    def handle_connection(self, origin_id, username, addr):
        """Método para lidar com a conexão de um novo cliente"""
        if (1 <= origin_id <= 999 and origin_id + 1000 in self.clients) or (1001 <= origin_id <= 1999 and origin_id in self.clients): # Se o ID do cliente já estiver em uso, envia um erro
            self.send_message(MSG_ERRO, 0, origin_id, addr, "Servidor", "ID já em uso.")
            return
        else:
            # Adiciona o cliente ao dicionário de clientes conectados
            self.clients[origin_id] = (addr, username)
            self.update_client_list()  # Atualiza a lista de clientes na interface
            self.update_status(f"Cliente {origin_id} ({username}) conectado.")
            self.send_message(MSG_OI, 0, origin_id, addr, "Servidor", "Conexão aceita.")  # Envia confirmação

    def handle_disconnection(self, origin_id):
        """Método para lidar com a desconexão de um cliente"""
        if origin_id in self.clients:
            self.update_status(f"Cliente {origin_id} desconectado.")
            del self.clients[origin_id]  # Remove o cliente do dicionário
            self.update_client_list()  # Atualiza a lista de clientes

    def handle_client_message(self, origin_id, dest_id, username, message):
        """Método para lidar com mensagens enviadas pelos clientes"""
        if origin_id not in self.clients:
            return

        # Se o destino for 0, envia a mensagem para todos os clientes (broadcast)
        if dest_id == 0:
            for client_id, (client_addr, _) in self.clients.items():
                self.send_message(MSG_MSG, origin_id, 0, client_addr, username, message)
        # Caso contrário, envia apenas para o cliente específico
        elif dest_id in self.clients:
            self.send_message(MSG_MSG, origin_id, dest_id, self.clients[dest_id][0], username, message)
        else:
            # Se o ID do destinatário não for encontrado, envia uma mensagem de erro
            self.send_message(MSG_ERRO, 0, origin_id, self.clients[origin_id][0], "Servidor", "ID de destino não encontrado.")

    def receive_messages(self):
        """Método que fica em loop para receber mensagens dos clientes"""
        while True:
            try:
                data, addr = self.server_socket.recvfrom(1024)  # Recebe dados de clientes
                self.handle_message(data, addr)  # Trata a mensagem recebida
            except ConnectionResetError:
                print("Conexão perdida com um cliente.")

    def send_server_status(self):
        """Método que envia o status do servidor periodicamente para os clientes"""
        start_time = time.time()  # Marca o tempo inicial
        while True:
            time.sleep(60)  # Espera 60 segundos
            elapsed_time = time.time() - start_time  # Calcula o tempo decorrido
            status_message = f"Servidor ativo há {elapsed_time:.0f} segundos. Clientes conectados: {len(self.clients)}."
            # Envia o status para todos os clientes conectados
            for client_id, (client_addr, _) in self.clients.items():
                self.send_message(MSG_MSG, 0, client_id, client_addr, "Servidor", status_message)

    def update_client_list(self):
        """Método que atualiza a lista de clientes na interface gráfica"""
        self.client_list.delete(0, END)
        for client_id, (_, username) in self.clients.items():
            self.client_list.insert(END, f"{client_id}: {username}")

    def update_status(self, status):
        """Método que atualiza o status do servidor no terminal (ou na interface)"""
        print(status)  # Por enquanto, apenas imprime o status no terminal

    def shutdown_server(self):
        """Método para desligar o servidor"""

        # Envia mensagem de desconexão para todos os clientes
        try:
            shutdown_message = "Servidor desligado. Conexão encerrada."
            for client_id, (client_addr, _) in self.clients.items():
                self.send_message(MSG_MSG, 0, client_id, client_addr, "Servidor", shutdown_message)
            if self.server_socket:
                self.server_socket.close()  # Fecha o socket do servidor
                self.window.quit()  # Fecha a interface gráfica
        except Exception as e:
            print(f"Erro ao enviar mensagem de desconexão!")

if __name__ == "__main__":
    server = ServerApp()  # Inicia o servidor
