import socket
import struct
import threading
from tkinter import Tk, Label, Entry, Button, Listbox, END

# Definição dos tipos de mensagens
MSG_OI = 0      # Identificação de conexão
MSG_TCHAU = 1   # Encerrar conexão
MSG_MSG = 2     # Mensagem de texto
MSG_ERRO = 3    # Mensagem de erro

class ClientApp:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria o socket do cliente (UDP)
        self.connected = False  # Flag de conexão
        self.start_gui()  # Inicia a interface gráfica

    def start_gui(self):
        """Método que inicializa a interface gráfica do cliente"""
        self.window = Tk()
        self.window.title("Cliente")

        # Entrada para o ID do usuário
        self.label_id = Label(self.window, text="ID:")
        self.label_id.pack()
        self.entry_id = Entry(self.window)
        self.entry_id.pack()

        # Entrada para o nome de usuário
        self.label_name = Label(self.window, text="Nome:")
        self.label_name.pack()
        self.entry_name = Entry(self.window)
        self.entry_name.pack()

        # Entrada para o IP do servidor
        self.label_ip = Label(self.window, text="IP do Servidor:")
        self.label_ip.pack()
        self.entry_ip = Entry(self.window)
        self.entry_ip.pack()

        # Entrada para a porta do servidor
        self.label_port = Label(self.window, text="Porta:")
        self.label_port.pack()
        self.entry_port = Entry(self.window)
        self.entry_port.pack()

        # Botão para conectar ao servidor
        self.connect_button = Button(self.window, text="Conectar", command=self.connect_to_server)
        self.connect_button.pack()

        # Botão para desconectar do servidor
        self.disconnect_button = Button(self.window, text="Desconectar", state="disabled", command=self.close_connection)
        self.disconnect_button.pack()

        # Lista para exibir mensagens recebidas
        self.message_list = Listbox(self.window)
        self.message_list.pack(fill="both", expand=True)

        # Entrada para o ID do destinatário
        self.label_dest = Label(self.window, text="ID do destinatário:")
        self.label_dest.pack()
        self.entry_dest = Entry(self.window)
        self.entry_dest.pack()

        # Entrada para a mensagem
        self.label_msg = Label(self.window, text="Mensagem:")
        self.label_msg.pack()
        self.entry_msg = Entry(self.window)
        self.entry_msg.pack()

        # Botão para enviar mensagem
        self.send_button = Button(self.window, text="Enviar", state="disabled", command=self.send_msg)
        self.send_button.pack()

        # Configura o fechamento da janela
        self.window.protocol("WM_DELETE_WINDOW", self.close_connection)
        self.window.mainloop()

    def connect_to_server(self):
        """Método para conectar ao servidor"""
        try:
            # Obtém os dados da interface
            self.user_id = int(self.entry_id.get())
            self.username = self.entry_name.get().strip()
            self.server_ip = self.entry_ip.get().strip()
            self.server_port = int(self.entry_port.get())

            # Validação do nome de usuário
            if not self.username:
                self.message_list.insert(END, "[ERRO] Nome não pode ser vazio.")
                return

            # Envia a mensagem de conexão
            self.send_message(MSG_OI, 0, f"Conectando como {self.username}...")
            threading.Thread(target=self.receive_messages, daemon=True).start()  # Inicia thread para receber mensagens

            # Desabilita o botão de conectar e habilita o de enviar
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
            self.send_button.config(state="normal")
        except Exception as e:
            self.message_list.insert(END, f"[ERRO] Falha na conexão. Tente novamente!")

    def send_message(self, msg_type, dest_id=0, message=""):
        """Método para enviar mensagens ao servidor"""
        message_size = len(message)  # Calcula o tamanho da mensagem
        # Empacota a mensagem para enviar em formato binário
        packet = struct.pack("!IIII", msg_type, self.user_id, dest_id, message_size)
        packet += self.username.encode().ljust(20, b'\x00')  # Nome com 20 caracteres
        packet += message.encode().ljust(140, b'\x00')  # Mensagem com até 140 caracteres
        self.client_socket.sendto(packet, (self.server_ip, self.server_port))  # Envia o pacote

    def receive_messages(self):
        """Método que fica em loop para receber mensagens do servidor"""
        while True:
            try:
                # Recebe dados do servidor
                data, _ = self.client_socket.recvfrom(1024)
                msg_type, origin_id, dest_id, msg_size = struct.unpack("!IIII", data[:16])
                origin_name = data[16:36].decode().strip('\x00')  # Nome do remetente
                message = data[36:36 + msg_size].decode()  # Mensagem

                # Trata diferentes tipos de mensagens
                if msg_type == MSG_MSG:
                    if origin_id == 0:
                        self.message_list.insert(END, f"[Servidor] {message}")
                    elif dest_id == 0:
                        self.message_list.insert(END, f"[Broadcast] {origin_name}: {message}")
                    elif dest_id == self.user_id:
                        self.message_list.insert(END, f"[Privado] {origin_name}: {message}")
                elif msg_type == MSG_ERRO:
                    self.message_list.insert(END, f"[ERRO] {message}")
                elif msg_type == MSG_OI:
                    self.connected = True
                    self.message_list.insert(END, f"[Servidor] {message}")
            except Exception as e:
                self.message_list.insert(END, f"[ERRO] Falha ao receber mensagem: {e}")
                break

    def send_msg(self):
        """Método para enviar uma mensagem ao destinatário"""
        try:
            dest_id = int(self.entry_dest.get())  # Obtém o ID do destinatário
            message = self.entry_msg.get()  # Obtém a mensagem
            if message.strip():  # Se a mensagem não for vazia
                self.send_message(MSG_MSG, dest_id, message)  # Envia a mensagem
                self.entry_msg.delete(0, END)  # Limpa a entrada de mensagem
        except ValueError:
            self.message_list.insert(END, "[ERRO] ID do destinatário inválido.")  # Se o ID não for válido

    def close_connection(self):
        """Método para encerrar a conexão com o servidor"""
        if self.connected:
            self.send_message(MSG_TCHAU)  # Envia a mensagem de desconexão
            self.client_socket.close()  # Fecha o socket do cliente
            self.connected = False  # Atualiza o status de conexão
            self.message_list.insert(END, "[INFO] Desconectado do servidor.")

        # Resetar botões e inputs da GUI
        self.connect_button.config(state="normal")  # Habilita o botão de conectar
        self.disconnect_button.config(state="disabled")  # Desabilita o botão de desconectar
        self.send_button.config(state="disabled")  # Desabilita o botão de enviar mensagens

        # Fecha a janela 
        self.window.destroy()

if __name__ == "__main__":
    client = ClientApp()  # Inicia o cliente
