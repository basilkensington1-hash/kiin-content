"""
Base adapter class for social media platforms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PostStatus(Enum):
    QUEUED = "queued"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"

@dataclass
class PostResult:
    """Result of a posting operation"""
    platform: str
    post_id: Optional[str] = None
    status: PostStatus = PostStatus.FAILED
    message: str = ""
    url: Optional[str] = None
    scheduled_time: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class VideoContent:
    """Video content data"""
    file_path: str
    title: str
    description: str
    hashtags: List[str]
    mentions: List[str] = None
    thumbnail_path: Optional[str] = None
    duration: Optional[float] = None
    aspect_ratio: Optional[str] = None  # "9:16", "1:1", "16:9"
    
    def __post_init__(self):
        if self.mentions is None:
            self.mentions = []

class BaseSocialAdapter(ABC):
    """Base class for all social media platform adapters"""
    
    def __init__(self, platform_name: str, credentials: Dict[str, Any]):
        self.platform_name = platform_name
        self.credentials = credentials
        self.authenticated = False
        self.rate_limit_remaining = 0
        self.rate_limit_reset = None
        
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    def upload_video(self, content: VideoContent) -> PostResult:
        """Upload video content immediately"""
        pass
    
    @abstractmethod
    def schedule_video(self, content: VideoContent, scheduled_time: str) -> PostResult:
        """Schedule video for future posting"""
        pass
    
    @abstractmethod
    def get_post_status(self, post_id: str) -> PostStatus:
        """Get the current status of a post"""
        pass
    
    @abstractmethod
    def delete_post(self, post_id: str) -> bool:
        """Delete a post"""
        pass
    
    @abstractmethod
    def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics data for a post"""
        pass
    
    @abstractmethod
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        pass
    
    def format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for this platform (can be overridden)"""
        return ' '.join(f'#{tag}' for tag in hashtags)
    
    def format_mentions(self, mentions: List[str]) -> str:
        """Format mentions for this platform (can be overridden)"""
        return ' '.join(f'@{mention}' for mention in mentions)
    
    def validate_content(self, content: VideoContent) -> List[str]:
        """Validate content for this platform (can be overridden)"""
        errors = []
        
        if not content.file_path:
            errors.append("Video file path is required")
            
        if not content.title:
            errors.append("Title is required")
            
        return errors
    
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log platform actions for debugging"""
        details = details or {}
        logger.info(f"[{self.platform_name}] {action}: {details}")
        
    def handle_rate_limit(self) -> bool:
        """Handle rate limiting (return True if should retry later)"""
        if self.rate_limit_remaining <= 0:
            logger.warning(f"[{self.platform_name}] Rate limit reached. Reset at: {self.rate_limit_reset}")
            return True
        return False