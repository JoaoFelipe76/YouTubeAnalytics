# Análise de Canal do YouTube - Let's Media Oficial

Esta aplicação fornece uma análise detalhada do desempenho do canal do YouTube "Let's Media Oficial" usando a API do YouTube e ferramentas modernas de análise de dados em Python.

## Funcionalidades

- **Análise de Crescimento**: Acompanhe o crescimento de inscritos e visualizações ao longo do tempo.
- **Métricas de Engajamento**: Visualize taxas de engajamento, likes e comentários.
- **Vídeos Populares**: Identifique os vídeos com melhor desempenho e maior engajamento.
- **Previsões de Crescimento**: Obtenha previsões sobre o crescimento futuro do canal usando modelos de aprendizado de máquina.
- **Análise Comparativa**: Compare o desempenho com canais semelhantes.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **YouTube Data API v3**: Para coleta de dados do canal
- **Pandas/NumPy**: Para manipulação e análise de dados
- **Dash/Plotly**: Para visualização interativa de dados e criação do dashboard
- **Statsmodels/Scikit-learn**: Para análise preditiva e modelos de série temporal

## Requisitos

- Python 3.8+
- Pacotes Python listados em `requirements.txt`
- Chave da API do YouTube

## Instalação

1. Clone este repositório:
```
git clone [URL_DO_REPOSITÓRIO]
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

## Uso

Para executar a aplicação:

```
python main.py
```

Após iniciar, acesse o dashboard em seu navegador em: `http://127.0.0.1:8050/`

## Configuração

A aplicação está configurada para analisar o canal "Let's Media Oficial", mas você pode modificar as variáveis `API_KEY` e `CHANNEL_URL` no arquivo `analytics_dashboard.py` para analisar outros canais.

## Estrutura do Projeto

- `youtube_analytics.py`: Contém a classe principal para interação com a API do YouTube
- `analytics_dashboard.py`: Aplicação Dash que cria e exibe o dashboard interativo
- `requirements.txt`: Lista de dependências do projeto
- `main.py`: Arquivo principal para iniciar a aplicação

## Observações

- A API do YouTube tem limites de quota diária. Monitore seu uso para evitar exceder os limites.
- Algumas funcionalidades podem exigir permissões adicionais se você planeja analisar canais privados.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes. 