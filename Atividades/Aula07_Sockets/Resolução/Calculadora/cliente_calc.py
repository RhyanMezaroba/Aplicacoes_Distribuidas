import sys
import socket

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
    print(f"[+] Conectado à Calculadora em {HOST}:{PORT}")
    print("Digite expressões aritméticas (ex: 40+2, 84/2) ou 'sair':")
    print("-" * 50)

    while True:
        expressao = input("Expressão > ").strip()
        if not expressao:
            continue

        client.sendall((expressao + "\n").encode('utf-8'))

        if expressao.lower() == 'sair':
            break

        resposta = client.recv(1024).decode('utf-8').strip()
        print(f"Resultado < {resposta}\n")

except ConnectionRefusedError:
    print(f"[-] Erro: Servidor inacessível em {HOST}:{PORT}.")
except KeyboardInterrupt:
    print("\n[*] Desconectado pelo usuário.")
finally:
    client.close()