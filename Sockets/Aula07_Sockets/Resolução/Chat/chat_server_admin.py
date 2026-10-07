import socket
import sys
import threading

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

# Estrutura: {socket: {"nick": str, "ip": str, "port": int}}
clientes = {}
lock = threading.Lock()
servidor_no_chat = True
executando = True

def broadcast(mensagem, remetente_sock=None):
    """Envia uma mensagem para todos os clientes conectados (exceto o remetente, se especificado)."""
    with lock:
        conexoes_ativas = list(clientes.items())
        
    for sock, info in conexoes_ativas:
        if sock != remetente_sock:
            try:
                sock.sendall(f"\n{mensagem}\n[Você]: ".encode('utf-8'))
            except:
                remover_cliente(sock)

def remover_cliente(sock):
    """Remove um socket da lista com segurança."""
    with lock:
        if sock in clientes:
            info = clientes.pop(sock)
            try:
                sock.close()
            except:
                pass
            return info
    return None

def gerenciar_cliente(client_sock, client_addr):
    """Thread dedicada para escutar cada cliente."""
    try:
        # Primeiro dado esperado: Nickname
        nick = client_sock.recv(1024).decode('utf-8').strip()
        if not nick:
            client_sock.close()
            return

        with lock:
            clientes[client_sock] = {"nick": nick, "ip": client_addr[0], "port": client_addr[1]}

        msg_entrada = f"[+] {nick} ({client_addr[0]}:{client_addr[1]}) entrou no chat."
        print(f"\n[Servidor]: {msg_entrada}")
        broadcast(msg_entrada, remetente_sock=client_sock)

        prompt_srv = "[Servidor]: " if servidor_no_chat else "[Painel-Srv]: "
        print(prompt_srv, end="", flush=True)

        while executando:
            data = client_sock.recv(1024)
            if not data:
                break

            msg = data.decode('utf-8').strip()
            if msg.lower() == 'sair':
                break

            msg_formatada = f"[{nick} - {client_addr[0]}]: {msg}"
            print(f"\n[Servidor]: {msg_formatada}")
            broadcast(msg_formatada, remetente_sock=client_sock)
            print(prompt_srv, end="", flush=True)

    except:
        pass
    finally:
        info = remover_cliente(client_sock)
        if info:
            msg_saida = f"[-] {info['nick']} ({info['ip']}:{info['port']}) saiu do chat."
            print(f"\n[Servidor]: {msg_saida}")
            broadcast(msg_saida)
            prompt_srv = "[Servidor]: " if servidor_no_chat else "[Painel-Srv]: "
            print(prompt_srv, end="", flush=True)

def painel_servidor(server_sock):
    """Thread que lê comandos e mensagens do administrador no terminal do servidor."""
    global servidor_no_chat, executando

    menu_ajuda = """
======================================================
              COMANDOS DISPONÍVEIS NO SERVIDOR
======================================================
  ajuda     - Mostra esta lista de comandos
  sair      - Sai do chat (modo gerenciamento oculto)
  entrar    - Volta a participar ativamente do chat
  usuarios  - Lista todos os clientes conectados
  kick <nick> - Desconecta um usuário pelo nickname
  encerrar  - Derruba todos os clientes e fecha o servidor
======================================================
"""
    while executando:
        prompt = "[Servidor]: " if servidor_no_chat else "[Painel-Srv]: "
        try:
            cmd = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            cmd = "encerrar"

        if not cmd:
            continue

        if cmd.lower() == 'ajuda':
            print(menu_ajuda)

        elif cmd.lower() == 'sair':
            if servidor_no_chat:
                servidor_no_chat = False
                print("[*] Você saiu do chat. Modo gerenciamento ativado.")
                broadcast("[SISTEMA]: O Administrador do Servidor saiu do chat.")
            else:
                print("[!] Você já está fora do chat.")

        elif cmd.lower() == 'entrar':
            if not servidor_no_chat:
                servidor_no_chat = True
                print("[*] Você voltou para o chat!")
                broadcast("[SISTEMA]: O Administrador do Servidor entrou no chat.")
            else:
                print("[!] Você já está no chat.")

        elif cmd.lower() == 'usuarios':
            with lock:
                print(f"\n--- {len(clientes)} Usuário(s) Conectado(s) ---")
                for s, info in clientes.items():
                    print(f" - {info['nick']} ({info['ip']}:{info['port']})")
                print("-" * 35)

        elif cmd.lower().startswith('kick '):
            alvo_nick = cmd[5:].strip()
            alvo_sock = None
            with lock:
                for s, info in clientes.items():
                    if info['nick'].lower() == alvo_nick.lower():
                        alvo_sock = s
                        break
            if alvo_sock:
                print(f"[*] Expulsando o usuário {alvo_nick}...")
                try:
                    alvo_sock.sendall("\n[SISTEMA]: Você foi expulso do servidor pelo Administrador.\n".encode('utf-8'))
                except:
                    pass
                remover_cliente(alvo_sock)
                broadcast(f"[*] {alvo_nick} foi expulso do chat pelo Administrador.")
            else:
                print(f"[!] Usuário '{alvo_nick}' não encontrado.")

        elif cmd.lower() == 'encerrar':
            print("[*] Avisando clientes e derrubando conexões...")
            executando = False
            broadcast("[SISTEMA]: O Servidor está sendo encerrado imediatamente!")
            with lock:
                for s in list(clientes.keys()):
                    try:
                        s.close()
                    except:
                        pass
                clientes.clear()
            server_sock.close()
            print("[*] Servidor desligado com sucesso.")
            break

        else:
            # Mensagem normal do servidor enviada para a sala
            if servidor_no_chat:
                broadcast(f"[Servidor]: {cmd}")
            else:
                print("[!] Você está no modo oculto. Digite 'entrar' para poder conversar ou 'ajuda' para comandos.")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"[*] Sala de Chat Multiusuário aguardando conexões em {HOST}:{PORT}...\n")

    # Dispara a thread para comandos locais do servidor
    threading.Thread(target=painel_servidor, args=(server,), daemon=True).start()

    try:
        while executando:
            client_sock, client_addr = server.accept()
            threading.Thread(target=gerenciar_cliente, args=(client_sock, client_addr), daemon=True).start()
    except OSError:
        pass
    finally:
        server.close()

if __name__ == '__main__':
    main()