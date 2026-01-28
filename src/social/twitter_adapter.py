"""
Twitter/X adapter using Twitter API v2.
"""

import requests
import time
from typing import Dict, Any, List
from .base_adapter import BaseSocialAdapter, PostResult, PostStatus, VideoContent
import logging

logger = logging.getLogger(__name__)

class TwitterAdapter(BaseSocialAdapter):
    """Twitter/X video posting via API v2"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__("twitter", credentials)
        self.bearer_token = credentials.get("bearer_token")
        self.api_key = credentials.get("api_key")
        self.api_secret = credentials.get("api_secret")
        self.access_token = credentials.get("access_token")
        self.access_token_secret = credentials.get("access_token_secret")
        self.api_base = "https://api.twitter.com/2"
        self.upload_base = "https://upload.twitter.com/1.1"
        
    def authenticate(self) -> bool:
        """Authenticate with Twitter API"""
        try:
            url = f"{self.api_base}/users/me"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.authenticated = True
                user_data = response.json()
                self.log_action("Authentication successful", {"user": user_data.get("data", {}).get("username")})
                return True
            else:
                self.log_action("Authentication failed", 
                              {"status": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            logger.error(f"Twitter authentication error: {e}")
            return False
    
    def upload_video(self, content: VideoContent) -> PostResult:
        """Upload video to Twitter/X"""
        try:
            validation_errors = self.validate_content(content)
            if validation_errors:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message=f"Validation errors: {', '.join(validation_errors)}"
                )
            
            # Step 1: Upload video file
            media_id = self._upload_video_file(content.file_path)
            if not media_id:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to upload video file"
                )
            
            # Step 2: Wait for processing
            if not self._wait_for_processing(media_id):
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Video processing failed"
                )
            
            # Step 3: Create tweet with video
            tweet_id = self._create_tweet(media_id, content)
            if tweet_id:
                return PostResult(
                    platform=self.platform_name,
                    post_id=tweet_id,
                    status=PostStatus.PUBLISHED,
                    message="Successfully posted to Twitter",
                    url=f"https://twitter.com/username/status/{tweet_id}"
                )
            else:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to create tweet"
                )
                
        except Exception as e:
            logger.error(f"Twitter upload error: {e}")
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message=f"Upload error: {str(e)}"
            )
    
    def _upload_video_file(self, file_path: str) -> str:
        """Upload video file using chunked upload"""
        try:
            # Get file size
            import os
            file_size = os.path.getsize(file_path)
            
            # Step 1: INIT
            media_id = self._init_upload(file_size)
            if not media_id:
                return None
            
            # Step 2: APPEND (chunked upload)
            if not self._append_upload(media_id, file_path):
                return None
            
            # Step 3: FINALIZE
            if self._finalize_upload(media_id):
                return media_id
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error uploading video file: {e}")
            return None
    
    def _init_upload(self, file_size: int) -> str:
        """Initialize chunked upload"""
        try:
            url = f"{self.upload_base}/media/upload.json"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            
            data = {
                "command": "INIT",
                "total_bytes": file_size,
                "media_type": "video/mp4",
                "media_category": "tweet_video"
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                media_id = result.get("media_id_string")
                self.log_action("Upload initialized", {"media_id": media_id})
                return media_id
            else:
                self.log_action("Failed to initialize upload", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error initializing upload: {e}")
            return None
    
    def _append_upload(self, media_id: str, file_path: str) -> bool:
        """Append video data in chunks"""
        try:
            url = f"{self.upload_base}/media/upload.json"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            
            chunk_size = 5 * 1024 * 1024  # 5MB chunks
            segment_id = 0
            
            with open(file_path, 'rb') as video_file:
                while True:
                    chunk = video_file.read(chunk_size)
                    if not chunk:
                        break
                    
                    data = {
                        "command": "APPEND",
                        "media_id": media_id,
                        "segment_index": segment_id
                    }
                    
                    files = {"media": chunk}
                    
                    response = requests.post(url, headers=headers, data=data, files=files)
                    
                    if response.status_code != 204:
                        self.log_action("Failed to append chunk", 
                                      {"segment": segment_id, "status": response.status_code})
                        return False
                    
                    segment_id += 1
            
            self.log_action("Upload append complete", {"segments": segment_id})
            return True
            
        except Exception as e:
            logger.error(f"Error appending upload: {e}")
            return False
    
    def _finalize_upload(self, media_id: str) -> bool:
        """Finalize chunked upload"""
        try:
            url = f"{self.upload_base}/media/upload.json"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            
            data = {
                "command": "FINALIZE",
                "media_id": media_id
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                processing_info = result.get("processing_info")
                
                if processing_info:
                    self.log_action("Upload finalized, processing started", {"media_id": media_id})
                else:
                    self.log_action("Upload finalized", {"media_id": media_id})
                
                return True
            else:
                self.log_action("Failed to finalize upload", 
                              {"status": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            logger.error(f"Error finalizing upload: {e}")
            return False
    
    def _wait_for_processing(self, media_id: str, max_wait: int = 300) -> bool:
        """Wait for video processing to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                url = f"{self.upload_base}/media/upload.json"
                headers = {"Authorization": f"Bearer {self.bearer_token}"}
                params = {
                    "command": "STATUS",
                    "media_id": media_id
                }
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    processing_info = result.get("processing_info")
                    
                    if not processing_info:
                        # No processing info means it's ready
                        self.log_action("Video ready (no processing required)", {"media_id": media_id})
                        return True
                    
                    state = processing_info.get("state")
                    
                    if state == "succeeded":
                        self.log_action("Video processing complete", {"media_id": media_id})
                        return True
                    elif state == "failed":
                        error = processing_info.get("error", {})
                        self.log_action("Video processing failed", 
                                      {"media_id": media_id, "error": error})
                        return False
                    elif state in ["pending", "in_progress"]:
                        check_after = processing_info.get("check_after_secs", 10)
                        time.sleep(check_after)
                    else:
                        logger.warning(f"Unknown processing state: {state}")
                        time.sleep(10)
                else:
                    logger.warning(f"Error checking processing status: {response.status_code}")
                    time.sleep(10)
                    
            except Exception as e:
                logger.error(f"Error checking processing: {e}")
                time.sleep(10)
        
        self.log_action("Video processing timeout", {"media_id": media_id})
        return False
    
    def _create_tweet(self, media_id: str, content: VideoContent) -> str:
        """Create tweet with video attachment"""
        try:
            url = f"{self.api_base}/tweets"
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            # Format text with hashtags and mentions
            text = content.description or content.title
            if content.hashtags:
                hashtag_text = self.format_hashtags(content.hashtags)
                # Ensure total length doesn't exceed Twitter limit
                available_space = 280 - len(hashtag_text) - 2  # -2 for newlines
                if len(text) > available_space:
                    text = text[:available_space-3] + "..."
                text += "\n\n" + hashtag_text
            
            if content.mentions:
                mention_text = self.format_mentions(content.mentions)
                if len(text) + len(mention_text) + 1 <= 280:
                    text = mention_text + " " + text
            
            data = {
                "text": text,
                "media": {
                    "media_ids": [media_id]
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                result = response.json()
                tweet_id = result.get("data", {}).get("id")
                self.log_action("Tweet created", {"tweet_id": tweet_id})
                return tweet_id
            else:
                self.log_action("Failed to create tweet", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error creating tweet: {e}")
            return None
    
    def schedule_video(self, content: VideoContent, scheduled_time: str) -> PostResult:
        """Twitter doesn't support scheduling via API v2"""
        return PostResult(
            platform=self.platform_name,
            status=PostStatus.FAILED,
            message="Twitter doesn't support native scheduling via API. Use posting manager queue or Twitter's web interface."
        )
    
    def get_post_status(self, post_id: str) -> PostStatus:
        """Get tweet status"""
        try:
            url = f"{self.api_base}/tweets/{post_id}"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return PostStatus.PUBLISHED
            elif response.status_code == 404:
                return PostStatus.DELETED
            else:
                return PostStatus.FAILED
                
        except Exception as e:
            logger.error(f"Error getting post status: {e}")
            return PostStatus.FAILED
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a tweet"""
        try:
            url = f"{self.api_base}/tweets/{post_id}"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                self.log_action("Tweet deleted", {"tweet_id": post_id})
                return True
            else:
                self.log_action("Failed to delete tweet", 
                              {"tweet_id": post_id, "status": response.status_code})
                return False
                
        except Exception as e:
            logger.error(f"Error deleting tweet: {e}")
            return False
    
    def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get tweet analytics"""
        try:
            url = f"{self.api_base}/tweets/{post_id}"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            params = {
                "tweet.fields": "public_metrics,organic_metrics",
                "expansions": "attachments.media_keys"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", {})
                
                public_metrics = data.get("public_metrics", {})
                organic_metrics = data.get("organic_metrics", {})
                
                return {
                    "retweets": public_metrics.get("retweet_count", 0),
                    "likes": public_metrics.get("like_count", 0),
                    "replies": public_metrics.get("reply_count", 0),
                    "quotes": public_metrics.get("quote_count", 0),
                    "impressions": organic_metrics.get("impression_count", 0),
                    "url_clicks": organic_metrics.get("url_link_clicks", 0),
                    "profile_clicks": organic_metrics.get("user_profile_clicks", 0)
                }
            else:
                return {"error": f"Failed to get analytics: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information"""
        try:
            # Twitter includes rate limit info in response headers
            url = f"{self.api_base}/users/me"
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            
            response = requests.get(url, headers=headers)
            
            return {
                "remaining": response.headers.get("x-rate-limit-remaining"),
                "limit": response.headers.get("x-rate-limit-limit"),
                "reset_time": response.headers.get("x-rate-limit-reset")
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit info: {e}")
            return {"error": str(e)}
    
    def validate_content(self, content: VideoContent) -> List[str]:
        """Validate content for Twitter"""
        errors = super().validate_content(content)
        
        # Twitter specific validations
        max_text_length = 280
        if content.hashtags:
            hashtag_length = len(self.format_hashtags(content.hashtags))
            max_text_length -= hashtag_length + 2  # +2 for newlines
        
        if len(content.description) > max_text_length:
            errors.append(f"Text too long (max {max_text_length} characters with hashtags)")
        
        # Video duration limit
        if content.duration and content.duration > 140:  # 2 minutes 20 seconds
            errors.append("Video too long (max 140 seconds for Twitter)")
            
        return errors