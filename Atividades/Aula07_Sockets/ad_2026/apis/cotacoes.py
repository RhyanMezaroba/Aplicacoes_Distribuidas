import yfinance as yf
import matplotlib.pyplot as plt

# No yfinance, o formato padrão de data é AAAA-MM-DD
cotacao_bovespa = yf.download('^BVSP',
                              start='2025-01-01',
                              end='2026-01-01')

# Exibe as primeiras linhas para verificar se funcionou
print(cotacao_bovespa.head())

# Exemplo de como plotar o gráfico do fechamento
cotacao_bovespa['Close'].plot(figsize=(10, 5))
plt.title('IBOVESPA 2025-2026')
plt.show()
