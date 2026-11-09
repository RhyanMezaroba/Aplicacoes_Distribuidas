import socket

HOST = "127.0.0.1"
PORTA = 9000

def receber_int(conexao):
    dados = b""
    while len(dados) < 4:
        parte = conexao.recv(4 - len(dados))
        if not parte:
            raise ConnectionError("Conexão encerrada antes do recebimento completo.")
        dados += parte
    return int.from_bytes(dados, byteorder="big", signed=True)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
    # Permite reutilizar a porta imediatamente se reiniciar o processo
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORTA))
    servidor.listen()
    print(f"Servidor Python rodando na porta {PORTA}...")

    while True:
        print("Aguardando conexão...")
        conexao, endereco = servidor.accept()
        with conexao:
            print(f"Cliente conectado: {endereco}")
            num1 = receber_int(conexao)
            num2 = receber_int(conexao)
            resultado = num1 + num2
            print(f"Recebido: {num1} + {num2}")
            print(f"Resultado enviado: {resultado}")
            conexao.sendall(resultado.to_bytes(4, byteorder="big", signed=True))