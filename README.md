# Análise de Canal do YouTube - Let's Media Oficia

Esta aplicação fornece uma análise detalhada do desempenho do canal do YouTube "Let's Media Oficia" usando a API do YouTube e ferramentas modernas de análise de dados em Python.

## Versões da Aplicação

Esta aplicação possui duas versões:

1. **Versão Dash**: Interface usando Dash/Plotly para execução local ou deploy no Heroku.
2. **Versão Streamlit**: Interface usando Streamlit para facilitar o deploy no Streamlit Cloud (recomendado).

## Funcionalidades

- **Análise de Crescimento**: Acompanhe o crescimento de inscritos e visualizações ao longo do tempo.
- **Métricas de Engajamento**: Visualize taxas de engajamento, likes e comentários.
- **Vídeos Populares**: Identifique os vídeos com melhor desempenho e maior engajamento.
- **Previsões de Crescimento**: Obtenha previsões sobre o crescimento futuro do canal usando modelos de aprendizado de máquina.
- **Análise Comparativa**: Compare o desempenho com canais semelhantes.
- **Relatórios no Slack**: Receba relatórios diários com os gráficos atualizados no Slack.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **YouTube Data API v3**: Para coleta de dados do canal
- **Pandas/NumPy**: Para manipulação e análise de dados
- **Streamlit/Dash/Plotly**: Para visualização interativa de dados e criação do dashboard
- **Statsmodels/Scikit-learn**: Para análise preditiva e modelos de série temporal
- **Slack SDK**: Para envio de relatórios automáticos

## Arquivos Principais

- `youtube_analytics.py`: Contém a classe principal para interação com a API do YouTube
- `streamlit_app.py`: Aplicação Streamlit (recomendado para deploy)
- `analytics_dashboard.py`: Aplicação Dash alternativa 
- `streamlit_slack_reporter.py`: Script para envio de relatórios para o Slack
- `requirements.txt`: Lista de dependências do projeto

## Deploy no Streamlit Cloud

1. Faça um fork deste repositório para sua conta GitHub
2. Acesse [streamlit.io/cloud](https://streamlit.io/cloud)
3. Faça login com sua conta GitHub
4. Clique em "New app"
5. Selecione o repositório fork e o arquivo `streamlit_app.py`
6. Clique em "Deploy!"

Para informações detalhadas, consulte `streamlit_deploy_instructions.md`.

## Configuração do Slack

Para configurar os relatórios diários no Slack:

1. Crie um app no Slack em [api.slack.com/apps](https://api.slack.com/apps)
2. Configure as permissões necessárias (`chat:write` e `files:write`)
3. Obtenha o Bot User OAuth Token
4. Configure o token como segredo no GitHub (`SLACK_API_TOKEN`)

O repositório já inclui uma configuração do GitHub Actions para enviar relatórios diários.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes. 