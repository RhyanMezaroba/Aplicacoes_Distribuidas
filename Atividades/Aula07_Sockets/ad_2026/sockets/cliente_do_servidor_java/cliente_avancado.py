import json
import socket
import sys

IP_SERVIDOR = "127.0.0.1"
PORTA = 9000
TIMEOUT = 5

# Tratamento dos argumentos da linha de comando
if len(sys.argv) > 1:
    IP_SERVIDOR = sys.argv[1]  # Se fornecido, substitui o IP padrão

num1 = int(input("Primeiro número: "))
num2 = int(input("Segundo número: "))
operacao = input("Operação [SOMAR, SUBTRAIR, MULTIPLICAR, DIVIDIR]: ").upper()

requisicao = {
    "operacao": operacao,
    "num1": num1,
    "num2": num2
}

try:
    with socket.create_connection((IP_SERVIDOR, PORTA), timeout=TIMEOUT) as cliente:
        cliente.settimeout(TIMEOUT)

        with cliente.makefile("r", encoding="utf-8") as entrada, \
             cliente.makefile("w", encoding="utf-8") as saida:

            requisicao_json = json.dumps(requisicao, ensure_ascii=False)

            saida.write(requisicao_json + "\n")
            saida.flush()

            resposta_json = entrada.readline()

            if not resposta_json:
                raise ConnectionError("Servidor encerrou a conexão sem responder.")

            resposta = json.loads(resposta_json)

            if resposta["status"] == "SUCESSO":
                print("Resultado:", resposta["resultado"])
            else:
                print("Erro do servidor:", resposta["mensagem"])
except socket.timeout:
    print("Erro: timeout na comunicação com o servidor.")
except ConnectionRefusedError:
    print("Erro: conexão recusada. O servidor está rodando?")
except ConnectionError as e:
    print("Erro:", e)
except OSError as e:
    print("Erro de comunicação:", e)
except json.JSONDecodeError:
    print("Erro: resposta JSON inválida.")