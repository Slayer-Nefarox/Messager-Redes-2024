# Sistema de troca de mensagens utilizando UDP com dois programas distintos: um para o servidor e outro para o cliente. 

Implementação do Server

O servidor será responsável por:

    Receber as mensagens de OI, TCHAU e MSG dos clientes.
    Manter uma lista de clientes ativos.
    Enviar mensagens periódicas informando o estado do servidor.
    Controlar a comunicação e garantir que cada cliente utilize um identificador único.

Implementar o servidor com threads para tratar múltiplos clientes de forma simultânea. 
A biblioteca socket do Python será utilizada para comunicação UDP.

Executar server com 'python server.py'

Implementação do Cliente

O cliente será responsável por:

    Enviar uma mensagem OI para se registrar no servidor.
    Enviar mensagens MSG para outros clientes ou para o servidor.
    Receber e exibir mensagens.

Executar client.py com  'client.py <ID> <Nome> <IP> <PORT>'
(exemplo: 'client.py 1 Alice 127.0.0.1 12345')
