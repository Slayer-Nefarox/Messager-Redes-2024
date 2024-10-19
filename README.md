# Sistema de Troca de Mensagens utilizando UDP com Servidor e Multi-Clientes 📨

Este projeto implementa um sistema de troca de mensagens simples (similar a um mini-Twitter) utilizando o protocolo UDP. O sistema permite que múltiplos clientes se conectem a um servidor, enviem mensagens entre si e recebam atualizações periódicas do servidor sobre o estado do sistema.

## Descrição Geral 📄

O sistema consiste em:
- **Um servidor:** responsável por gerenciar as comunicações entre os clientes, incluindo o envio de mensagens e a manutenção de uma lista de clientes ativos.
- **Clientes:** que podem enviar e receber mensagens do servidor e entre si. Cada cliente se identifica por um número inteiro único e pode trocar mensagens com todos os clientes ou enviar mensagens específicas.

## Tecnologias Utilizadas 🛠️

- Linguagem de Programação: Python
- Comunicação via **Sockets** utilizando o protocolo **UDP**
- Controle de múltiplos clientes por meio de **Threads** no servidor

## Funcionalidades do Sistema 📡

### Servidor 🖥️

O servidor é responsável por:

- Receber mensagens de **OI**, **TCHAU** e **MSG** dos clientes:
  - **OI:** Utilizada para registro no sistema.
  - **TCHAU:** Utilizada para sinalizar a saída do cliente do sistema.
  - **MSG:** Utilizada para enviar mensagens entre os clientes.
  
- Manter uma lista de clientes ativos, associando cada cliente ao seu identificador único.

- Enviar mensagens periódicas a todos os clientes conectados com informações gerais sobre o estado do sistema, como número de clientes conectados e mensagens recentes.

- Controlar a comunicação de forma concorrente, garantindo que múltiplos clientes possam se comunicar simultaneamente através de threads.

### Cliente 🫡

O cliente é responsável por:

- Enviar uma mensagem **OI** ao servidor para se registrar.
- Enviar mensagens **MSG** que podem ser:
  - Mensagens públicas (para todos os clientes).
  - Mensagens privadas (para um cliente específico).
  
- Receber e exibir mensagens enviadas por outros clientes ou pelo servidor.
- Enviar uma mensagem **TCHAU** para informar ao servidor que está saindo do sistema.

## Estrutura do Projeto 📁

O projeto contém os seguintes arquivos:

- `server.py`: Implementação do servidor.
- `client.py`: Implementação do cliente.
- `README.md`: Este arquivo de instruções.

## Instruções de Execução 📝

### Executando o Servidor

O servidor deve ser iniciado primeiro para que os clientes possam se conectar. Ele gerencia todas as conexões e a troca de mensagens. Para iniciar o servidor, utilize o seguinte comando:

```bash
python server.py
```

Ao iniciar o servidor, a interface gráfica mostrará o IP e a porta usados pelo servidor. A lista de clientes conectados será atualizada automaticamente.

###  Comandos do servidor:

- Iniciar servidor: Insira o IP e a porta e clique no botão para iniciar o servidor.
- Desligar servidor: Fecha o servidor e desconecta todos os clientes.


### Como executar o cliente:

Abra um terminal.
Navegue até o diretório do projeto.
Execute o arquivo client.py com o comando:

```bash
python client.py
```

Ao executar o cliente, insira seu ID, nome de usuário, IP do servidor e porta. Clique em Conectar para estabelecer a conexão com o servidor.

### Funcionalidades do cliente:

- Enviar mensagem privada: Insira o ID do destinatário e a mensagem, e clique em Enviar.
- Enviar mensagem em broadcast: Para enviar uma mensagem para todos, insira "0" no campo de ID do destinatário.
- Solicitar lista de clientes: Clique em Lista de Clientes para visualizar os clientes conectados ao servidor.
- Desconectar: Clique em Desconectar para encerrar a conexão com o servidor.
Protocolo de Mensagens

As mensagens trocadas entre o servidor e os clientes seguem um formato específico usando a biblioteca struct para empacotar os dados em formato binário:

- MSG_OI (0): Identifica uma nova conexão do cliente.
- MSG_TCHAU (1): Solicita a desconexão do cliente.
- MSG_MSG (2): Envia uma mensagem (privada ou broadcast).
- MSG_ERRO (3): Envia uma mensagem de erro.
- MSG_LISTA_CLIENTES (4): Solicita ou envia a lista de clientes conectados.

Cada mensagem contém os seguintes campos:

Tipo da mensagem (4 bytes)
ID de origem (4 bytes)
ID de destino (4 bytes)
Tamanho da mensagem (4 bytes)
Nome do usuário (20 bytes)
Mensagem (140 bytes)
Estrutura do Projeto

```
bash
├── server.py          # Código do servidor UDP
└── client.py          # Código do cliente UDP
```

Exemplo de Execução
- Servidor:
    - Mensagem de status: O servidor envia mensagens periódicas sobre o tempo de atividade e o número de clientes conectados.
    - Lista de clientes: Quando solicitado, o servidor responde com a lista de IDs e nomes dos clientes conectados.
- Cliente:
    - de broadcast: O cliente pode enviar mensagens que serão recebidas por todos os clientes conectados.
    - Mensagem privada: O cliente pode enviar mensagens para um destinatário específico.

## Tratamento de Erros ⚠️
- O servidor valida se o ID do cliente é único. Caso um cliente tente conectar com um ID já em uso, uma mensagem de erro é enviada.
- Quando um cliente tenta enviar uma mensagem para um ID inexistente, o servidor retorna uma mensagem de erro.
- Encerramento de Conexão: 
O cliente pode se desconectar a qualquer momento clicando no botão Desconectar.
O servidor envia uma mensagem de encerramento para todos os clientes ao ser desligado.

## Autores do Projeto 🧑‍💻
- [Filipe de Andrade Machado](https://github.com/filipeAndr)
- [Gabriel Spressola Ziviani](https://github.com/Slayer-Nefarox)
- [José Pedro Cândido Lopes Peres](https://github.com/PeterYouseph/)
- [Pedro Arfux Pereira Cavalcante de Castro](https://github.com/SafeMantella)