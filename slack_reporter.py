"""
Script para enviar relatórios do YouTube Analytics para o Slack
"""
import os
import io
import json
import pandas as pd
import plotly.io as pio
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from PIL import Image

from youtube_analytics import YouTubeAnalytics
from analytics_dashboard import (
    update_views_by_video,
    update_growth_over_time,
    update_growth_prediction,
    update_top_videos_table,
    analyzer,
    channel_info,
    df_videos
)

# Configuração do Slack
# Você precisa definir esta variável de ambiente com seu token do Slack
# export SLACK_API_TOKEN=xoxb-your-token
SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN", "")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#youtube-analytics")

class SlackReporter:
    def __init__(self, token=SLACK_API_TOKEN, channel=SLACK_CHANNEL):
        self.token = token
        self.channel = channel
        self.client = WebClient(token=token)
        
    def send_message(self, text):
        """Envia uma mensagem de texto para o canal"""
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=text
            )
            return response
        except SlackApiError as e:
            print(f"Erro ao enviar mensagem para o Slack: {e}")
            return None
    
    def send_image(self, image_bytes, title, filename="graph.png"):
        """Envia uma imagem para o canal"""
        try:
            response = self.client.files_upload_v2(
                channel=self.channel,
                title=title,
                filename=filename,
                file=image_bytes,
                initial_comment=title
            )
            return response
        except SlackApiError as e:
            print(f"Erro ao enviar imagem para o Slack: {e}")
            return None
    
    def figure_to_image(self, fig):
        """Converte uma figura Plotly em bytes de imagem"""
        img_bytes = pio.to_image(fig, format="png", scale=2)
        return io.BytesIO(img_bytes)
    
    def html_to_image(self, html_content):
        """Converte HTML em uma imagem - útil para tabelas"""
        # Esta é uma implementação simplificada
        # Para uma solução completa, você poderia usar bibliotecas como selenium ou playwright
        # para renderizar HTML e capturar screenshots
        # Aqui vamos usar apenas um placeholder
        return None
    
    def send_channel_summary(self):
        """Envia um resumo do canal para o Slack"""
        if not channel_info:
            self.send_message("❌ Não foi possível obter informações do canal.")
            return
        
        # Mensagem de resumo
        summary = f"📊 *Relatório do Canal YouTube: {channel_info['title']}*\n"
        summary += f"📅 *Data do Relatório:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        summary += f"👥 *Inscritos:* {channel_info['subscriberCount']:,}\n"
        summary += f"👁️ *Total de Visualizações:* {channel_info['viewCount']:,}\n"
        summary += f"🎬 *Total de Vídeos:* {channel_info['videoCount']:,}\n"
        
        self.send_message(summary)
    
    def send_views_by_video_chart(self):
        """Envia o gráfico de visualizações por vídeo"""
        fig = update_views_by_video(None)
        img_bytes = self.figure_to_image(fig)
        self.send_image(
            img_bytes, 
            "📈 Visualizações por Vídeo (20 mais recentes)",
            "views_by_video.png"
        )
    
    def send_growth_chart(self):
        """Envia o gráfico de crescimento"""
        fig = update_growth_over_time(None)
        img_bytes = self.figure_to_image(fig)
        self.send_image(
            img_bytes,
            "📊 Crescimento Mensal de Visualizações",
            "growth_over_time.png"
        )
    
    def send_prediction_chart(self):
        """Envia o gráfico de previsão"""
        fig = update_growth_prediction(None)
        img_bytes = self.figure_to_image(fig)
        self.send_image(
            img_bytes,
            "🔮 Previsão de Crescimento (90 dias)",
            "growth_prediction.png"
        )
    
    def send_full_report(self):
        """Envia um relatório completo para o Slack"""
        self.send_channel_summary()
        self.send_views_by_video_chart()
        self.send_growth_chart()
        self.send_prediction_chart()
        
        # Mensagem de encerramento
        self.send_message("✅ *Relatório concluído!* Acesse o dashboard completo em: [LINK_DO_DEPLOY]")

def main():
    """Função principal para enviar relatório"""
    if not SLACK_API_TOKEN:
        print("❌ Token do Slack não configurado. Configure a variável de ambiente SLACK_API_TOKEN.")
        return 1
    
    print(f"🚀 Iniciando relatório para o canal Let's Media Oficia...")
    
    try:
        reporter = SlackReporter()
        reporter.send_full_report()
        print("✅ Relatório enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar relatório: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    main() 