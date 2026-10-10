import socket
import struct
import sys

# Configuração dos valores padrões
IP_SERVIDOR = '127.0.0.1'
PORTA = 9000

# Tratamento dos argumentos da linha de comando
if len(sys.argv) > 1:
    IP_SERVIDOR = sys.argv[1]  # Se fornecido, substitui o IP padrão

num1 = int(input("Digite o primeiro número: "))
num2 = int(input("Digite o segundo número: "))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect((IP_SERVIDOR, PORTA))

    cliente.sendall(num1.to_bytes(4, byteorder="big", signed=True))
    cliente.sendall(num2.to_bytes(4, byteorder="big", signed=True))

    dados = cliente.recv(4)
    resultado = int.from_bytes(dados, byteorder="big", signed=True)

print("Resultado:", resultado)
