import socket
import sys

HOST = '127.0.0.1'
PORT = 5000

if len(sys.argv) > 1:
    HOST = sys.argv[1]

if len(sys.argv) > 2:
    try:
        PORT = int(sys.argv[2])

    except ValueError:
        print("Erro: A porta deve ser um número inteiro.")
        sys.exit(1)


client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

try:
    print(f"[*] Conectando em {HOST}:{PORT}...")

    client.connect((HOST, PORT))

    print("[+] Conectado à calculadora!")
    print("Digite uma expressão matemática.")
    print("Exemplos:")
    print("40+2")
    print("84/2")
    print("10*5")
    print("Digite 'sair' para encerrar.")
    print("-" * 40)

    while True:
        expressao = input("Cálculo > ").strip()

        if not expressao:
            continue

        client.sendall(
            expressao.encode("utf-8")
        )

        if expressao.lower() == "sair":
            break

        resposta = client.recv(1024)

        if not resposta:
            print("Servidor desconectado.")
            break

        print(
            resposta.decode("utf-8").strip()
        )

except ConnectionRefusedError:
    print("Erro: Servidor não está rodando.")

except KeyboardInterrupt:
    print("\nPrograma encerrado.")

finally:
    client.close()

    print("[*] Cliente finalizado.")