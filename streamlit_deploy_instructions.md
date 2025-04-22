# Instruções para Deploy com Streamlit

Este guia descreve os passos para fazer o deploy da aplicação de análise do YouTube usando Streamlit e configurar os relatórios para o Slack.

## Deploy no Streamlit Cloud

O Streamlit Cloud é uma plataforma gratuita para hospedagem de aplicações Streamlit, oferecida pela própria empresa por trás da biblioteca.

### Passos para o Deploy

1. **Crie uma conta no Streamlit Cloud**
   - Acesse [streamlit.io/cloud](https://streamlit.io/cloud)
   - Faça login com sua conta GitHub

2. **Prepare seu repositório no GitHub**
   - Faça o upload dos seus arquivos para um repositório GitHub
   - Certifique-se de que o repositório contenha:
     - `streamlit_app.py` (o aplicativo principal)
     - `youtube_analytics.py` (classe para análise do YouTube)
     - `requirements.txt` (com todas as dependências)

3. **Crie uma nova aplicação no Streamlit Cloud**
   - Clique em "New app"
   - Selecione seu repositório
   - Configure:
     - Main file path: `streamlit_app.py`
     - Defina as variáveis de ambiente necessárias:
       - `YOUTUBE_API_KEY` = `AIzaSyCswbMKKorlHVSA_9kWSS9ZIKogaurZdNA`

4. **Deploy**
   - Clique em "Deploy!"
   - O Streamlit Cloud automaticamente criará e implantará sua aplicação
   - Após alguns minutos, sua aplicação estará disponível no URL fornecido

## Configuração do Envio Diário para o Slack

### Usando GitHub Actions

Uma maneira simples de agendar o envio diário dos gráficos para o Slack é usando GitHub Actions:

1. **Crie um arquivo de workflow do GitHub Actions**
   - Crie uma pasta `.github/workflows` no seu repositório
   - Adicione um arquivo chamado `daily_slack_report.yml` com o conteúdo:

```yaml
name: Daily Slack Report

on:
  schedule:
    # Agendado para 10:00 UTC (ajuste conforme necessário)
    - cron: '0 10 * * *'
  workflow_dispatch:  # Permite execução manual

jobs:
  send-report:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Send report to Slack
        run: python streamlit_slack_reporter.py
        env:
          SLACK_API_TOKEN: ${{ secrets.SLACK_API_TOKEN }}
          SLACK_CHANNEL: '#youtube-analytics'
```

2. **Configure o token do Slack como um segredo no GitHub**
   - Vá para Settings > Secrets no seu repositório
   - Adicione um novo segredo:
     - Nome: `SLACK_API_TOKEN`
     - Valor: Seu token do Slack (começa com `xoxb-`)

### Usando um Serviço Externo (Alternativa)

Se preferir não usar GitHub Actions, você pode usar serviços como:

- **Heroku Scheduler**: Configure um job para executar `python streamlit_slack_reporter.py` diariamente
- **AWS Lambda + EventBridge**: Configure uma função Lambda para executar o script e agende com EventBridge
- **Google Cloud Functions + Cloud Scheduler**: Similar à opção da AWS

## Configuração do Slack

Para configurar a integração com o Slack, siga estas etapas:

1. **Crie um App no Slack**
   - Acesse [api.slack.com/apps](https://api.slack.com/apps)
   - Clique em "Create New App" → "From scratch"
   - Dê um nome e selecione seu workspace

2. **Configure as permissões do Bot**
   - Na seção "OAuth & Permissions", adicione os seguintes escopos:
     - `chat:write`
     - `files:write`

3. **Instale o app no seu workspace**
   - Ainda em "OAuth & Permissions", clique em "Install to Workspace"
   - Aceite as permissões solicitadas

4. **Obtenha o token do Bot**
   - Após a instalação, você verá o "Bot User OAuth Token"
   - Este é o token que você usará como `SLACK_API_TOKEN`

5. **Adicione o Bot ao canal onde deseja receber os relatórios**
   - No Slack, vá ao canal
   - Digite `/invite @seu-bot-name`

## Testando os Relatórios

Para enviar um relatório manualmente para testar:

```bash
# Configure o token do Slack
export SLACK_API_TOKEN=xoxb-seu-token-aqui
export SLACK_CHANNEL=#seu-canal

# Execute o script de relatório
python streamlit_slack_reporter.py
```

## Solução de Problemas

### Erros comuns:

1. **Erro de Token do Slack**
   - Verifique se o token está correto e tem os escopos necessários
   - Certifique-se de que o bot foi adicionado ao canal

2. **Erro ao enviar imagens**
   - Verifique se a dependência `kaleido` está instalada corretamente
   - Tente reinstalar com `pip install -U kaleido`

3. **Erro de API do YouTube**
   - Verifique se a chave API está correta e tem as permissões necessárias
   - Verifique os limites de quota da API

4. **Streamlit Cloud não inicia**
   - Verifique os logs de erro no painel do Streamlit Cloud
   - Certifique-se de que todas as dependências estão listadas no requirements.txt 