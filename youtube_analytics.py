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
            # Extrair channel ID da URL se fornecida
            if '@' in channel_url:
                handle = channel_url.split('@')[-1]
                self.channel_id = self._get_channel_id_from_handle(handle)
            else:
                self.channel_id = self._extract_channel_id(channel_url)
    
    def _get_channel_id_from_handle(self, handle):
        """Busca o ID do canal a partir do handle (@nome)"""
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=f"@{handle}",
                type="channel",
                maxResults=1
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
        except HttpError as e:
            print(f"Erro ao buscar handle do canal: {e}")
            
        return None
    
    def _get_channel_id_from_username(self, username):
        try:
            request = self.youtube.channels().list(
                part="id",
                forUsername=username
            )
            response = request.execute()
            
            if response.get('items'):
                return response['items'][0]['id']
        except HttpError as e:
            print(f"Erro ao buscar username do canal: {e}")
            
        return None
    
    def _extract_channel_id(self, url):
        # Extrair channel ID de diferentes formatos de URL
        if 'channel/' in url:
            return url.split('channel/')[-1].split('/')[0]
        elif 'user/' in url:
            username = url.split('user/')[-1].split('/')[0]
            return self._get_channel_id_from_username(username)
        return None
    
    def get_channel_info(self):
        try:
            if not self.channel_id:
                print("ID do canal não encontrado")
                return None
                
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
                return info
            else:
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