import socket
import struct
import sys

# Configuração dos valores padrões
IP_SERVIDOR = '127.0.0.1'
PORTA = 9000

# Tratamento dos argumentos da linha de comando
if len(sys.argv) > 1:
    IP_SERVIDOR = sys.argv[1]  # Se fornecido, substitui o IP padrão

if len(sys.argv) > 2:
    try:
        PORTA = int(sys.argv[2])  # Se fornecido, substitui a porta padrão
    except ValueError:
        print("Erro: A porta deve ser um número inteiro.")
        print("Uso correto: python3 cliente_simples-v2.py <IP_DO_SERVIDOR> <PORTA>")
        print("Exemplo:     python3 cliente_simples-v2.py 192.168.1.50 9000")
        sys.exit(1)

def receber_int(socket_cliente):
    dados = b""

    while len(dados) < 4:
        parte = socket_cliente.recv(4 - len(dados))

        if not parte:
            raise ConnectionError("Conexão encerrada antes do recebimento completo.")

        dados += parte

    return struct.unpack(">i", dados)[0]

num1 = int(input("Digite o primeiro número: "))
num2 = int(input("Digite o segundo número: "))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect((IP_SERVIDOR, PORTA))

    cliente.sendall(struct.pack(">i", num1))
    cliente.sendall(struct.pack(">i", num2))

    resultado = receber_int(cliente)

print("Resultado:", resultado)