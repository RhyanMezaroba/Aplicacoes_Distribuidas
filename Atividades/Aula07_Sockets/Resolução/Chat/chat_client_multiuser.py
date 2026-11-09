import socket
import sys
import threading

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

def receber(sock):
    while True:
        try:
            dados = sock.recv(1024)
            if not dados:
                print("\n[*] O servidor encerrou o chat ou você foi desconectado.")
                break
            print(dados.decode('utf-8'), end="", flush=True)
        except:
            break
    print("\n[*] Programa finalizado.")
    sock.close()

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nick = input("Escolha seu nome de usuário (Nickname): ").strip()
    while not nick:
        nick = input("Nickname inválido. Digite um nome: ").strip()

    try:
        print(f"[*] Conectando ao chat em {HOST}:{PORT}...")
        client.connect((HOST, PORT))
        print("[+] Conectado à sala de chat!")
        print("Digite 'sair' para encerrar.\n" + "-" * 50)

        # Envia o nickname como identificador inicial
        client.sendall((nick + "\n").encode('utf-8'))

        # Thread de recepção contínua em segundo plano
        threading.Thread(target=receber, args=(client,), daemon=True).start()

        while True:
            msg = input("[Você]: ").strip()
            if not msg:
                continue
            client.sendall((msg + "\n").encode('utf-8'))
            if msg.lower() == 'sair':
                break

    except ConnectionRefusedError:
        print(f"[-] Erro: Servidor não encontrado em {HOST}:{PORT}.")
    except KeyboardInterrupt:
        print("\n[*] Desconectado via teclado.")
    finally:
        client.close()

if __name__ == '__main__':
    main()