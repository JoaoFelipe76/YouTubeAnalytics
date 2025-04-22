# Instruções de Deploy

Este guia descreve os passos para fazer o deploy da aplicação de análise do YouTube tanto para produção quanto para integração com o Slack.

## Deploy no Heroku

### Pré-requisitos
- Conta no [Heroku](https://www.heroku.com/)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) instalado
- Git instalado

### Passos para Deploy

1. **Login no Heroku**
   ```
   heroku login
   ```

2. **Criar uma nova aplicação no Heroku**
   ```
   heroku create lets-media-analytics
   ```

3. **Adicionar o remote do Heroku ao seu repositório**
   ```
   heroku git:remote -a lets-media-analytics
   ```

4. **Configurar variáveis de ambiente**
   ```
   heroku config:set YOUTUBE_API_KEY=AIzaSyCswbMKKorlHVSA_9kWSS9ZIKogaurZdNA
   ```

5. **Fazer o deploy da aplicação**
   ```
   git push heroku main
   ```

6. **Abrir a aplicação**
   ```
   heroku open
   ```

## Deploy usando o Render (alternativa gratuita)

1. Crie uma conta no [Render](https://render.com/)
2. No dashboard, clique em "New Web Service"
3. Conecte ao seu repositório GitHub
4. Configure:
   - Nome: lets-media-analytics
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:server`
5. Adicione as variáveis de ambiente necessárias
6. Clique em "Create Web Service"

## Configuração do Slack

### Criar um App no Slack

1. Acesse [api.slack.com/apps](https://api.slack.com/apps)
2. Clique em "Create New App" → "From scratch"
3. Dê um nome como "YouTube Analytics" e selecione seu workspace
4. Na seção "OAuth & Permissions", adicione os seguintes escopos:
   - `chat:write`
   - `files:write`
5. Instale o app no seu workspace
6. Copie o "Bot User OAuth Token" que começa com `xoxb-`

### Configuração das Variáveis de Ambiente

No servidor onde a aplicação está hospedada:

```
export SLACK_API_TOKEN=xoxb-seu-token-aqui
export SLACK_CHANNEL=#seu-canal
```

Para o Heroku:
```
heroku config:set SLACK_API_TOKEN=xoxb-seu-token-aqui
heroku config:set SLACK_CHANNEL=#seu-canal
```

## Configuração do Agendador de Relatórios

Você pode usar o `cron_scheduler.py` para enviar relatórios automaticamente.

### No seu próprio servidor:
```
nohup python cron_scheduler.py &
```

### No Heroku:
1. Instale o add-on Heroku Scheduler:
   ```
   heroku addons:create scheduler:standard
   ```

2. Abra o dashboard do scheduler:
   ```
   heroku addons:open scheduler
   ```

3. Adicione um novo job para executar:
   ```
   python slack_reporter.py
   ```
   Defina a frequência desejada (diária, por exemplo).

## Testando o Envio para o Slack

Para verificar se o envio para o Slack está funcionando:

```
python slack_reporter.py
```

## Troubleshooting

### Problemas comuns:

1. **Erro de Token do Slack**
   - Verifique se o token está correto e tem os escopos necessários

2. **Erros no Heroku**
   - Verifique os logs com `heroku logs --tail`

3. **Problemas com a API do YouTube**
   - Verifique se a chave da API está correta e tem as permissões necessárias
   - Verifique os limites de quota

4. **Problemas com Plotly/Kaleido**
   - Se houver problemas ao gerar imagens, certifique-se de que o kaleido está instalado corretamente

Para suporte adicional, consulte a documentação ou abra uma issue no repositório. 