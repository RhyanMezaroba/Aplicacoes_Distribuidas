# servidor_calculadora_json.py
import json
import socket
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"
PORTA = 9000
TIMEOUT = 5
pool = ThreadPoolExecutor(max_workers=10)

def processar_operacao(requisicao):
    """Valida parâmetros e executa a operação aritmética solicitada."""
    try:
        operacao = requisicao["operacao"].upper()
        num1 = int(requisicao["num1"])
        num2 = int(requisicao["num2"])

        if operacao == "SOMAR":
            resultado = num1 + num2
        elif operacao == "SUBTRAIR":
            resultado = num1 - num2
        elif operacao == "MULTIPLICAR":
            resultado = num1 * num2
        elif operacao == "DIVIDIR":
            if num2 == 0:
                return {"status": "ERRO", "resultado": 0, "mensagem": "Divisão por zero."}
            resultado = num1 // num2
        else:
            return {"status": "ERRO", "resultado": 0, "mensagem": "Operação inválida."}

        return {"status": "SUCESSO", "resultado": resultado, "mensagem": "OK"}
    except (KeyError, ValueError, TypeError) as e:
        return {"status": "ERRO", "resultado": 0, "mensagem": f"Falha de formato: {e}"}

def processar_cliente(conexao, endereco):
    """Processa a transação JSON de um cliente conectado."""
    try:
        conexao.settimeout(TIMEOUT)
        with conexao.makefile("r", encoding="utf-8") as entrada, \
             conexao.makefile("w", encoding="utf-8") as saida:

            linha = entrada.readline()
            if not linha:
                return

            print(f"[Recebido de {endereco}]: {linha.strip()}")
            requisicao = json.loads(linha)
            resposta = processar_operacao(requisicao)
            resposta_json = json.dumps(resposta, ensure_ascii=False)
            saida.write(resposta_json + "\n")
            saida.flush()
            print(f"[Enviado para {endereco}]: {resposta_json}")

    except socket.timeout:
        print(f"[-] Timeout aguardando dados de {endereco}")
    except json.JSONDecodeError:
        resposta_erro = {"status": "ERRO", "resultado": 0, "mensagem": "JSON inválido."}
        try:
            conexao.sendall((json.dumps(resposta_erro) + "\n").encode("utf-8"))
        except OSError:
            pass
    except OSError as e:
        print(f"[-] Erro na comunicação com {endereco}: {e}")
    finally:
        conexao.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORTA))
    servidor.listen()
    print(f"[*] Servidor JSON Multithread ativo na porta {PORTA}...")

    try:
        while True:
            conexao, endereco = servidor.accept()
            print(f"[+] Cliente conectado: {endereco}")
            pool.submit(processar_cliente, conexao, endereco)
    except KeyboardInterrupt:
        print("\n[*] Encerrando servidor...")
    finally:
        pool.shutdown()
