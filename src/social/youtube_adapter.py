"""
YouTube Shorts adapter using YouTube Data API v3.
"""

import requests
import time
import json
from typing import Dict, Any, List
from .base_adapter import BaseSocialAdapter, PostResult, PostStatus, VideoContent
import logging

logger = logging.getLogger(__name__)

class YouTubeAdapter(BaseSocialAdapter):
    """YouTube Shorts posting via YouTube Data API v3"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__("youtube", credentials)
        self.access_token = credentials.get("access_token")
        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret") 
        self.refresh_token = credentials.get("refresh_token")
        self.api_base = "https://www.googleapis.com/youtube/v3"
        self.upload_base = "https://www.googleapis.com/upload/youtube/v3"
        
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        try:
            # Check if current token is valid
            url = f"{self.api_base}/channels"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {"part": "id", "mine": True}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                self.authenticated = True
                self.log_action("Authentication successful")
                return True
            elif response.status_code == 401:
                # Try to refresh token
                if self._refresh_access_token():
                    return self.authenticate()
                else:
                    return False
            else:
                logger.error(f"YouTube auth failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"YouTube authentication error: {e}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        try:
            url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                self.log_action("Token refreshed successfully")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    def upload_video(self, content: VideoContent) -> PostResult:
        """Upload video to YouTube as a Short"""
        try:
            validation_errors = self.validate_content(content)
            if validation_errors:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message=f"Validation errors: {', '.join(validation_errors)}"
                )
            
            # Step 1: Upload video file
            video_id = self._upload_video_file(content)
            if not video_id:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to upload video file"
                )
            
            # Step 2: Wait for processing
            if self._wait_for_processing(video_id):
                return PostResult(
                    platform=self.platform_name,
                    post_id=video_id,
                    status=PostStatus.PUBLISHED,
                    message="Successfully uploaded to YouTube",
                    url=f"https://www.youtube.com/watch?v={video_id}"
                )
            else:
                return PostResult(
                    platform=self.platform_name,
                    post_id=video_id,
                    status=PostStatus.PROCESSING,
                    message="Video uploaded but still processing",
                    url=f"https://www.youtube.com/watch?v={video_id}"
                )
                
        except Exception as e:
            logger.error(f"YouTube upload error: {e}")
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message=f"Upload error: {str(e)}"
            )
    
    def _upload_video_file(self, content: VideoContent) -> str:
        """Upload video file to YouTube"""
        try:
            url = f"{self.upload_base}/videos"
            
            # Prepare metadata
            description = content.description
            if content.hashtags:
                description += "\n\n" + self.format_hashtags(content.hashtags)
            if content.mentions:
                description += "\n" + self.format_mentions(content.mentions)
            
            # Add #Shorts tag for YouTube Shorts
            if "#Shorts" not in description and "#shorts" not in description:
                description += "\n\n#Shorts"
            
            snippet = {
                "title": content.title,
                "description": description,
                "tags": content.hashtags + ["Shorts", "caregiver", "caregiving"],
                "categoryId": "22",  # People & Blogs
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en"
            }
            
            # Set as unlisted initially, then make public after processing
            status = {
                "privacyStatus": "private",  # Start as private
                "selfDeclaredMadeForKids": False
            }
            
            metadata = {
                "snippet": snippet,
                "status": status
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "part": "snippet,status",
                "uploadType": "resumable"
            }
            
            # Initiate resumable upload
            response = requests.post(
                url, 
                headers=headers, 
                params=params, 
                json=metadata
            )
            
            if response.status_code == 200:
                upload_url = response.headers.get("Location")
                if upload_url:
                    # Upload the actual file
                    return self._resumable_upload(upload_url, content.file_path)
                else:
                    logger.error("No upload URL in response")
                    return None
            else:
                self.log_action("Failed to initiate upload", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return None
    
    def _resumable_upload(self, upload_url: str, file_path: str) -> str:
        """Perform resumable upload of video file"""
        try:
            with open(file_path, 'rb') as video_file:
                headers = {
                    "Content-Type": "application/octet-stream"
                }
                
                response = requests.put(upload_url, headers=headers, data=video_file)
                
                if response.status_code == 200:
                    result = response.json()
                    video_id = result.get("id")
                    self.log_action("Video uploaded", {"video_id": video_id})
                    
                    # Make video public after successful upload
                    self._set_video_public(video_id)
                    
                    return video_id
                else:
                    self.log_action("Resumable upload failed", 
                                  {"status": response.status_code, "response": response.text})
                    return None
                    
        except Exception as e:
            logger.error(f"Error in resumable upload: {e}")
            return None
    
    def _set_video_public(self, video_id: str):
        """Set video privacy to public"""
        try:
            url = f"{self.api_base}/videos"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "id": video_id,
                "status": {
                    "privacyStatus": "public"
                }
            }
            
            params = {"part": "status"}
            
            response = requests.put(url, headers=headers, params=params, json=data)
            
            if response.status_code == 200:
                self.log_action("Video made public", {"video_id": video_id})
            else:
                self.log_action("Failed to make video public", 
                              {"video_id": video_id, "status": response.status_code})
                
        except Exception as e:
            logger.error(f"Error setting video public: {e}")
    
    def _wait_for_processing(self, video_id: str, max_wait: int = 300) -> bool:
        """Wait for video processing to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                url = f"{self.api_base}/videos"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                params = {
                    "part": "status,processingDetails",
                    "id": video_id
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    items = result.get("items", [])
                    
                    if items:
                        status = items[0].get("status", {})
                        upload_status = status.get("uploadStatus")
                        
                        if upload_status == "processed":
                            self.log_action("Video processing complete", {"video_id": video_id})
                            return True
                        elif upload_status == "failed":
                            self.log_action("Video processing failed", {"video_id": video_id})
                            return False
                        
                        # Still processing
                        time.sleep(10)
                    else:
                        logger.warning(f"Video {video_id} not found")
                        return False
                else:
                    logger.warning(f"Error checking processing status: {response.status_code}")
                    time.sleep(10)
                    
            except Exception as e:
                logger.error(f"Error checking processing: {e}")
                time.sleep(10)
        
        # Timeout - video might still be processing
        return False
    
    def schedule_video(self, content: VideoContent, scheduled_time: str) -> PostResult:
        """Schedule video for future publishing"""
        # YouTube supports scheduling, but implementation is complex
        # For now, return a note about manual scheduling
        return PostResult(
            platform=self.platform_name,
            status=PostStatus.FAILED,
            message="YouTube scheduling requires complex implementation. Use posting manager queue or YouTube Studio."
        )
    
    def get_post_status(self, post_id: str) -> PostStatus:
        """Get video status"""
        try:
            url = f"{self.api_base}/videos"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "part": "status",
                "id": post_id
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                items = result.get("items", [])
                
                if items:
                    status = items[0].get("status", {})
                    upload_status = status.get("uploadStatus")
                    privacy_status = status.get("privacyStatus")
                    
                    if upload_status == "processed" and privacy_status == "public":
                        return PostStatus.PUBLISHED
                    elif upload_status == "processing":
                        return PostStatus.PROCESSING
                    elif upload_status == "failed":
                        return PostStatus.FAILED
                    else:
                        return PostStatus.PROCESSING
                else:
                    return PostStatus.FAILED
            else:
                return PostStatus.FAILED
                
        except Exception as e:
            logger.error(f"Error getting post status: {e}")
            return PostStatus.FAILED
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a video"""
        try:
            url = f"{self.api_base}/videos"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {"id": post_id}
            
            response = requests.delete(url, headers=headers, params=params)
            
            if response.status_code == 204:
                self.log_action("Video deleted", {"video_id": post_id})
                return True
            else:
                self.log_action("Failed to delete video", 
                              {"video_id": post_id, "status": response.status_code})
                return False
                
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False
    
    def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get video analytics"""
        try:
            # YouTube Analytics API requires separate setup
            # For now, return basic video statistics
            url = f"{self.api_base}/videos"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "part": "statistics,snippet",
                "id": post_id
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                items = result.get("items", [])
                
                if items:
                    stats = items[0].get("statistics", {})
                    snippet = items[0].get("snippet", {})
                    
                    return {
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                        "title": snippet.get("title"),
                        "published_at": snippet.get("publishedAt")
                    }
                else:
                    return {"error": "Video not found"}
            else:
                return {"error": f"Failed to get analytics: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information"""
        # YouTube has quota limits, not traditional rate limits
        return {
            "quota_cost_per_upload": "1600 units",
            "daily_quota_limit": "10000 units",
            "note": "YouTube uses quota system, not rate limits"
        }
    
    def validate_content(self, content: VideoContent) -> List[str]:
        """Validate content for YouTube"""
        errors = super().validate_content(content)
        
        # YouTube specific validations
        if len(content.title) > 100:
            errors.append("Title too long (max 100 characters)")
            
        if len(content.description) > 5000:
            errors.append("Description too long (max 5000 characters)")
            
        # Check for Shorts requirements
        if content.duration and content.duration > 60:
            errors.append("YouTube Shorts must be 60 seconds or less")
            
        if content.aspect_ratio and content.aspect_ratio not in ["9:16", "1:1"]:
            errors.append("YouTube Shorts should be vertical (9:16) or square (1:1)")
            
        return errors
    
    def format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for YouTube"""
        # YouTube hashtags should be at the end of description
        return ' '.join(f'#{tag}' for tag in hashtags[:15])  # Max 15 hashtags