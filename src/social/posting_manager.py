"""
Unified Posting Manager - Central hub for all social media posting.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
from pathlib import Path

from .base_adapter import BaseSocialAdapter, PostResult, PostStatus, VideoContent
from .instagram_adapter import InstagramAdapter
from .tiktok_adapter import TikTokAdapter
from .youtube_adapter import YouTubeAdapter
from .twitter_adapter import TwitterAdapter
from .linkedin_adapter import LinkedInAdapter
from .pinterest_adapter import PinterestAdapter
from .facebook_adapter import FacebookAdapter

logger = logging.getLogger(__name__)

@dataclass
class PostJob:
    """A posting job in the queue"""
    id: str
    platform: str
    content: VideoContent
    scheduled_time: Optional[datetime] = None
    status: PostStatus = PostStatus.QUEUED
    created_at: datetime = None
    attempts: int = 0
    max_attempts: int = 3
    result: Optional[PostResult] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class PostingManager:
    """Unified manager for all social media posting"""
    
    def __init__(self, config_path: str = "config/social_credentials.json"):
        self.config_path = config_path
        self.adapters: Dict[str, BaseSocialAdapter] = {}
        self.queue: List[PostJob] = []
        self.db_path = "data/posting_manager.db"
        self.running = False
        self.worker_thread = None
        
        # Initialize database
        self._init_database()
        
        # Load adapters
        self._load_adapters()
        
        # Load existing jobs from database
        self._load_jobs()
    
    def _init_database(self):
        """Initialize SQLite database for job persistence"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS post_jobs (
                    id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    content_json TEXT NOT NULL,
                    scheduled_time TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    result_json TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS post_analytics (
                    post_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    analytics_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
    
    def _load_adapters(self):
        """Load and authenticate social media adapters"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            adapter_classes = {
                'instagram': InstagramAdapter,
                'tiktok': TikTokAdapter,
                'youtube': YouTubeAdapter,
                'twitter': TwitterAdapter,
                'linkedin': LinkedInAdapter,
                'pinterest': PinterestAdapter,
                'facebook': FacebookAdapter
            }
            
            for platform, credentials in config.items():
                if platform in adapter_classes and credentials.get('enabled', False):
                    try:
                        adapter = adapter_classes[platform](credentials)
                        if adapter.authenticate():
                            self.adapters[platform] = adapter
                            logger.info(f"Successfully loaded {platform} adapter")
                        else:
                            logger.warning(f"Failed to authenticate {platform} adapter")
                    except Exception as e:
                        logger.error(f"Error loading {platform} adapter: {e}")
                        
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading adapters: {e}")
    
    def _load_jobs(self):
        """Load pending jobs from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM post_jobs 
                WHERE status IN ('queued', 'processing', 'scheduled')
                ORDER BY created_at ASC
            """)
            
            for row in cursor.fetchall():
                try:
                    job = self._row_to_job(row)
                    self.queue.append(job)
                except Exception as e:
                    logger.error(f"Error loading job {row[0]}: {e}")
    
    def _row_to_job(self, row) -> PostJob:
        """Convert database row to PostJob"""
        content_data = json.loads(row[2])
        content = VideoContent(**content_data)
        
        scheduled_time = None
        if row[3]:
            scheduled_time = datetime.fromisoformat(row[3])
        
        result = None
        if row[8]:
            result_data = json.loads(row[8])
            result = PostResult(**result_data)
        
        return PostJob(
            id=row[0],
            platform=row[1],
            content=content,
            scheduled_time=scheduled_time,
            status=PostStatus(row[4]),
            created_at=datetime.fromisoformat(row[5]),
            attempts=row[6],
            max_attempts=row[7],
            result=result
        )
    
    def _save_job(self, job: PostJob):
        """Save job to database"""
        with sqlite3.connect(self.db_path) as conn:
            content_json = json.dumps(asdict(job.content))
            scheduled_time_str = job.scheduled_time.isoformat() if job.scheduled_time else None
            result_json = json.dumps(asdict(job.result)) if job.result else None
            
            conn.execute("""
                INSERT OR REPLACE INTO post_jobs 
                (id, platform, content_json, scheduled_time, status, created_at, attempts, max_attempts, result_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id, job.platform, content_json, scheduled_time_str,
                job.status.value, job.created_at.isoformat(),
                job.attempts, job.max_attempts, result_json
            ))
    
    def queue_post(self, platform: str, content: VideoContent, scheduled_time: Optional[datetime] = None) -> str:
        """Queue a post for publishing"""
        import uuid
        job_id = str(uuid.uuid4())
        
        job = PostJob(
            id=job_id,
            platform=platform,
            content=content,
            scheduled_time=scheduled_time
        )
        
        self.queue.append(job)
        self._save_job(job)
        
        logger.info(f"Queued post {job_id} for {platform}")
        return job_id
    
    def queue_bulk_post(self, platforms: List[str], content: VideoContent, 
                       scheduled_time: Optional[datetime] = None, 
                       delay_between_posts: int = 300) -> List[str]:
        """Queue the same content to multiple platforms with optional delays"""
        job_ids = []
        current_time = scheduled_time or datetime.now()
        
        for i, platform in enumerate(platforms):
            # Add delay between posts to avoid rate limiting
            post_time = current_time + timedelta(seconds=i * delay_between_posts)
            job_id = self.queue_post(platform, content, post_time)
            job_ids.append(job_id)
        
        logger.info(f"Queued bulk post to {len(platforms)} platforms")
        return job_ids
    
    def cancel_post(self, job_id: str) -> bool:
        """Cancel a queued post"""
        for job in self.queue:
            if job.id == job_id and job.status in [PostStatus.QUEUED, PostStatus.SCHEDULED]:
                job.status = PostStatus.FAILED
                job.result = PostResult(
                    platform=job.platform,
                    status=PostStatus.FAILED,
                    message="Cancelled by user"
                )
                self._save_job(job)
                logger.info(f"Cancelled post {job_id}")
                return True
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        status_counts = {}
        for status in PostStatus:
            status_counts[status.value] = len([job for job in self.queue if job.status == status])
        
        return {
            "total_jobs": len(self.queue),
            "by_status": status_counts,
            "active_platforms": list(self.adapters.keys()),
            "next_scheduled": self._get_next_scheduled_time()
        }
    
    def _get_next_scheduled_time(self) -> Optional[str]:
        """Get the next scheduled post time"""
        scheduled_jobs = [job for job in self.queue 
                         if job.scheduled_time and job.status in [PostStatus.QUEUED, PostStatus.SCHEDULED]]
        
        if scheduled_jobs:
            next_job = min(scheduled_jobs, key=lambda x: x.scheduled_time)
            return next_job.scheduled_time.isoformat()
        return None
    
    def start_processing(self):
        """Start the background processing thread"""
        if self.running:
            logger.warning("Processing already running")
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        logger.info("Started posting manager processing")
    
    def stop_processing(self):
        """Stop the background processing"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=10)
        logger.info("Stopped posting manager processing")
    
    def _process_queue(self):
        """Background worker to process the posting queue"""
        while self.running:
            try:
                # Process ready jobs
                ready_jobs = [job for job in self.queue 
                             if self._is_job_ready(job) and job.status == PostStatus.QUEUED]
                
                for job in ready_jobs:
                    if not self.running:
                        break
                    
                    self._process_job(job)
                
                # Clean up old completed jobs
                self._cleanup_old_jobs()
                
                # Sleep before next iteration
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(60)  # Longer sleep on error
    
    def _is_job_ready(self, job: PostJob) -> bool:
        """Check if a job is ready to be processed"""
        if job.status != PostStatus.QUEUED:
            return False
        
        if job.scheduled_time and job.scheduled_time > datetime.now():
            return False
        
        if job.platform not in self.adapters:
            return False
        
        # Check rate limiting
        adapter = self.adapters[job.platform]
        if adapter.handle_rate_limit():
            return False
        
        return True
    
    def _process_job(self, job: PostJob):
        """Process a single posting job"""
        try:
            job.status = PostStatus.UPLOADING
            job.attempts += 1
            self._save_job(job)
            
            logger.info(f"Processing job {job.id} for {job.platform} (attempt {job.attempts})")
            
            adapter = self.adapters[job.platform]
            
            # Try to post
            if job.scheduled_time and job.scheduled_time > datetime.now():
                # Use platform scheduling if available
                result = adapter.schedule_video(job.content, job.scheduled_time.isoformat())
            else:
                # Post immediately
                result = adapter.upload_video(job.content)
            
            job.result = result
            job.status = result.status
            
            if result.status == PostStatus.PUBLISHED:
                logger.info(f"Successfully posted {job.id} to {job.platform}: {result.url}")
            elif result.status == PostStatus.SCHEDULED:
                logger.info(f"Successfully scheduled {job.id} for {job.platform}")
            else:
                logger.warning(f"Failed to post {job.id} to {job.platform}: {result.message}")
                
                # Retry logic
                if job.attempts < job.max_attempts and result.status == PostStatus.FAILED:
                    job.status = PostStatus.QUEUED  # Retry later
                    # Add exponential backoff
                    retry_delay = min(300 * (2 ** (job.attempts - 1)), 3600)  # Max 1 hour
                    job.scheduled_time = datetime.now() + timedelta(seconds=retry_delay)
                    logger.info(f"Will retry {job.id} in {retry_delay} seconds")
            
            self._save_job(job)
            
        except Exception as e:
            logger.error(f"Error processing job {job.id}: {e}")
            job.status = PostStatus.FAILED
            job.result = PostResult(
                platform=job.platform,
                status=PostStatus.FAILED,
                message=f"Processing error: {str(e)}"
            )
            self._save_job(job)
    
    def _cleanup_old_jobs(self):
        """Remove old completed jobs from queue"""
        cutoff_time = datetime.now() - timedelta(days=7)  # Keep jobs for 7 days
        
        jobs_to_remove = [
            job for job in self.queue
            if job.status in [PostStatus.PUBLISHED, PostStatus.FAILED, PostStatus.DELETED]
            and job.created_at < cutoff_time
        ]
        
        for job in jobs_to_remove:
            self.queue.remove(job)
        
        if jobs_to_remove:
            logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
    
    def get_job_status(self, job_id: str) -> Optional[PostJob]:
        """Get status of a specific job"""
        for job in self.queue:
            if job.id == job_id:
                return job
        return None
    
    def get_recent_posts(self, platform: Optional[str] = None, limit: int = 50) -> List[PostJob]:
        """Get recent posts, optionally filtered by platform"""
        jobs = [job for job in self.queue 
                if job.status in [PostStatus.PUBLISHED, PostStatus.SCHEDULED]]
        
        if platform:
            jobs = [job for job in jobs if job.platform == platform]
        
        # Sort by creation time, most recent first
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        
        return jobs[:limit]
    
    def collect_analytics(self) -> Dict[str, Any]:
        """Collect analytics from all published posts"""
        analytics = {}
        
        published_jobs = [job for job in self.queue 
                         if job.status == PostStatus.PUBLISHED and job.result and job.result.post_id]
        
        for job in published_jobs:
            try:
                if job.platform in self.adapters:
                    adapter = self.adapters[job.platform]
                    post_analytics = adapter.get_analytics(job.result.post_id)
                    
                    if job.platform not in analytics:
                        analytics[job.platform] = []
                    
                    analytics[job.platform].append({
                        "job_id": job.id,
                        "post_id": job.result.post_id,
                        "url": job.result.url,
                        "created_at": job.created_at.isoformat(),
                        "analytics": post_analytics
                    })
                    
                    # Save to database
                    self._save_analytics(job.result.post_id, job.platform, post_analytics)
                    
            except Exception as e:
                logger.error(f"Error collecting analytics for {job.id}: {e}")
        
        return analytics
    
    def _save_analytics(self, post_id: str, platform: str, analytics_data: Dict[str, Any]):
        """Save analytics data to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO post_analytics 
                (post_id, platform, analytics_json, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                post_id, platform, 
                json.dumps(analytics_data), 
                datetime.now().isoformat()
            ))
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        total_posts = len([job for job in self.queue if job.status == PostStatus.PUBLISHED])
        failed_posts = len([job for job in self.queue if job.status == PostStatus.FAILED])
        
        platform_stats = {}
        for platform in self.adapters.keys():
            platform_jobs = [job for job in self.queue if job.platform == platform]
            platform_stats[platform] = {
                "total": len(platform_jobs),
                "published": len([job for job in platform_jobs if job.status == PostStatus.PUBLISHED]),
                "failed": len([job for job in platform_jobs if job.status == PostStatus.FAILED]),
                "queued": len([job for job in platform_jobs if job.status == PostStatus.QUEUED])
            }
        
        return {
            "total_posts": total_posts,
            "failed_posts": failed_posts,
            "success_rate": (total_posts / (total_posts + failed_posts) * 100) if (total_posts + failed_posts) > 0 else 0,
            "platform_stats": platform_stats,
            "active_platforms": len(self.adapters)
        }