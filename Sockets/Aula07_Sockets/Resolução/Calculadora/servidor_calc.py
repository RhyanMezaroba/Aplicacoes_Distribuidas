import sys
import socket

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print(f"[*] Servidor Calculadora ativo em {HOST}:{PORT}... (Ctrl+C para sair)")

try:
    conexao, cliente_ip = server.accept()
    print(f"[+] Conectado por: {cliente_ip}")

    while True:
        dados = conexao.recv(1024)
        if not dados:
            print("[*] Conexão encerrada pelo cliente.")
            break

        expressao = dados.decode('utf-8').strip()

        if expressao.lower() == 'sair':
            conexao.sendall("Conexão encerrada.\n".encode('utf-8'))
            break

        print(f"[Recebido]: {expressao}")

        # Avaliação da expressão com tratamento de erros
        try:
            # Avalia a expressão aritmética
            resultado = eval(expressao)
            resposta = f"{resultado}\n"
        except ZeroDivisionError:
            resposta = "ERRO: Divisão por zero\n"
        except Exception as e:
            resposta = f"ERRO: Expressão inválida ({e})\n"

        print(f"[Resultado enviado]: {resposta.strip()}")
        conexao.sendall(resposta.encode('utf-8'))

    conexao.close()
except KeyboardInterrupt:
    print("\n[*] Servidor finalizado via teclado.")
finally:
    server.close()