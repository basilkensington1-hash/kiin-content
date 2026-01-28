"""
Instagram adapter using Facebook Graph API for business accounts.
"""

import requests
import time
from typing import Dict, Any, List
from .base_adapter import BaseSocialAdapter, PostResult, PostStatus, VideoContent
import logging

logger = logging.getLogger(__name__)

class InstagramAdapter(BaseSocialAdapter):
    """Instagram posting via Facebook Graph API"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__("instagram", credentials)
        self.access_token = credentials.get("access_token")
        self.instagram_account_id = credentials.get("instagram_account_id")
        self.api_base = "https://graph.facebook.com/v19.0"
        
    def authenticate(self) -> bool:
        """Verify access token and account access"""
        try:
            url = f"{self.api_base}/{self.instagram_account_id}"
            params = {
                "fields": "id,username",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                self.authenticated = True
                self.log_action("Authentication successful", response.json())
                return True
            else:
                self.log_action("Authentication failed", {"status": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            logger.error(f"Instagram authentication error: {e}")
            return False
    
    def upload_video(self, content: VideoContent) -> PostResult:
        """Upload video to Instagram immediately"""
        try:
            # Validate content first
            validation_errors = self.validate_content(content)
            if validation_errors:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message=f"Validation errors: {', '.join(validation_errors)}"
                )
            
            # Step 1: Create media container
            container_id = self._create_media_container(content)
            if not container_id:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to create media container"
                )
            
            # Step 2: Wait for processing
            if not self._wait_for_processing(container_id):
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Media processing failed or timed out"
                )
            
            # Step 3: Publish media
            post_id = self._publish_media(container_id)
            if post_id:
                return PostResult(
                    platform=self.platform_name,
                    post_id=post_id,
                    status=PostStatus.PUBLISHED,
                    message="Successfully published to Instagram",
                    url=f"https://www.instagram.com/p/{post_id}/"
                )
            else:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to publish media"
                )
                
        except Exception as e:
            logger.error(f"Instagram upload error: {e}")
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message=f"Upload error: {str(e)}"
            )
    
    def schedule_video(self, content: VideoContent, scheduled_time: str) -> PostResult:
        """Schedule video for future posting (Instagram doesn't support native scheduling)"""
        # Instagram API doesn't support scheduling directly
        # This would need to be handled by the posting manager
        return PostResult(
            platform=self.platform_name,
            status=PostStatus.FAILED,
            message="Instagram doesn't support native scheduling. Use posting manager queue."
        )
    
    def _create_media_container(self, content: VideoContent) -> str:
        """Create media container for video upload"""
        try:
            # Format caption with hashtags and mentions
            caption = content.description
            if content.hashtags:
                caption += "\n\n" + self.format_hashtags(content.hashtags)
            if content.mentions:
                caption += "\n" + self.format_mentions(content.mentions)
            
            url = f"{self.api_base}/{self.instagram_account_id}/media"
            
            # Upload video file first to get media URL
            files = {'source': open(content.file_path, 'rb')}
            data = {
                'caption': caption,
                'media_type': 'REELS',  # For short videos
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                self.log_action("Media container created", {"container_id": result.get("id")})
                return result.get("id")
            else:
                self.log_action("Failed to create media container", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error creating media container: {e}")
            return None
        finally:
            # Close file if it was opened
            try:
                files['source'].close()
            except:
                pass
    
    def _wait_for_processing(self, container_id: str, max_wait: int = 300) -> bool:
        """Wait for media to finish processing"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                url = f"{self.api_base}/{container_id}"
                params = {
                    "fields": "status_code",
                    "access_token": self.access_token
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status_code")
                    
                    if status == "FINISHED":
                        self.log_action("Media processing complete", {"container_id": container_id})
                        return True
                    elif status == "ERROR":
                        self.log_action("Media processing error", {"container_id": container_id})
                        return False
                    
                    # Still processing, wait a bit
                    time.sleep(10)
                else:
                    logger.warning(f"Error checking processing status: {response.status_code}")
                    time.sleep(10)
                    
            except Exception as e:
                logger.error(f"Error checking processing status: {e}")
                time.sleep(10)
        
        self.log_action("Media processing timeout", {"container_id": container_id})
        return False
    
    def _publish_media(self, container_id: str) -> str:
        """Publish processed media"""
        try:
            url = f"{self.api_base}/{self.instagram_account_id}/media_publish"
            data = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get("id")
                self.log_action("Media published", {"post_id": post_id})
                return post_id
            else:
                self.log_action("Failed to publish media", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error publishing media: {e}")
            return None
    
    def get_post_status(self, post_id: str) -> PostStatus:
        """Get post status"""
        try:
            url = f"{self.api_base}/{post_id}"
            params = {
                "fields": "id,permalink",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return PostStatus.PUBLISHED
            else:
                return PostStatus.FAILED
                
        except Exception as e:
            logger.error(f"Error getting post status: {e}")
            return PostStatus.FAILED
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post"""
        try:
            url = f"{self.api_base}/{post_id}"
            params = {"access_token": self.access_token}
            
            response = requests.delete(url, params=params)
            
            if response.status_code == 200:
                self.log_action("Post deleted", {"post_id": post_id})
                return True
            else:
                self.log_action("Failed to delete post", 
                              {"post_id": post_id, "status": response.status_code})
                return False
                
        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            return False
    
    def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get post analytics"""
        try:
            url = f"{self.api_base}/{post_id}/insights"
            params = {
                "metric": "impressions,reach,likes,comments,saves,shares,plays",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get analytics: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information"""
        # Instagram uses app-level rate limiting
        return {
            "remaining": "Unknown - Instagram uses app-level limits",
            "reset_time": "Unknown",
            "limit_type": "app_level"
        }
    
    def validate_content(self, content: VideoContent) -> List[str]:
        """Validate content for Instagram"""
        errors = super().validate_content(content)
        
        # Instagram specific validations
        if len(content.description) > 2200:
            errors.append("Caption too long (max 2200 characters)")
            
        if len(content.hashtags) > 30:
            errors.append("Too many hashtags (max 30)")
            
        return errors