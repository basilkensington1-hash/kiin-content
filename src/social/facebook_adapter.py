"""
Facebook adapter for Reels using Facebook Graph API.
"""

import requests
import time
from typing import Dict, Any, List
from .base_adapter import BaseSocialAdapter, PostResult, PostStatus, VideoContent
import logging

logger = logging.getLogger(__name__)

class FacebookAdapter(BaseSocialAdapter):
    """Facebook Reels posting via Graph API"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__("facebook", credentials)
        self.access_token = credentials.get("access_token")
        self.page_id = credentials.get("page_id")  # Facebook Page ID
        self.api_base = "https://graph.facebook.com/v19.0"
        
    def authenticate(self) -> bool:
        """Authenticate with Facebook API"""
        try:
            url = f"{self.api_base}/me"
            params = {
                "access_token": self.access_token,
                "fields": "id,name"
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                self.authenticated = True
                user_data = response.json()
                self.log_action("Authentication successful", {"user": user_data.get("name")})
                return True
            else:
                self.log_action("Authentication failed", 
                              {"status": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            logger.error(f"Facebook authentication error: {e}")
            return False
    
    def upload_video(self, content: VideoContent) -> PostResult:
        """Upload video as Facebook Reel"""
        try:
            validation_errors = self.validate_content(content)
            if validation_errors:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message=f"Validation errors: {', '.join(validation_errors)}"
                )
            
            # Step 1: Create video container
            container_id = self._create_video_container(content)
            if not container_id:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to create video container"
                )
            
            # Step 2: Wait for processing
            if not self._wait_for_processing(container_id):
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Video processing failed"
                )
            
            # Step 3: Publish video
            post_id = self._publish_video(container_id)
            if post_id:
                return PostResult(
                    platform=self.platform_name,
                    post_id=post_id,
                    status=PostStatus.PUBLISHED,
                    message="Successfully published Facebook Reel",
                    url=f"https://www.facebook.com/{post_id}"
                )
            else:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to publish video"
                )
                
        except Exception as e:
            logger.error(f"Facebook upload error: {e}")
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message=f"Upload error: {str(e)}"
            )
    
    def _create_video_container(self, content: VideoContent) -> str:
        """Create video container for Reel upload"""
        try:
            # Use page ID for posting to page, or remove for personal profile
            endpoint = f"{self.page_id}/video_reels" if self.page_id else "me/video_reels"
            url = f"{self.api_base}/{endpoint}"
            
            # Prepare description with hashtags
            description = content.description
            if content.hashtags:
                description += "\n\n" + self.format_hashtags(content.hashtags)
            if content.mentions:
                description += "\n" + self.format_mentions(content.mentions)
            
            # Upload video file
            files = {'source': open(content.file_path, 'rb')}
            data = {
                'description': description,
                'upload_phase': 'start',
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                container_id = result.get("video_id")
                self.log_action("Video container created", {"container_id": container_id})
                return container_id
            else:
                self.log_action("Failed to create video container", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error creating video container: {e}")
            return None
        finally:
            # Close file if it was opened
            try:
                files['source'].close()
            except:
                pass
    
    def _wait_for_processing(self, container_id: str, max_wait: int = 300) -> bool:
        """Wait for video processing to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                url = f"{self.api_base}/{container_id}"
                params = {
                    "fields": "status",
                    "access_token": self.access_token
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status", {})
                    video_status = status.get("video_status")
                    
                    if video_status == "ready":
                        self.log_action("Video processing complete", {"container_id": container_id})
                        return True
                    elif video_status == "error":
                        self.log_action("Video processing error", {"container_id": container_id})
                        return False
                    
                    # Still processing
                    time.sleep(10)
                else:
                    logger.warning(f"Error checking processing status: {response.status_code}")
                    time.sleep(10)
                    
            except Exception as e:
                logger.error(f"Error checking processing status: {e}")
                time.sleep(10)
        
        self.log_action("Video processing timeout", {"container_id": container_id})
        return False
    
    def _publish_video(self, container_id: str) -> str:
        """Publish processed video"""
        try:
            # Use page ID for posting to page
            endpoint = f"{self.page_id}/video_reels" if self.page_id else "me/video_reels" 
            url = f"{self.api_base}/{endpoint}"
            
            data = {
                "video_id": container_id,
                "upload_phase": "finish",
                "access_token": self.access_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get("id")
                self.log_action("Video published", {"post_id": post_id})
                return post_id
            else:
                self.log_action("Failed to publish video", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error publishing video: {e}")
            return None
    
    def schedule_video(self, content: VideoContent, scheduled_time: str) -> PostResult:
        """Schedule video for future publishing"""
        try:
            validation_errors = self.validate_content(content)
            if validation_errors:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message=f"Validation errors: {', '.join(validation_errors)}"
                )
            
            # Facebook supports scheduling
            endpoint = f"{self.page_id}/video_reels" if self.page_id else "me/video_reels"
            url = f"{self.api_base}/{endpoint}"
            
            description = content.description
            if content.hashtags:
                description += "\n\n" + self.format_hashtags(content.hashtags)
            
            files = {'source': open(content.file_path, 'rb')}
            data = {
                'description': description,
                'scheduled_publish_time': scheduled_time,  # Unix timestamp
                'published': 'false',  # Keep as draft until scheduled time
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get("id")
                return PostResult(
                    platform=self.platform_name,
                    post_id=post_id,
                    status=PostStatus.SCHEDULED,
                    message="Successfully scheduled Facebook Reel",
                    scheduled_time=scheduled_time
                )
            else:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message=f"Failed to schedule video: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"Facebook scheduling error: {e}")
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message=f"Scheduling error: {str(e)}"
            )
        finally:
            try:
                files['source'].close()
            except:
                pass
    
    def get_post_status(self, post_id: str) -> PostStatus:
        """Get post status"""
        try:
            url = f"{self.api_base}/{post_id}"
            params = {
                "fields": "id,permalink_url,is_published",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                is_published = result.get("is_published", False)
                
                if is_published:
                    return PostStatus.PUBLISHED
                else:
                    return PostStatus.SCHEDULED
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
                "metric": "post_impressions,post_engaged_users,post_clicks,post_reactions_by_type_total",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                data = result.get("data", [])
                
                # Parse insights data
                analytics = {}
                for insight in data:
                    metric_name = insight.get("name")
                    value = insight.get("values", [{}])[0].get("value", 0)
                    analytics[metric_name] = value
                
                return analytics
            else:
                return {"error": f"Failed to get analytics: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information"""
        return {
            "note": "Facebook uses app-level rate limiting",
            "calls_per_hour": "200 calls per hour per user",
            "recommendation": "Space posts 3-5 minutes apart"
        }
    
    def validate_content(self, content: VideoContent) -> List[str]:
        """Validate content for Facebook"""
        errors = super().validate_content(content)
        
        # Facebook specific validations
        if len(content.description) > 2000:
            errors.append("Description too long (max 2000 characters)")
            
        # Video requirements for Reels
        if content.duration and content.duration > 90:
            errors.append("Facebook Reels should be 90 seconds or less")
            
        if content.aspect_ratio and content.aspect_ratio not in ["9:16", "1:1"]:
            errors.append("Facebook Reels work best with vertical (9:16) or square (1:1) aspect ratios")
            
        return errors
    
    def format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for Facebook"""
        # Facebook allows hashtags but they're less important than other platforms
        return ' '.join(f'#{tag}' for tag in hashtags[:10])  # Limit to 10 hashtags
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get Facebook page information"""
        if not self.page_id:
            return {"error": "No page ID configured"}
            
        try:
            url = f"{self.api_base}/{self.page_id}"
            params = {
                "fields": "name,category,followers_count,fan_count",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get page info: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}