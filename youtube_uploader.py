"""
YouTube Uploader
Handles uploading videos to YouTube using the YouTube Data API
"""

import os
import logging
import pickle
from pathlib import Path
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class YouTubeUploader:
    """Upload videos to YouTube"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, client_secrets_file: str):
        """
        Initialize YouTube uploader
        
        Args:
            client_secrets_file: Path to OAuth2 client secrets JSON file
        """
        self.client_secrets_file = client_secrets_file
        self.credentials = None
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API"""
        token_file = 'youtube_token.pickle'
        
        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # Refresh or get new credentials
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    logger.info("Refreshed YouTube credentials")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {str(e)}")
                    self.credentials = None
            
            if not self.credentials:
                if not os.path.exists(self.client_secrets_file):
                    logger.error(f"Client secrets file not found: {self.client_secrets_file}")
                    raise FileNotFoundError(
                        f"YouTube client secrets not found. Please download from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.SCOPES
                )
                self.credentials = flow.run_local_server(port=0)
                logger.info("Obtained new YouTube credentials")
            
            # Save credentials for future use
            with open(token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        logger.info("YouTube service initialized")
    
    def upload_video(self, video_path: str, title: str, description: str,
                    category: str = "22", privacy_status: str = "private",
                    tags: Optional[list] = None) -> Dict:
        """
        Upload a video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            category: YouTube category ID (default: 22 - People & Blogs)
            privacy_status: 'public', 'private', or 'unlisted'
            tags: List of tags for the video
            
        Returns:
            Dictionary with upload results including video ID and URL
        """
        logger.info(f"Uploading video to YouTube: {title}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # YouTube description limit
                    'tags': tags or [],
                    'categoryId': category
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create upload request
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # Upload in a single request
                resumable=True,
                mimetype='video/*'
            )
            
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            # Execute upload with progress tracking
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"Video uploaded successfully: {video_url}")
            
            return {
                'id': video_id,
                'url': video_url,
                'title': title,
                'status': 'uploaded',
                'privacy': privacy_status
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            raise
    
    def update_video(self, video_id: str, title: Optional[str] = None,
                    description: Optional[str] = None,
                    tags: Optional[list] = None,
                    privacy_status: Optional[str] = None) -> Dict:
        """
        Update video metadata
        
        Args:
            video_id: YouTube video ID
            title: New title (optional)
            description: New description (optional)
            tags: New tags (optional)
            privacy_status: New privacy status (optional)
            
        Returns:
            Updated video information
        """
        logger.info(f"Updating video: {video_id}")
        
        try:
            # Get current video details
            video_response = self.youtube.videos().list(
                part='snippet,status',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                raise ValueError(f"Video not found: {video_id}")
            
            video = video_response['items'][0]
            
            # Update fields
            if title:
                video['snippet']['title'] = title
            if description:
                video['snippet']['description'] = description
            if tags:
                video['snippet']['tags'] = tags
            if privacy_status:
                video['status']['privacyStatus'] = privacy_status
            
            # Update video
            update_response = self.youtube.videos().update(
                part='snippet,status',
                body=video
            ).execute()
            
            logger.info(f"Video updated successfully: {video_id}")
            
            return {
                'id': video_id,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'title': update_response['snippet']['title'],
                'status': 'updated'
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating video: {str(e)}")
            raise
    
    def delete_video(self, video_id: str) -> bool:
        """
        Delete a video from YouTube
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if successful
        """
        logger.info(f"Deleting video: {video_id}")
        
        try:
            self.youtube.videos().delete(id=video_id).execute()
            logger.info(f"Video deleted successfully: {video_id}")
            return True
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error deleting video: {str(e)}")
            raise
    
    def get_video_status(self, video_id: str) -> Dict:
        """
        Get the status of an uploaded video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video status information
        """
        try:
            response = self.youtube.videos().list(
                part='status,snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            if not response['items']:
                raise ValueError(f"Video not found: {video_id}")
            
            video = response['items'][0]
            
            return {
                'id': video_id,
                'title': video['snippet']['title'],
                'upload_status': video['status']['uploadStatus'],
                'privacy_status': video['status']['privacyStatus'],
                'view_count': video['statistics'].get('viewCount', 0),
                'like_count': video['statistics'].get('likeCount', 0),
                'comment_count': video['statistics'].get('commentCount', 0),
                'duration': video['contentDetails']['duration']
            }
            
        except Exception as e:
            logger.error(f"Error getting video status: {str(e)}")
            raise


def setup_youtube_credentials():
    """
    Guide user through setting up YouTube API credentials
    """
    print("\n=== YouTube API Setup ===")
    print("\nTo upload videos to YouTube, you need to:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project (or select existing)")
    print("3. Enable YouTube Data API v3")
    print("4. Create OAuth 2.0 credentials (Desktop app)")
    print("5. Download the credentials JSON file")
    print("6. Save it as 'client_secrets.json' in this directory")
    print("\nFor detailed instructions, visit:")
    print("https://developers.google.com/youtube/v3/getting-started")
    print("\n========================\n")


if __name__ == "__main__":
    # Test the uploader
    import sys
    
    if len(sys.argv) < 2:
        setup_youtube_credentials()
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    uploader = YouTubeUploader('client_secrets.json')
    result = uploader.upload_video(
        video_path=video_path,
        title="Test Video Upload",
        description="This is a test upload from the automated video system",
        privacy_status="private"
    )
    
    print(f"\nVideo uploaded successfully!")
    print(f"URL: {result['url']}")
    print(f"Video ID: {result['id']}")
