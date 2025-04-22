"""
Análise de Canal do YouTube - Versão Streamlit
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from youtube_analytics import YouTubeAnalytics
from sklearn.linear_model import LinearRegression

# Configuração da página
st.set_page_config(
    page_title="Análise do Canal Let's Media Oficia",
    page_icon="📊",
    layout="wide"
)

# Configuração da API
API_KEY = 'AIzaSyCswbMKKorlHVSA_9kWSS9ZIKogaurZdNA'

# Título principal
st.title("Análise do Canal Let's Media Oficia")

try:
    # Inicialização da classe de análise usando busca direta
    @st.cache_resource
    def get_analyzer():
        analyzer = YouTubeAnalytics(API_KEY)
        # Busca o canal pelo nome exato
        channel_id = analyzer.search_channel_by_name("Let's Media Oficia")
        if channel_id:
            analyzer.channel_id = channel_id
            return analyzer
        else:
            st.error("Canal não encontrado via busca por nome. Tentando URL alternativa...")
            # Tenta usar o URL como fallback
            return YouTubeAnalytics(API_KEY, channel_url='https://www.youtube.com/@LetsMediaOficia')

    analyzer = get_analyzer()

    # Verifica se o canal foi encontrado
    @st.cache_data(ttl=3600)
    def get_channel_info():
        return analyzer.get_channel_info()

    channel_info = get_channel_info()

    if not channel_info:
        st.error("Canal não encontrado. Verifique a URL ou ID do canal.")
        st.info("Tente procurar o canal manualmente em https://www.youtube.com e copiar a URL exata.")
        st.stop()

    # Obtenção dos dados históricos a partir dos vídeos
    @st.cache_data(ttl=3600)
    def get_videos_data(video_count=100):
        return analyzer.get_channel_historical_data(video_count=video_count)

    df_videos = get_videos_data()

    # Função para prever crescimento de visualizações usando regressão linear
    def predict_views_growth(df, days=30):
        if df is None or len(df) < 10:
            return None
        
        # Preparar dados para previsão
        df_sorted = df.sort_values('publishedAt')
        
        # Criar série temporal agregada por dia
        df_sorted['date'] = df_sorted['publishedAt'].dt.date
        df_daily = df_sorted.groupby('date')['viewCount'].sum().reset_index()
        df_daily['date'] = pd.to_datetime(df_daily['date'])
        
        # Preencher datas faltantes e criar série contínua
        date_range = pd.date_range(start=df_daily['date'].min(), end=df_daily['date'].max())
        full_df = pd.DataFrame({'date': date_range})
        full_df = pd.merge(full_df, df_daily, on='date', how='left')
        full_df['viewCount'] = full_df['viewCount'].fillna(0)
        
        # Calcular visualizações cumulativas
        full_df['cumulative_views'] = full_df['viewCount'].cumsum()
        
        # Preparar dados para regressão linear
        X = np.arange(len(full_df)).reshape(-1, 1)
        y = full_df['cumulative_views'].values
        
        # Treinar modelo de regressão linear
        model = LinearRegression()
        model.fit(X, y)
        
        # Preparar datas para previsão
        future_dates = pd.date_range(
            start=full_df['date'].max() + timedelta(days=1),
            periods=days
        )
        
        # Prever valores futuros
        future_X = np.arange(len(full_df), len(full_df) + days).reshape(-1, 1)
        future_y = model.predict(future_X)
        
        # Criar dataframe com resultados
        forecast_df = pd.DataFrame({
            'ds': pd.concat([full_df['date'], pd.Series(future_dates)]),
            'y': np.concatenate([full_df['cumulative_views'].values, future_y]),
            'yhat': np.concatenate([full_df['cumulative_views'].values, future_y]),
            'yhat_lower': np.concatenate([
                full_df['cumulative_views'].values, 
                future_y * 0.9  # Limite inferior simples: -10%
            ]),
            'yhat_upper': np.concatenate([
                full_df['cumulative_views'].values, 
                future_y * 1.1  # Limite superior simples: +10%
            ])
        })
        
        return forecast_df

    # Layout do Dashboard
    col1, col2 = st.columns([1, 2])

    # Coluna 1: Informações do Canal
    with col1:
        st.subheader("Informações do Canal")
        st.metric("Inscritos", f"{channel_info['subscriberCount']:,}")
        st.metric("Total de Visualizações", f"{channel_info['viewCount']:,}")
        st.metric("Total de Vídeos", f"{channel_info['videoCount']:,}")
        st.write(f"**Data de Criação:** {datetime.fromisoformat(channel_info['publishedAt'].replace('Z', '+00:00')).strftime('%d/%m/%Y')}")

    # Coluna 2: Métricas de Engajamento
    with col2:
        st.subheader("Métricas de Engajamento")
        
        if df_videos is not None and len(df_videos) > 0:
            # Calcula taxas de engajamento médias
            avg_views = df_videos['viewCount'].mean()
            avg_likes = df_videos['likeCount'].mean()
            avg_comments = df_videos['commentCount'].mean()
            
            engagement_rate = (avg_likes + avg_comments) / avg_views * 100 if avg_views > 0 else 0
            like_rate = avg_likes / avg_views * 100 if avg_views > 0 else 0
            comment_rate = avg_comments / avg_views * 100 if avg_views > 0 else 0
            
            engagement_col1, engagement_col2, engagement_col3 = st.columns(3)
            
            with engagement_col1:
                st.metric("Taxa de Engajamento", f"{engagement_rate:.2f}%")
                st.metric("Visualizações Médias", f"{avg_views:.0f}")
            
            with engagement_col2:
                st.metric("Taxa de Likes", f"{like_rate:.2f}%")
                st.metric("Likes Médios", f"{avg_likes:.0f}")
                
            with engagement_col3:
                st.metric("Taxa de Comentários", f"{comment_rate:.2f}%")
                st.metric("Comentários Médios", f"{avg_comments:.0f}")
        else:
            st.warning("Dados insuficientes para calcular métricas de engajamento.")

    # Visualizações por Vídeo
    st.subheader("Visualizações por Vídeo")
    if df_videos is not None and len(df_videos) > 0:
        # Seleciona os últimos 20 vídeos para visualização
        df_recent = df_videos.sort_values('publishedAt', ascending=False).head(20)
        
        fig = px.bar(df_recent, x='title', y='viewCount', 
                    labels={'viewCount': 'Visualizações', 'title': 'Título do Vídeo'},
                    title='Visualizações por Vídeo (20 mais recentes)')
        
        fig.update_layout(
            xaxis={'categoryorder': 'total descending'},
            xaxis_tickangle=-45,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados insuficientes para mostrar visualizações por vídeo.")

    # Crescimento ao Longo do Tempo
    st.subheader("Crescimento ao Longo do Tempo")
    if df_videos is not None and len(df_videos) > 0:
        # Cria uma cópia para evitar o aviso de SettingWithCopyWarning
        df_for_growth = df_videos.copy()
        
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
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados insuficientes para mostrar crescimento ao longo do tempo.")

    # Previsão de Crescimento
    st.subheader("Previsão de Crescimento")
    if df_videos is not None and len(df_videos) >= 10:
        try:
            # Prever crescimento para os próximos 90 dias
            forecast = predict_views_growth(df_videos, days=90)
            
            if forecast is not None:
                fig = go.Figure()
                
                # Dados históricos
                historical = df_videos.sort_values('publishedAt')
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
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Não foi possível gerar previsões de crescimento com os dados disponíveis.")
        except Exception as e:
            st.error(f"Erro na previsão de crescimento: {e}")
    else:
        st.warning("Dados insuficientes para fazer previsões de crescimento.")

    # Vídeos com Maior Engajamento
    st.subheader("Vídeos com Maior Engajamento")
    if df_videos is not None and len(df_videos) > 0:
        # Calcula a taxa de engajamento para cada vídeo
        df_for_engagement = df_videos.copy()
        df_for_engagement['engagement_rate'] = (df_for_engagement['likeCount'] + df_for_engagement['commentCount']) / df_for_engagement['viewCount'] * 100
        
        # Seleciona os 10 vídeos com maior engajamento
        top_videos = df_for_engagement.sort_values('engagement_rate', ascending=False).head(10)
        
        # Cria uma tabela formatada com Streamlit
        st.dataframe(
            top_videos[['title', 'viewCount', 'likeCount', 'commentCount', 'engagement_rate']].rename(
                columns={
                    'title': 'Título', 
                    'viewCount': 'Visualizações', 
                    'likeCount': 'Likes', 
                    'commentCount': 'Comentários', 
                    'engagement_rate': 'Taxa de Engajamento (%)'
                }
            ).style.format({
                'Visualizações': '{:,}',
                'Likes': '{:,}',
                'Comentários': '{:,}',
                'Taxa de Engajamento (%)': '{:.2f}%'
            }),
            use_container_width=True
        )
    else:
        st.warning("Dados insuficientes para mostrar vídeos com maior engajamento.")

    # Canais Similares
    st.subheader("Canais Similares")
    similar_channels = analyzer.search_similar_channels(max_results=5)

    if similar_channels:
        # Cria colunas para mostrar os canais similares
        channel_cols = st.columns(len(similar_channels))
        
        for i, channel in enumerate(similar_channels):
            with channel_cols[i]:
                st.write(f"**{channel['title']}**")
                st.write(channel['description'][:200] + "..." if len(channel['description']) > 200 else channel['description'])
                st.write(f"[Visitar Canal](https://www.youtube.com/channel/{channel['id']})")
    else:
        st.warning("Nenhum canal similar encontrado.")
except Exception as e:
    st.error(f"Erro ao inicializar a aplicação: {e}")
    st.info("Detalhes do erro para ajudar na depuração:")
    st.exception(e) 