"""
Script para enviar relatórios do Streamlit para o Slack
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
from streamlit_app import (
    predict_views_growth,
    get_analyzer,
    get_channel_info,
    get_videos_data
)

# Configuração do Slack
# Você precisa definir esta variável de ambiente com seu token do Slack
# export SLACK_API_TOKEN=xoxb-your-token
SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN", "")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#youtube-analytics")

# Configuração da API
API_KEY = 'AIzaSyCswbMKKorlHVSA_9kWSS9ZIKogaurZdNA'
CHANNEL_URL = 'https://youtube.com/@letsmediaoficial?si=Fk-kf1JqYBjj2LA0'

class StreamlitSlackReporter:
    def __init__(self, token=SLACK_API_TOKEN, channel=SLACK_CHANNEL):
        self.token = token
        self.channel = channel
        self.client = WebClient(token=token)
        
        # Inicializa o analisador YouTube
        self.analyzer = YouTubeAnalytics(API_KEY, channel_url=CHANNEL_URL)
        self.channel_info = self.analyzer.get_channel_info()
        self.df_videos = self.analyzer.get_channel_historical_data(video_count=100)
        
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
    
    def send_channel_summary(self):
        """Envia um resumo do canal para o Slack"""
        if not self.channel_info:
            self.send_message("❌ Não foi possível obter informações do canal.")
            return
        
        # Mensagem de resumo
        summary = f"📊 *Relatório do Canal YouTube: {self.channel_info['title']}*\n"
        summary += f"📅 *Data do Relatório:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        summary += f"👥 *Inscritos:* {self.channel_info['subscriberCount']:,}\n"
        summary += f"👁️ *Total de Visualizações:* {self.channel_info['viewCount']:,}\n"
        summary += f"🎬 *Total de Vídeos:* {self.channel_info['videoCount']:,}\n"
        
        # Adiciona métricas de engajamento
        if self.df_videos is not None and len(self.df_videos) > 0:
            avg_views = self.df_videos['viewCount'].mean()
            avg_likes = self.df_videos['likeCount'].mean()
            avg_comments = self.df_videos['commentCount'].mean()
            
            engagement_rate = (avg_likes + avg_comments) / avg_views * 100 if avg_views > 0 else 0
            
            summary += f"\n📈 *Métricas de Engajamento:*\n"
            summary += f"- Taxa de Engajamento Média: {engagement_rate:.2f}%\n"
            summary += f"- Visualizações Médias por Vídeo: {avg_views:.0f}\n"
            summary += f"- Likes Médios por Vídeo: {avg_likes:.0f}\n"
            summary += f"- Comentários Médios por Vídeo: {avg_comments:.0f}\n"
        
        self.send_message(summary)
    
    def send_views_by_video_chart(self):
        """Envia o gráfico de visualizações por vídeo"""
        if self.df_videos is None or len(self.df_videos) == 0:
            return
        
        # Seleciona os últimos 20 vídeos para visualização
        df_recent = self.df_videos.sort_values('publishedAt', ascending=False).head(20)
        
        import plotly.express as px
        fig = px.bar(df_recent, x='title', y='viewCount', 
                     labels={'viewCount': 'Visualizações', 'title': 'Título do Vídeo'},
                     title='Visualizações por Vídeo (20 mais recentes)')
        
        fig.update_layout(
            xaxis={'categoryorder': 'total descending'},
            xaxis_tickangle=-45,
            height=500
        )
        
        img_bytes = self.figure_to_image(fig)
        self.send_image(
            img_bytes, 
            "📈 Visualizações por Vídeo (20 mais recentes)",
            "views_by_video.png"
        )
    
    def send_growth_chart(self):
        """Envia o gráfico de crescimento"""
        if self.df_videos is None or len(self.df_videos) == 0:
            return
            
        # Cria uma cópia para evitar modificações no dataframe original
        df_for_growth = self.df_videos.copy()
        
        # Agrupa os vídeos por mês e soma as visualizações
        df_for_growth['month'] = df_for_growth['publishedAt'].dt.to_period('M')
        monthly_data = df_for_growth.groupby('month').agg({
            'viewCount': 'sum',
            'likeCount': 'sum',
            'commentCount': 'sum',
            'id': 'count'
        }).reset_index()
        
        monthly_data['month'] = monthly_data['month'].dt.to_timestamp()
        
        # Cria o gráfico de crescimento
        import plotly.graph_objects as go
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_data['month'], 
            y=monthly_data['viewCount'],
            mode='lines+markers',
            name='Visualizações',
            line=dict(width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data['month'], 
            y=monthly_data['id'] * 1000,  # Multiplicação para escala
            mode='lines+markers',
            name='Vídeos Publicados (x1000)',
            line=dict(width=2, dash='dot')
        ))
        
        fig.update_layout(
            title='Crescimento Mensal de Visualizações',
            xaxis_title='Mês',
            yaxis_title='Visualizações',
            height=500,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        img_bytes = self.figure_to_image(fig)
        self.send_image(
            img_bytes,
            "📊 Crescimento Mensal de Visualizações",
            "growth_over_time.png"
        )
    
    def send_prediction_chart(self):
        """Envia o gráfico de previsão"""
        if self.df_videos is None or len(self.df_videos) < 10:
            return
            
        try:
            # Prever crescimento para os próximos 90 dias
            forecast = predict_views_growth(self.df_videos, days=90)
            
            if forecast is None:
                return
                
            import plotly.graph_objects as go
            fig = go.Figure()
            
            # Dados históricos
            historical = self.df_videos.sort_values('publishedAt')
            historical_idx = len(historical)
            
            # Adiciona dados históricos
            fig.add_trace(go.Scatter(
                x=forecast['ds'][:historical_idx],
                y=forecast['y'][:historical_idx],
                mode='lines',
                name='Visualizações Históricas',
                line=dict(width=2)
            ))
            
            # Adiciona previsão
            fig.add_trace(go.Scatter(
                x=forecast['ds'][historical_idx:],
                y=forecast['yhat'][historical_idx:],
                mode='lines',
                name='Previsão',
                line=dict(width=3, dash='dash', color='red')
            ))
            
            # Adiciona intervalo de confiança
            fig.add_trace(go.Scatter(
                x=forecast['ds'][historical_idx:],
                y=forecast['yhat_upper'][historical_idx:],
                mode='lines',
                name='Limite Superior',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast['ds'][historical_idx:],
                y=forecast['yhat_lower'][historical_idx:],
                mode='lines',
                name='Limite Inferior',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(255, 0, 0, 0.1)',
                showlegend=False
            ))
            
            fig.update_layout(
                title='Previsão de Crescimento de Visualizações (90 dias)',
                xaxis_title='Data',
                yaxis_title='Visualizações Acumuladas',
                height=500,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            img_bytes = self.figure_to_image(fig)
            self.send_image(
                img_bytes,
                "🔮 Previsão de Crescimento (90 dias)",
                "growth_prediction.png"
            )
        except Exception as e:
            print(f"Erro na previsão de crescimento: {e}")
    
    def send_full_report(self):
        """Envia um relatório completo para o Slack"""
        self.send_channel_summary()
        self.send_views_by_video_chart()
        self.send_growth_chart()
        self.send_prediction_chart()
        
        # Mensagem de encerramento
        self.send_message("✅ *Relatório concluído!* Acesse o dashboard completo em: https://lets-media-analytics.streamlit.app")

def main():
    """Função principal para enviar relatório"""
    if not SLACK_API_TOKEN:
        print("❌ Token do Slack não configurado. Configure a variável de ambiente SLACK_API_TOKEN.")
        return 1
    
    print(f"🚀 Iniciando relatório para o canal Let's Media Oficia...")
    
    try:
        reporter = StreamlitSlackReporter()
        reporter.send_full_report()
        print("✅ Relatório enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar relatório: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    main() 