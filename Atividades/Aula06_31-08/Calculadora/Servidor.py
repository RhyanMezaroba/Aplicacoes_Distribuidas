import socket
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen(1)

print(f"[*] Servidor da calculadora rodando em {HOST}:{PORT}")
print("[*] Aguardando conexão...")

try:
    conexao, endereco = server.accept()

    print(f"[+] Cliente conectado: {endereco}")

    while True:
        dados = conexao.recv(1024)

        if not dados:
            print("[*] Cliente desconectado.")
            break

        expressao = dados.decode("utf-8").strip()

        print(f"[Cliente]: {expressao}")

        if expressao.lower() == "sair":
            conexao.sendall(
                "Conexão encerrada pelo servidor.\n".encode("utf-8")
            )
            break

        try:
            resultado = eval(expressao)

            resposta = f"Resultado: {resultado}\n"

        except Exception as e:
            resposta = f"Erro na expressão: {e}\n"

        conexao.sendall(
            resposta.encode("utf-8")
        )

finally:
    conexao.close()
    server.close()

    print("[*] Servidor encerrado.")