"""
LinkedIn adapter for B2B caregiver content.
Note: LinkedIn's video API has restrictions and requires approval for some features.
"""

import requests
import time
from typing import Dict, Any, List
from .base_adapter import BaseSocialAdapter, PostResult, PostStatus, VideoContent
import logging

logger = logging.getLogger(__name__)

class LinkedInAdapter(BaseSocialAdapter):
    """LinkedIn posting for professional caregiver content"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__("linkedin", credentials)
        self.access_token = credentials.get("access_token")
        self.person_id = credentials.get("person_id")  # User's LinkedIn ID
        self.organization_id = credentials.get("organization_id")  # Optional: for company pages
        self.api_base = "https://api.linkedin.com/v2"
        
    def authenticate(self) -> bool:
        """Authenticate with LinkedIn API"""
        try:
            url = f"{self.api_base}/people/~"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.authenticated = True
                profile_data = response.json()
                self.log_action("Authentication successful", 
                              {"user_id": profile_data.get("id")})
                return True
            else:
                self.log_action("Authentication failed", 
                              {"status": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn authentication error: {e}")
            return False
    
    def upload_video(self, content: VideoContent) -> PostResult:
        """Upload video to LinkedIn"""
        try:
            validation_errors = self.validate_content(content)
            if validation_errors:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message=f"Validation errors: {', '.join(validation_errors)}"
                )
            
            # Step 1: Register upload
            upload_info = self._register_upload()
            if not upload_info:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to register upload"
                )
            
            # Step 2: Upload video file
            if not self._upload_video_file(upload_info, content.file_path):
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to upload video file"
                )
            
            # Step 3: Create post
            post_id = self._create_post(upload_info["asset_id"], content)
            if post_id:
                return PostResult(
                    platform=self.platform_name,
                    post_id=post_id,
                    status=PostStatus.PUBLISHED,
                    message="Successfully posted to LinkedIn",
                    url=f"https://www.linkedin.com/feed/update/{post_id}/"
                )
            else:
                return PostResult(
                    platform=self.platform_name,
                    status=PostStatus.FAILED,
                    message="Failed to create post"
                )
                
        except Exception as e:
            logger.error(f"LinkedIn upload error: {e}")
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message=f"Upload error: {str(e)}"
            )
    
    def _register_upload(self) -> Dict[str, Any]:
        """Register video upload with LinkedIn"""
        try:
            url = f"{self.api_base}/assets"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Use person or organization as owner
            owner = f"urn:li:person:{self.person_id}"
            if self.organization_id:
                owner = f"urn:li:organization:{self.organization_id}"
            
            data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                    "owner": owner,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                asset_id = result.get("value", {}).get("asset")
                upload_mechanism = result.get("value", {}).get("uploadMechanism")
                upload_url = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
                
                self.log_action("Upload registered", {"asset_id": asset_id})
                
                return {
                    "asset_id": asset_id,
                    "upload_url": upload_url
                }
            else:
                self.log_action("Failed to register upload", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error registering upload: {e}")
            return None
    
    def _upload_video_file(self, upload_info: Dict[str, Any], file_path: str) -> bool:
        """Upload video file to LinkedIn's servers"""
        try:
            upload_url = upload_info["upload_url"]
            
            with open(file_path, 'rb') as video_file:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/octet-stream"
                }
                
                response = requests.put(upload_url, headers=headers, data=video_file)
                
                if response.status_code == 201:
                    self.log_action("Video file uploaded", {"asset_id": upload_info["asset_id"]})
                    return True
                else:
                    self.log_action("Failed to upload video file", 
                                  {"status": response.status_code, "response": response.text})
                    return False
                    
        except Exception as e:
            logger.error(f"Error uploading video file: {e}")
            return False
    
    def _create_post(self, asset_id: str, content: VideoContent) -> str:
        """Create LinkedIn post with video"""
        try:
            url = f"{self.api_base}/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Format text for LinkedIn (more professional tone)
            text = content.description
            if content.hashtags:
                # LinkedIn hashtags are more selective - use fewer, more relevant ones
                professional_hashtags = [tag for tag in content.hashtags 
                                       if tag.lower() in ['caregiver', 'caregiving', 'healthcare', 
                                                        'eldercare', 'familycare', 'mentalhealth']]
                if professional_hashtags:
                    text += "\n\n" + ' '.join(f'#{tag}' for tag in professional_hashtags[:5])
            
            # Use person or organization as author
            author = f"urn:li:person:{self.person_id}"
            if self.organization_id:
                author = f"urn:li:organization:{self.organization_id}"
            
            data = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "VIDEO",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": content.title
                                },
                                "media": asset_id,
                                "title": {
                                    "text": content.title
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                result = response.json()
                post_id = result.get("id")
                self.log_action("Post created", {"post_id": post_id})
                return post_id
            else:
                self.log_action("Failed to create post", 
                              {"status": response.status_code, "response": response.text})
                return None
                
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return None
    
    def schedule_video(self, content: VideoContent, scheduled_time: str) -> PostResult:
        """LinkedIn doesn't support scheduling via API"""
        return PostResult(
            platform=self.platform_name,
            status=PostStatus.FAILED,
            message="LinkedIn doesn't support native scheduling. Use posting manager queue or LinkedIn's web interface."
        )
    
    def get_post_status(self, post_id: str) -> PostStatus:
        """Get post status"""
        try:
            url = f"{self.api_base}/ugcPosts/{post_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                lifecycle_state = result.get("lifecycleState")
                
                if lifecycle_state == "PUBLISHED":
                    return PostStatus.PUBLISHED
                elif lifecycle_state == "DRAFT":
                    return PostStatus.SCHEDULED
                else:
                    return PostStatus.PROCESSING
            else:
                return PostStatus.FAILED
                
        except Exception as e:
            logger.error(f"Error getting post status: {e}")
            return PostStatus.FAILED
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post"""
        try:
            url = f"{self.api_base}/ugcPosts/{post_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
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
            # LinkedIn analytics require additional permissions
            url = f"{self.api_base}/socialActions/{post_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Basic metrics - full analytics require LinkedIn Marketing API
                return {
                    "note": "Full analytics require LinkedIn Marketing API access",
                    "status": "available_via_marketing_api"
                }
            else:
                return {"error": f"Failed to get analytics: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get rate limit information"""
        return {
            "note": "LinkedIn uses throttling rather than hard limits",
            "recommendation": "Space posts 15+ minutes apart",
            "daily_limit": "Approximately 100 API calls per day for most endpoints"
        }
    
    def validate_content(self, content: VideoContent) -> List[str]:
        """Validate content for LinkedIn"""
        errors = super().validate_content(content)
        
        # LinkedIn specific validations
        if len(content.description) > 3000:
            errors.append("Text too long (max 3000 characters)")
            
        # Video requirements
        if content.duration and content.duration > 600:  # 10 minutes
            errors.append("Video too long (max 10 minutes)")
            
        # Professional content guidelines
        unprofessional_words = ['crazy', 'insane', 'stupid', 'dumb']
        text_lower = content.description.lower()
        found_unprofessional = [word for word in unprofessional_words if word in text_lower]
        if found_unprofessional:
            errors.append(f"Consider more professional language. Found: {', '.join(found_unprofessional)}")
            
        return errors
    
    def format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for LinkedIn (more selective)"""
        # LinkedIn works better with fewer, more relevant hashtags
        professional_hashtags = []
        for tag in hashtags[:5]:  # Max 5 hashtags for LinkedIn
            if any(keyword in tag.lower() for keyword in 
                   ['caregiver', 'care', 'health', 'elder', 'family', 'support']):
                professional_hashtags.append(tag)
        
        return ' '.join(f'#{tag}' for tag in professional_hashtags)