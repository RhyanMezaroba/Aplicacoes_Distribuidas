import requests

# Recupera os dados da consulta à API em formato JSON
cotacoes = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL').json()
print(cotacoes)

cotacao_dolar = cotacoes['USDBRL']
print(cotacao_dolar['bid'])