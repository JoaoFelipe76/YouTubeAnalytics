import os
import pandas as pd
import numpy as np
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeAnalytics:
    def __init__(self, api_key, channel_url=None, channel_id=None):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.channel_id = channel_id
        
        if channel_url and not channel_id:
            # Vamos tentar várias abordagens para encontrar o canal
            self.channel_id = self._find_channel_from_url(channel_url)
    
    def _find_channel_from_url(self, url):
        """Método principal para encontrar canais, tenta várias abordagens"""
        print(f"Tentando encontrar canal a partir da URL: {url}")
        
        # Tenta extrair handle do url
        handle = None
        if '@' in url:
            handle = url.split('@')[1].split('?')[0].split('/')[0]
            print(f"Handle extraído: {handle}")
        
        # Abordagem 1: Busca pelo handle exato, apenas no Brasil
        if handle:
            try:
                print(f"Buscando canais no Brasil com handle: @{handle}")
                request = self.youtube.search().list(
                    part="snippet",
                    q=f"@{handle}",
                    type="channel",
                    regionCode="BR",
                    relevanceLanguage="pt",
                    maxResults=5
                )
                response = request.execute()
                
                if response.get('items'):
                    for item in response['items']:
                        print(f"Canal encontrado: {item['snippet']['title']}")
                        print(f"Channel ID: {item['snippet']['channelId']}")
                        # Se o título contém "Let's Media", vamos usá-lo
                        if "let's media" in item['snippet']['title'].lower():
                            print(f"Canal encontrado pelo título: {item['snippet']['title']}")
                            return item['snippet']['channelId']
                    
                    # Se não encontrou por título específico, usa o primeiro
                    print(f"Usando primeiro canal encontrado: {response['items'][0]['snippet']['title']}")
                    return response['items'][0]['snippet']['channelId']
            except Exception as e:
                print(f"Erro na busca por handle: {e}")
        
        # Abordagem 2: Busca direta pelo nome específico "Let's Media Oficial"
        try:
            print("Buscando pelo nome específico 'Let's Media Oficial'")
            request = self.youtube.search().list(
                part="snippet",
                q="Let's Media Oficial",
                type="channel",
                regionCode="BR",
                relevanceLanguage="pt",
                maxResults=5
            )
            response = request.execute()
            
            if response.get('items'):
                for item in response['items']:
                    print(f"Canal encontrado: {item['snippet']['title']}")
                    return item['snippet']['channelId']
        except Exception as e:
            print(f"Erro na busca pelo nome específico: {e}")
        
        # Abordagem 3: Última tentativa, busca genérica
        try:
            print("Última tentativa: busca genérica por 'letsmediaoficial'")
            request = self.youtube.search().list(
                part="snippet",
                q="letsmediaoficial",
                type="channel",
                regionCode="BR",
                maxResults=1
            )
            response = request.execute()
            
            if response.get('items'):
                print(f"Canal encontrado na busca genérica: {response['items'][0]['snippet']['title']}")
                return response['items'][0]['snippet']['channelId']
        except Exception as e:
            print(f"Erro na busca genérica: {e}")
        
        print("Nenhum canal encontrado após várias tentativas")
        return None
    
    def search_channel_by_name(self, channel_name):
        """Busca o canal diretamente pelo nome exato"""
        try:
            print(f"Buscando canal pelo nome: {channel_name}")
            request = self.youtube.search().list(
                part="snippet",
                q=channel_name,
                type="channel",
                regionCode="BR",
                relevanceLanguage="pt",
                maxResults=5
            )
            response = request.execute()
            
            # Procura por correspondência exata no nome
            for item in response.get('items', []):
                title = item['snippet']['title']
                print(f"Encontrado canal: {title}")
                if title.lower() == channel_name.lower() or title.lower().startswith(channel_name.lower()):
                    print(f"Correspondência exata encontrada: {title}")
                    return item['snippet']['channelId']
            
            # Se não encontrou uma correspondência exata, retorna o primeiro resultado
            if response.get('items'):
                print(f"Usando primeiro resultado: {response['items'][0]['snippet']['title']}")
                return response['items'][0]['snippet']['channelId']
                
            return None
        except HttpError as e:
            print(f"Erro ao buscar canal pelo nome: {e}")
            return None
    
    def get_channel_info(self):
        try:
            if not self.channel_id:
                print("ID do canal não encontrado. Tentando última busca pelo nome.")
                self.channel_id = self.search_channel_by_name("Let's Media Oficial")
                if not self.channel_id:
                    print("ID do canal não encontrado após todas as tentativas.")
                    return None
                
            print(f"Buscando informações para channel_id: {self.channel_id}")
            request = self.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                id=self.channel_id
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                info = {
                    'id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'customUrl': channel['snippet'].get('customUrl', ''),
                    'publishedAt': channel['snippet']['publishedAt'],
                    'thumbnails': channel['snippet']['thumbnails'],
                    'subscriberCount': int(channel['statistics'].get('subscriberCount', 0)),
                    'videoCount': int(channel['statistics'].get('videoCount', 0)),
                    'viewCount': int(channel['statistics'].get('viewCount', 0)),
                    'playlistId': channel['contentDetails']['relatedPlaylists']['uploads']
                }
                print(f"Canal encontrado: {info['title']}")
                return info
            else:
                print("Nenhum canal encontrado com este ID.")
                return None
        except HttpError as e:
            print(f"Erro ao obter informações do canal: {e}")
            return None
    
    def get_all_videos(self, max_results=None):
        channel_info = self.get_channel_info()
        if not channel_info:
            return []
        
        uploads_playlist_id = channel_info['playlistId']
        videos = []
        next_page_token = None
        count = 0
        
        while True:
            try:
                request = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response['items']:
                    video_id = item['contentDetails']['videoId']
                    video_info = {
                        'id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'publishedAt': item['snippet']['publishedAt'],
                        'thumbnails': item['snippet']['thumbnails']
                    }
                    videos.append(video_info)
                    count += 1
                    
                    if max_results and count >= max_results:
                        return videos
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            except HttpError as e:
                print(f"Erro ao obter vídeos: {e}")
                break
        
        return videos
    
    def get_video_statistics(self, video_ids):
        if isinstance(video_ids, str):
            video_ids = [video_ids]
            
        video_stats = []
        # Divide em grupos de 50 IDs devido às limitações da API
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            try:
                request = self.youtube.videos().list(
                    part="statistics,contentDetails",
                    id=','.join(batch)
                )
                response = request.execute()
                
                for item in response['items']:
                    stats = {
                        'id': item['id'],
                        'viewCount': int(item['statistics'].get('viewCount', 0)),
                        'likeCount': int(item['statistics'].get('likeCount', 0)),
                        'commentCount': int(item['statistics'].get('commentCount', 0)),
                        'duration': item['contentDetails']['duration'],
                        'definition': item['contentDetails']['definition']
                    }
                    video_stats.append(stats)
            except HttpError as e:
                print(f"Erro ao obter estatísticas dos vídeos: {e}")
        
        return video_stats
    
    def get_channel_historical_data(self, video_count=50):
        """
        Obtém dados históricos aproximados analisando os vídeos mais recentes
        """
        videos = self.get_all_videos(max_results=video_count)
        if not videos:
            return None
            
        video_ids = [video['id'] for video in videos]
        video_stats = self.get_video_statistics(video_ids)
        
        # Mapeia estatísticas para os vídeos
        video_data = []
        for video, stats in zip(videos, video_stats):
            video_info = {
                'id': video['id'],
                'title': video['title'],
                'publishedAt': video['publishedAt'],
                'viewCount': stats.get('viewCount', 0),
                'likeCount': stats.get('likeCount', 0),
                'commentCount': stats.get('commentCount', 0)
            }
            video_data.append(video_info)
        
        df = pd.DataFrame(video_data)
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df = df.sort_values(by='publishedAt')
        
        return df
    
    def get_video_comments(self, video_id, max_results=100):
        comments = []
        next_page_token = None
        count = 0
        
        while True:
            try:
                request = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(100, max_results - count),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comment_info = {
                        'authorDisplayName': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'publishedAt': comment['publishedAt'],
                        'likeCount': comment['likeCount']
                    }
                    comments.append(comment_info)
                    count += 1
                    
                    if count >= max_results:
                        return comments
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            except HttpError as e:
                if 'commentsDisabled' in str(e):
                    print(f"Comentários desativados para o vídeo {video_id}")
                else:
                    print(f"Erro ao obter comentários: {e}")
                break
        
        return comments
    
    def search_similar_channels(self, query=None, max_results=10):
        if not query:
            channel_info = self.get_channel_info()
            if channel_info:
                query = channel_info['title']
            else:
                return []
                
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=max_results
            )
            response = request.execute()
            
            similar_channels = []
            for item in response['items']:
                if item['snippet']['channelId'] != self.channel_id:  # Exclui o próprio canal
                    channel_info = {
                        'id': item['snippet']['channelId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnails': item['snippet']['thumbnails']
                    }
                    similar_channels.append(channel_info)
            
            return similar_channels
        except HttpError as e:
            print(f"Erro ao buscar canais similares: {e}")
            return [] 