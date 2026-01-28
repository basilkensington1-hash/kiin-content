"""
Pinterest adapter for video pins and caregiver content.
"""

import requests
from typing import Dict, Any, List
from .base_adapter import BaseSocialAdapter, PostResult, PostStatus, VideoContent
import logging

logger = logging.getLogger(__name__)

class PinterestAdapter(BaseSocialAdapter):
    """Pinterest video pins adapter"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__("pinterest", credentials)
        self.access_token = credentials.get("access_token")
        self.api_base = "https://api.pinterest.com/v5"
        
    def authenticate(self) -> bool:
        """Authenticate with Pinterest API"""
        try:
            url = f"{self.api_base}/user_account"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.authenticated = True
                user_data = response.json()
                self.log_action("Authentication successful", 
                              {"username": user_data.get("username")})
                return True
            else:
                self.log_action("Authentication failed", 
                              {"status": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            logger.error(f"Pinterest authentication error: {e}")
            return False
    
    def upload_video(self, content: VideoContent) -> PostResult:
        """Create video pin on Pinterest"""
        try:
            validation_errors = self.validate_content(content)
            if validation_errors:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message=f"Validation errors: {', '.join(validation_errors)}"
                )
            
            # Create video pin
            pin_id = self._create_video_pin(content)
            if pin_id:
                return PostResult(
                    platform=self.platform_name,
                    post_id=pin_id,
                    status=PostStatus.PUBLISHED,
                    message="Successfully created Pinterest video pin",
                    url=f"https://www.pinterest.com/pin/{pin_id}/"
                )
            else:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to create video pin"
                )
                
        except Exception as e:
            logger.error(f"Pinterest upload error: {e}")
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message=f"Upload error: {str(e)}"
            )
    
    def _create_video_pin(self, content: VideoContent) -> str:
        """Create a video pin"""
        try:
            url = f"{self.api_base}/pins"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "multipart/form-data"
            }
            
            # Prepare description with hashtags
            description = content.description
            if content.hashtags:
                # Pinterest allows up to 20 hashtags
                hashtag_text = self.format_hashtags(content.hashtags[:20])
                description += "\n\n" + hashtag_text
            
            # Prepare form data
            files = {
                "video_file": open(content.file_path, 'rb')
            }
            
            data = {
                "title": content.title,
                "description": description,
                "link": "",  # Optional: link to website
                "board_id": "",  # Will need to be set based on user's boards
            }
            
            # Get user's boards first to assign pin
            board_id = self._get_default_board()
            if board_id:
                data["board_id"] = board_id
            
            # Note: Pinterest API for video upload is complex and may require
            # different endpoints depending on the video size and format
            
            # For now, this is a placeholder implementation
            # Real implementation would need to handle:
            # 1. Video size limits
            # 2. Proper multipart upload
            # 3. Board selection
            
            response = requests.post(url, headers=headers, data=data, files=files)
            
            if response.status_code == 201:
                result = response.json()
                pin_id = result.get("id")
                self.log_action("Video pin created", {"pin_id": pin_id})
                return pin_id
            else:
                self.log_action("Failed to create video pin", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error creating video pin: {e}")
            return None
        finally:
            # Close file if it was opened
            try:
                files['video_file'].close()
            except:
                pass
    
    def _get_default_board(self) -> str:
        """Get user's default board or first available board"""
        try:
            url = f"{self.api_base}/boards"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                boards = result.get("items", [])
                
                if boards:
                    # Return first board ID
                    return boards[0].get("id")
                else:
                    logger.warning("No boards found for user")
                    return None
            else:
                logger.error(f"Failed to get boards: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting boards: {e}")
            return None
    
    def schedule_video(self, content: VideoContent, scheduled_time: str) -> PostResult:
        """Pinterest doesn't support scheduling via API"""
        return PostResult(
            platform=self.platform_name,
            status=PostStatus.FAILED,
            message="Pinterest doesn't support native scheduling. Use posting manager queue or Pinterest Business tools."
        )
    
    def get_post_status(self, post_id: str) -> PostStatus:
        """Get pin status"""
        try:
            url = f"{self.api_base}/pins/{post_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
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
        """Delete a pin"""
        try:
            url = f"{self.api_base}/pins/{post_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                self.log_action("Pin deleted", {"pin_id": post_id})
                return True
            else:
                self.log_action("Failed to delete pin", 
                              {"pin_id": post_id, "status": response.status_code})
                return False
                
        except Exception as e:
            logger.error(f"Error deleting pin: {e}")
            return False
    
    def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get pin analytics"""
        try:
            # Pinterest analytics require business account
            url = f"{self.api_base}/pins/{post_id}/analytics"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "start_date": "2024-01-01",  # Would be dynamic
                "end_date": "2024-12-31",
                "metric_types": "IMPRESSION,SAVE,PIN_CLICK,OUTBOUND_CLICK"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get analytics: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information"""
        return {
            "note": "Pinterest has rate limits but doesn't expose them in headers",
            "recommendation": "Stay under 10 requests per minute for content creation",
            "daily_pins": "Limit to 50-100 pins per day for best engagement"
        }
    
    def validate_content(self, content: VideoContent) -> List[str]:
        """Validate content for Pinterest"""
        errors = super().validate_content(content)
        
        # Pinterest specific validations
        if len(content.title) > 100:
            errors.append("Title too long (max 100 characters)")
            
        if len(content.description) > 500:
            errors.append("Description too long (max 500 characters)")
            
        # Video requirements
        if content.duration and content.duration > 60:
            errors.append("Video should be under 60 seconds for best performance")
            
        # Pinterest prefers vertical content
        if content.aspect_ratio and content.aspect_ratio not in ["9:16", "2:3", "1:1"]:
            errors.append("Pinterest prefers vertical or square videos (9:16, 2:3, or 1:1)")
            
        return errors
    
    def format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for Pinterest"""
        # Pinterest hashtags should be more descriptive and specific
        formatted_hashtags = []
        
        for tag in hashtags:
            # Pinterest likes longer, more descriptive hashtags
            if len(tag) < 3:
                continue  # Skip very short hashtags
                
            # Convert to Pinterest style (more descriptive)
            pinterest_tag = tag.lower().replace(' ', '')
            formatted_hashtags.append(f'#{pinterest_tag}')
        
        return ' '.join(formatted_hashtags)
    
    def get_content_suggestions(self) -> Dict[str, List[str]]:
        """Get Pinterest-specific content suggestions for caregivers"""
        return {
            "board_ideas": [
                "Caregiver Self-Care Tips",
                "Elder Care Resources", 
                "Family Caregiving",
                "Caregiver Support",
                "Healthy Aging",
                "Memory Care Activities",
                "Caregiver Wellness"
            ],
            "popular_hashtags": [
                "#caregiver",
                "#eldercare", 
                "#familycaregiving",
                "#caregiversupport",
                "#dementia",
                "#alzheimers",
                "#seniorcare",
                "#caregivertips",
                "#caregiverselfcare",
                "#agingparents"
            ],
            "content_types": [
                "Infographic tips",
                "Quote cards",
                "Step-by-step guides",
                "Emotional support content",
                "Resource lists",
                "Self-care reminders"
            ]
        }