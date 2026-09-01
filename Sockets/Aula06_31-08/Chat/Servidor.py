import socket
import threading
import sys


HOST = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000


clientes = {}
lock = threading.Lock()

servidor_ativo_no_chat = True


def broadcast(mensagem, excluir=None):

    with lock:
        clientes_lista = list(clientes.items())

    for socket_cliente, dados_cliente in clientes_lista:

        if socket_cliente != excluir:

            try:
                socket_cliente.sendall(
                    mensagem.encode("utf-8")
                )

            except:

                remover_cliente(socket_cliente)


def remover_cliente(client_socket):

    with lock:

        if client_socket in clientes:

            nickname = clientes[client_socket]["nickname"]
            endereco = clientes[client_socket]["endereco"]

            del clientes[client_socket]

            print(
                f"\n[-] {nickname} ({endereco[0]}) desconectou."
            )

            broadcast(
                f"\n[*] {nickname} saiu do chat.\n"
            )

    try:
        client_socket.close()

    except:
        pass


def listar_usuarios():

    with lock:

        if not clientes:
            return "Nenhum usuário conectado."

        lista = "\n===== USUÁRIOS CONECTADOS =====\n"

        for dados in clientes.values():

            nickname = dados["nickname"]
            endereco = dados["endereco"]

            lista += (
                f"- {nickname} "
                f"({endereco[0]})\n"
            )

        lista += "===============================\n"

        return lista


def kick_usuario(nickname):

    with lock:

        for socket_cliente, dados in list(clientes.items()):

            if dados["nickname"].lower() == nickname.lower():

                try:

                    socket_cliente.sendall(
                        "\n[*] Você foi expulso pelo servidor.\n"
                        .encode("utf-8")
                    )

                except:
                    pass

                del clientes[socket_cliente]

                try:
                    socket_cliente.close()

                except:
                    pass

                broadcast(
                    f"\n[*] {nickname} foi removido do chat.\n"
                )

                return True

    return False


def gerenciar_cliente(client_socket, endereco):

    try:

        client_socket.sendall(
            "Digite seu nickname: ".encode("utf-8")
        )

        nickname = client_socket.recv(1024).decode(
            "utf-8"
        ).strip()

        if not nickname:
            nickname = f"Usuario_{endereco[1]}"

        with lock:

            clientes[client_socket] = {
                "nickname": nickname,
                "endereco": endereco
            }

        print(
            f"\n[+] {nickname} entrou no chat "
            f"({endereco[0]}:{endereco[1]})"
        )

        broadcast(
            f"\n[*] {nickname} entrou no chat.\n",
            excluir=client_socket
        )

        client_socket.sendall(
            "\n===== BEM-VINDO AO CHAT =====\n"
            "Digite 'ajuda' para ver os comandos.\n"
            .encode("utf-8")
        )

        while True:

            dados = client_socket.recv(1024)

            if not dados:
                break

            mensagem = dados.decode(
                "utf-8"
            ).strip()

            if not mensagem:
                continue

            comando = mensagem.lower()

            if comando == "sair":

                client_socket.sendall(
                    "Você saiu do chat.\n".encode(
                        "utf-8"
                    )
                )

                break


            elif comando == "ajuda":

                ajuda = """
===== COMANDOS DISPONÍVEIS =====

ajuda
    Mostra esta tela de ajuda.

usuarios
    Mostra os usuários conectados.

sair
    Sai do chat.

================================
"""

                client_socket.sendall(
                    ajuda.encode("utf-8")
                )


            elif comando == "usuarios":

                lista = listar_usuarios()

                client_socket.sendall(
                    lista.encode("utf-8")
                )


            else:

                mensagem_formatada = (
                    f"\n[{nickname} - {endereco[0]}]: "
                    f"{mensagem}\n"
                )

                print(
                    mensagem_formatada.strip()
                )

                broadcast(
                    mensagem_formatada,
                    excluir=client_socket
                )


    except ConnectionResetError:

        pass

    except Exception as e:

        print(
            f"\n[-] Erro com cliente "
            f"{endereco}: {e}"
        )

    finally:

        remover_cliente(client_socket)


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))

server.listen(10)


print("=" * 50)
print(" SERVIDOR DE CHAT MULTIUSUÁRIO")
print("=" * 50)

print(
    f"[*] Servidor rodando em {HOST}:{PORT}"
)

print("[*] Aguardando clientes...")
print()
print("Comandos do servidor:")
print("entrar")
print("sair")
print("usuarios")
print("kick <nickname>")
print("encerrar")
print()


def aceitar_clientes():

    while True:

        try:

            client_socket, endereco = server.accept()

            print(
                f"\n[+] Nova conexão: "
                f"{endereco[0]}:{endereco[1]}"
            )

            thread = threading.Thread(
                target=gerenciar_cliente,
                args=(client_socket, endereco),
                daemon=True
            )

            thread.start()

        except OSError:
            break


thread_aceitar = threading.Thread(
    target=aceitar_clientes,
    daemon=True
)

thread_aceitar.start()


try:

    while True:

        comando = input("[Servidor]: ").strip()

        if not comando:
            continue


        if comando.lower() == "entrar":

            servidor_ativo_no_chat = True

            print(
                "[*] Servidor entrou no chat."
            )

            broadcast(
                "\n[*] O servidor entrou no chat.\n"
            )


        elif comando.lower() == "sair":

            servidor_ativo_no_chat = False

            print(
                "[*] Servidor saiu do chat."
            )

            broadcast(
                "\n[*] O servidor saiu do chat, "
                "mas continua encaminhando mensagens.\n"
            )


        elif comando.lower() == "usuarios":

            print(
                listar_usuarios()
            )


        elif comando.lower().startswith("kick "):

            partes = comando.split(
                " ",
                1
            )

            if len(partes) < 2:

                print(
                    "Uso: kick <nickname>"
                )

            else:

                nickname = partes[1].strip()

                sucesso = kick_usuario(
                    nickname
                )

                if sucesso:

                    print(
                        f"[*] {nickname} foi expulso."
                    )

                else:

                    print(
                        "[!] Usuário não encontrado."
                    )


        elif comando.lower() == "encerrar":

            print(
                "[*] Encerrando servidor..."
            )

            broadcast(
                "\n[*] O servidor foi encerrado.\n"
            )

            with lock:

                lista_clientes = list(
                    clientes.keys()
                )

            for client_socket in lista_clientes:

                try:

                    client_socket.sendall(
                        "\n[*] Servidor encerrado.\n"
                        .encode("utf-8")
                    )

                    client_socket.close()

                except:
                    pass

            break


        else:

            if servidor_ativo_no_chat:

                mensagem = (
                    f"\n[Servidor]: {comando}\n"
                )

                print(
                    mensagem.strip()
                )

                broadcast(mensagem)

            else:

                print(
                    "[!] Servidor está fora do chat. "
                    "Digite 'entrar' para voltar."
                )


except KeyboardInterrupt:

    print(
        "\n[*] Encerrando servidor..."
    )


finally:

    with lock:

        lista_clientes = list(
            clientes.keys()
        )

    for client_socket in lista_clientes:

        try:
            client_socket.close()
        except:
            pass

    server.close()

    print(
        "[*] Servidor finalizado."
    )