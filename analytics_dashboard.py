import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from youtube_analytics import YouTubeAnalytics
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA

# Configuração da API
API_KEY = 'AIzaSyCswbMKKorlHVSA_9kWSS9ZIKogaurZdNA'
CHANNEL_URL = 'https://www.youtube.com/@LetsMediaOficia'

# Inicialização da classe de análise
analyzer = YouTubeAnalytics(API_KEY, channel_url=CHANNEL_URL)

# Verifica se o canal foi encontrado
channel_info = analyzer.get_channel_info()
if not channel_info:
    print("Canal não encontrado. Verifique a URL ou ID do canal.")
    exit()

# Obtenção dos dados históricos a partir dos vídeos
df_videos = analyzer.get_channel_historical_data(video_count=100)

# Inicialização do app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = f"Análise do Canal: {channel_info['title']}"

# Função para conversão de tempo ISO 8601 para minutos
def iso8601_to_minutes(duration):
    hours = 0
    minutes = 0
    seconds = 0
    
    if 'H' in duration:
        hours = int(duration.split('H')[0].split('PT')[1])
        duration = duration.split('H')[1]
    else:
        duration = duration.split('PT')[1]
        
    if 'M' in duration:
        minutes = int(duration.split('M')[0])
        duration = duration.split('M')[1]
        
    if 'S' in duration:
        seconds = int(duration.split('S')[0])
    
    total_minutes = hours * 60 + minutes + seconds / 60
    return total_minutes

# Função para prever crescimento de visualizações usando ARIMA e regressão linear
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

# Layout do dashboard
def create_dashboard_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(f"Análise do Canal: {channel_info['title']}", className="mt-4 mb-4"),
                html.Hr()
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Informações do Canal", className="card-title"),
                        html.P(f"Inscritos: {channel_info['subscriberCount']:,}"),
                        html.P(f"Total de Visualizações: {channel_info['viewCount']:,}"),
                        html.P(f"Total de Vídeos: {channel_info['videoCount']:,}"),
                        html.P(f"Data de Criação: {datetime.fromisoformat(channel_info['publishedAt'].replace('Z', '+00:00')).strftime('%d/%m/%Y')}")
                    ])
                ], className="mb-4")
            ], width=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Métricas de Engajamento", className="card-title"),
                        html.Div(id="engagement-metrics")
                    ])
                ], className="mb-4")
            ], width=8)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Visualizações por Vídeo", className="card-title"),
                        dcc.Graph(id="views-by-video")
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Crescimento ao Longo do Tempo", className="card-title"),
                        dcc.Graph(id="growth-over-time")
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Previsão de Crescimento", className="card-title"),
                        dcc.Graph(id="growth-prediction")
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Vídeos com Maior Engajamento", className="card-title"),
                        html.Div(id="top-videos-table")
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Canais Similares", className="card-title"),
                        html.Div(id="similar-channels")
                    ])
                ], className="mb-4")
            ], width=12)
        ])
    ], fluid=True)

# Configuração do layout
app.layout = create_dashboard_layout()

# Callbacks para atualizar os gráficos
@app.callback(
    Output("engagement-metrics", "children"),
    [Input("engagement-metrics", "id")]
)
def update_engagement_metrics(_):
    if df_videos is None or len(df_videos) == 0:
        return html.P("Dados insuficientes para calcular métricas de engajamento.")
    
    # Calcula taxas de engajamento médias
    avg_views = df_videos['viewCount'].mean()
    avg_likes = df_videos['likeCount'].mean()
    avg_comments = df_videos['commentCount'].mean()
    
    engagement_rate = (avg_likes + avg_comments) / avg_views * 100 if avg_views > 0 else 0
    like_rate = avg_likes / avg_views * 100 if avg_views > 0 else 0
    comment_rate = avg_comments / avg_views * 100 if avg_views > 0 else 0
    
    return [
        html.P(f"Taxa de Engajamento Média: {engagement_rate:.2f}%"),
        html.P(f"Taxa de Likes: {like_rate:.2f}%"),
        html.P(f"Taxa de Comentários: {comment_rate:.2f}%"),
        html.P(f"Visualizações Médias por Vídeo: {avg_views:.0f}"),
        html.P(f"Likes Médios por Vídeo: {avg_likes:.0f}"),
        html.P(f"Comentários Médios por Vídeo: {avg_comments:.0f}")
    ]

@app.callback(
    Output("views-by-video", "figure"),
    [Input("views-by-video", "id")]
)
def update_views_by_video(_):
    if df_videos is None or len(df_videos) == 0:
        return go.Figure()
    
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
    
    return fig

@app.callback(
    Output("growth-over-time", "figure"),
    [Input("growth-over-time", "id")]
)
def update_growth_over_time(_):
    if df_videos is None or len(df_videos) == 0:
        return go.Figure()
    
    # Agrupa os vídeos por mês e soma as visualizações
    df_videos['month'] = df_videos['publishedAt'].dt.to_period('M')
    monthly_data = df_videos.groupby('month').agg({
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
    
    return fig

@app.callback(
    Output("growth-prediction", "figure"),
    [Input("growth-prediction", "id")]
)
def update_growth_prediction(_):
    if df_videos is None or len(df_videos) < 10:
        return go.Figure()
    
    try:
        # Prever crescimento para os próximos 90 dias
        forecast = predict_views_growth(df_videos, days=90)
        
        if forecast is None:
            return go.Figure()
        
        fig = go.Figure()
        
        # Dados históricos
        historical = df_videos.sort_values('publishedAt')
        
        # Adiciona dados históricos
        fig.add_trace(go.Scatter(
            x=forecast['ds'][:len(historical)],
            y=forecast['y'][:len(historical)],
            mode='lines',
            name='Visualizações Históricas',
            line=dict(width=2)
        ))
        
        # Adiciona previsão
        fig.add_trace(go.Scatter(
            x=forecast['ds'][len(historical):],
            y=forecast['yhat'][len(historical):],
            mode='lines',
            name='Previsão',
            line=dict(width=3, dash='dash', color='red')
        ))
        
        # Adiciona intervalo de confiança
        fig.add_trace(go.Scatter(
            x=forecast['ds'][len(historical):],
            y=forecast['yhat_upper'][len(historical):],
            mode='lines',
            name='Limite Superior',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast['ds'][len(historical):],
            y=forecast['yhat_lower'][len(historical):],
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
        
        return fig
    except Exception as e:
        print(f"Erro na previsão de crescimento: {e}")
        return go.Figure()

@app.callback(
    Output("top-videos-table", "children"),
    [Input("top-videos-table", "id")]
)
def update_top_videos_table(_):
    if df_videos is None or len(df_videos) == 0:
        return html.P("Dados insuficientes.")
    
    # Calcula a taxa de engajamento para cada vídeo
    df_videos['engagement_rate'] = (df_videos['likeCount'] + df_videos['commentCount']) / df_videos['viewCount'] * 100
    
    # Seleciona os 10 vídeos com maior engajamento
    top_videos = df_videos.sort_values('engagement_rate', ascending=False).head(10)
    
    # Cria a tabela
    table_header = [
        html.Thead(html.Tr([
            html.Th("Título"), 
            html.Th("Visualizações"), 
            html.Th("Likes"), 
            html.Th("Comentários"), 
            html.Th("Taxa de Engajamento (%)")
        ]))
    ]
    
    rows = []
    for _, video in top_videos.iterrows():
        row = html.Tr([
            html.Td(video['title']),
            html.Td(f"{video['viewCount']:,}"),
            html.Td(f"{video['likeCount']:,}"),
            html.Td(f"{video['commentCount']:,}"),
            html.Td(f"{video['engagement_rate']:.2f}%")
        ])
        rows.append(row)
    
    table_body = [html.Tbody(rows)]
    
    return dbc.Table(table_header + table_body, bordered=True, hover=True, striped=True, responsive=True)

@app.callback(
    Output("similar-channels", "children"),
    [Input("similar-channels", "id")]
)
def update_similar_channels(_):
    # Busca canais similares
    similar_channels = analyzer.search_similar_channels(max_results=5)
    
    if not similar_channels:
        return html.P("Nenhum canal similar encontrado.")
    
    # Cria cards para os canais similares
    cards = []
    for channel in similar_channels:
        card = dbc.Card([
            dbc.CardBody([
                html.H5(channel['title'], className="card-title"),
                html.P(channel['description'][:200] + "..." if len(channel['description']) > 200 else channel['description']),
                html.A("Visitar Canal", href=f"https://www.youtube.com/channel/{channel['id']}", 
                       className="btn btn-primary", target="_blank")
            ])
        ], className="mb-3")
        cards.append(card)
    
    return html.Div(cards)

# Executar o app
if __name__ == '__main__':
    app.run_server(debug=True) 