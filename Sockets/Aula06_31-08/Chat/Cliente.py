import socket
import threading
import sys


HOST = "127.0.0.1"
PORT = 5000


if len(sys.argv) > 1:
    HOST = sys.argv[1]


if len(sys.argv) > 2:

    try:
        PORT = int(sys.argv[2])

    except ValueError:

        print(
            "Erro: A porta deve ser um número."
        )

        sys.exit(1)


def receber_mensagens(client):

    while True:

        try:

            dados = client.recv(1024)

            if not dados:

                print(
                    "\n[*] Conexão com o servidor encerrada."
                )

                break

            mensagem = dados.decode(
                "utf-8"
            )

            print(
                mensagem,
                end="",
                flush=True
            )


        except:

            break


client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


try:

    print(
        f"[*] Conectando ao servidor "
        f"{HOST}:{PORT}..."
    )

    client.connect(
        (HOST, PORT)
    )


    mensagem = client.recv(1024).decode(
        "utf-8"
    )

    print(
        mensagem,
        end=""
    )


    nickname = input().strip()


    while not nickname:

        print(
            "Nickname não pode ser vazio."
        )

        nickname = input(
            "Digite seu nickname: "
        ).strip()


    client.sendall(
        nickname.encode("utf-8")
    )


    print(
        "\n[+] Conectado ao chat!"
    )

    print(
        "Digite 'ajuda' para ver os comandos."
    )

    print(
        "-" * 50
    )


    thread_receber = threading.Thread(
        target=receber_mensagens,
        args=(client,),
        daemon=True
    )

    thread_receber.start()


    while True:

        mensagem = input(
            "[Você]: "
        ).strip()


        if not mensagem:
            continue


        client.sendall(
            mensagem.encode("utf-8")
        )


        if mensagem.lower() == "sair":

            break


except ConnectionRefusedError:

    print(
        "[-] Erro: Não foi possível conectar ao servidor."
    )


except KeyboardInterrupt:

    print(
        "\n[*] Cliente encerrado."
    )


except Exception as e:

    print(
        f"[-] Erro: {e}"
    )


finally:

    try:
        client.close()
    except:
        pass

    print(
        "[*] Programa finalizado."
    )