# Security Best Practices - Kiin Social Media Integration

## 🔒 Overview

This document outlines security best practices for the Kiin Content Factory social media integration system. Follow these guidelines to protect your API credentials, user data, and maintain compliance with platform terms of service.

## 🗝️ API Credential Security

### 1. Credential Storage

**❌ Never Do:**
```json
// DON'T commit real credentials to version control
{
  "instagram": {
    "access_token": "EAABwzLixnjYBAB123456789..."
  }
}
```

**✅ Best Practice:**
```bash
# Use environment variables in production
export INSTAGRAM_ACCESS_TOKEN="your_token_here"
export YOUTUBE_CLIENT_SECRET="your_secret_here"

# Or use a secure credential management system
```

### 2. File Permissions
```bash
# Set restrictive permissions on credential files
chmod 600 config/social_credentials.json  # Owner read/write only
chmod 700 config/                         # Owner access only

# Verify permissions
ls -la config/social_credentials.json
# Should show: -rw------- (600)
```

### 3. Gitignore Configuration
```bash
# Add to .gitignore
echo "config/social_credentials.json" >> .gitignore
echo "data/*.db" >> .gitignore
echo "temp/" >> .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
```

### 4. Environment Variables
```python
# Use environment variables in production
import os
from pathlib import Path

def load_secure_credentials():
    return {
        "instagram": {
            "enabled": True,
            "access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            "instagram_account_id": os.getenv("INSTAGRAM_ACCOUNT_ID")
        },
        "youtube": {
            "enabled": True,
            "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
            "access_token": os.getenv("YOUTUBE_ACCESS_TOKEN"),
            "refresh_token": os.getenv("YOUTUBE_REFRESH_TOKEN")
        }
    }
```

## 🛡️ Access Control

### 1. Database Security
```python
import sqlite3
import os

def secure_db_setup():
    db_path = "data/posting_manager.db"
    
    # Ensure data directory exists with proper permissions
    os.makedirs("data", mode=0o700, exist_ok=True)
    
    # Set database file permissions
    if os.path.exists(db_path):
        os.chmod(db_path, 0o600)
    
    # Use connection with timeout to prevent hanging
    conn = sqlite3.connect(db_path, timeout=10.0)
    return conn
```

### 2. Input Validation
```python
def validate_video_content(content: VideoContent) -> List[str]:
    """Validate and sanitize video content"""
    errors = []
    
    # File path validation
    if not content.file_path or ".." in content.file_path:
        errors.append("Invalid file path")
    
    # Check file exists and is readable
    if not os.path.exists(content.file_path):
        errors.append("Video file not found")
    
    # Validate file type
    allowed_extensions = ['.mp4', '.mov', '.avi']
    if not any(content.file_path.lower().endswith(ext) for ext in allowed_extensions):
        errors.append("Invalid video format")
    
    # Sanitize text fields
    content.title = sanitize_text(content.title)
    content.description = sanitize_text(content.description)
    
    return errors

def sanitize_text(text: str) -> str:
    """Remove potentially harmful characters"""
    import re
    # Remove control characters and normalize whitespace
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()
```

### 3. Rate Limiting Protection
```python
class SecureAdapter(BaseSocialAdapter):
    def __init__(self, platform_name: str, credentials: Dict[str, Any]):
        super().__init__(platform_name, credentials)
        self.rate_limiter = RateLimiter(max_calls=100, time_window=3600)
        self.suspicious_activity_threshold = 10
        self.failed_attempts = 0
    
    def upload_video(self, content: VideoContent) -> PostResult:
        # Check rate limits
        if not self.rate_limiter.allow_request():
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message="Rate limit exceeded"
            )
        
        # Monitor for suspicious activity
        if self.failed_attempts >= self.suspicious_activity_threshold:
            logger.warning(f"Suspicious activity detected for {self.platform_name}")
            return PostResult(
                platform=self.platform_name,
                status=PostStatus.FAILED,
                message="Account temporarily locked due to suspicious activity"
            )
        
        try:
            result = self._upload_video_impl(content)
            if result.status == PostStatus.FAILED:
                self.failed_attempts += 1
            else:
                self.failed_attempts = 0  # Reset on success
            return result
        except Exception as e:
            self.failed_attempts += 1
            raise e
```

## 🔍 Monitoring & Logging

### 1. Secure Logging
```python
import logging
import logging.handlers
from pathlib import Path

def setup_secure_logging():
    # Create logs directory with restricted permissions
    log_dir = Path("logs")
    log_dir.mkdir(mode=0o700, exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger("social_media")
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/social_media.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Secure formatter (don't log sensitive data)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_action_securely(platform: str, action: str, details: Dict[str, Any]):
    """Log actions without exposing sensitive data"""
    # Remove sensitive fields
    safe_details = {k: v for k, v in details.items() 
                    if k not in ['access_token', 'password', 'secret']}
    
    # Truncate long values
    for key, value in safe_details.items():
        if isinstance(value, str) and len(value) > 100:
            safe_details[key] = value[:97] + "..."
    
    logger.info(f"[{platform}] {action}: {safe_details}")
```

### 2. Audit Trail
```python
def create_audit_log(action: str, platform: str, user_id: str, 
                    success: bool, details: str = ""):
    """Create audit trail for all actions"""
    with sqlite3.connect("data/audit.db") as conn:
        conn.execute("""
            INSERT INTO audit_log 
            (timestamp, action, platform, user_id, success, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            action,
            platform,
            user_id,
            success,
            details
        ))
```

## 🔐 Data Protection

### 1. Data Encryption
```python
from cryptography.fernet import Fernet
import base64

class CredentialManager:
    def __init__(self, key_file: str = ".credential_key"):
        self.key_file = key_file
        self._ensure_key_exists()
        
    def _ensure_key_exists(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)
    
    def _get_cipher(self):
        with open(self.key_file, 'rb') as f:
            key = f.read()
        return Fernet(key)
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> bytes:
        cipher = self._get_cipher()
        return cipher.encrypt(json.dumps(credentials).encode())
    
    def decrypt_credentials(self, encrypted_data: bytes) -> Dict[str, Any]:
        cipher = self._get_cipher()
        decrypted = cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
```

### 2. Temporary File Security
```python
import tempfile
import shutil

class SecureFileHandler:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kiin_secure_")
        os.chmod(self.temp_dir, 0o700)
    
    def create_temp_file(self, suffix: str = ".tmp") -> str:
        fd, path = tempfile.mkstemp(dir=self.temp_dir, suffix=suffix)
        os.close(fd)
        os.chmod(path, 0o600)
        return path
    
    def cleanup(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def __del__(self):
        self.cleanup()
```

## 🚨 Error Handling

### 1. Secure Error Messages
```python
def handle_api_error(exception: Exception, platform: str) -> str:
    """Handle API errors without exposing sensitive information"""
    
    # Log full error details securely
    logger.error(f"API error for {platform}", exc_info=True)
    
    # Return sanitized error message to user
    error_messages = {
        "authentication_failed": "Authentication failed. Please check your credentials.",
        "rate_limit_exceeded": "Rate limit exceeded. Please try again later.",
        "invalid_content": "Content validation failed. Please check your video file.",
        "network_error": "Network error. Please check your connection.",
        "server_error": "Server error. Please try again later."
    }
    
    # Map exception types to user-friendly messages
    if "401" in str(exception) or "authentication" in str(exception).lower():
        return error_messages["authentication_failed"]
    elif "429" in str(exception) or "rate limit" in str(exception).lower():
        return error_messages["rate_limit_exceeded"]
    elif "400" in str(exception):
        return error_messages["invalid_content"]
    else:
        return error_messages["server_error"]
```

### 2. Graceful Degradation
```python
def safe_api_call(func, *args, **kwargs):
    """Wrapper for safe API calls with retry logic"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, log and raise
                logger.error(f"API call failed after {max_retries} attempts: {e}")
                raise
            else:
                # Retry with exponential backoff
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"API call failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
```

## ✅ Compliance Checklist

### Platform API Compliance
- [ ] Review and accept all platform Terms of Service
- [ ] Implement proper attribution for automated content
- [ ] Respect rate limits and quotas
- [ ] Handle user consent for cross-platform posting
- [ ] Implement proper error handling and retries

### Data Protection (GDPR/CCPA)
- [ ] Obtain explicit consent for data processing
- [ ] Provide data deletion capabilities
- [ ] Implement data minimization practices
- [ ] Maintain audit logs for data access
- [ ] Encrypt sensitive data at rest and in transit

### Content Security
- [ ] Validate all user-uploaded content
- [ ] Scan for malicious files
- [ ] Implement content filtering
- [ ] Respect copyright and intellectual property
- [ ] Maintain content approval workflows

## 🔧 Security Configuration

### Production Environment Setup
```bash
#!/bin/bash
# Production security setup script

# Create secure directories
mkdir -p /app/data /app/logs /app/temp
chmod 700 /app/data /app/logs /app/temp

# Set up logging
touch /app/logs/security.log
chmod 600 /app/logs/security.log

# Install security updates
apt update && apt upgrade -y

# Configure firewall (if needed)
ufw enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh

# Set up fail2ban for rate limiting
apt install fail2ban -y
```

### Environment Variables Template
```bash
# .env file template (never commit this file)
export INSTAGRAM_ACCESS_TOKEN="your_token"
export INSTAGRAM_ACCOUNT_ID="your_id"
export YOUTUBE_CLIENT_ID="your_client_id"
export YOUTUBE_CLIENT_SECRET="your_client_secret"
export YOUTUBE_ACCESS_TOKEN="your_access_token"
export YOUTUBE_REFRESH_TOKEN="your_refresh_token"
export TWITTER_BEARER_TOKEN="your_bearer_token"
export ENCRYPTION_KEY_PATH="/secure/path/to/encryption.key"
export DATABASE_ENCRYPTION_ENABLED="true"
export LOG_LEVEL="INFO"
export SECURITY_AUDIT_ENABLED="true"
```

## 🚨 Incident Response

### Security Incident Checklist
1. **Immediate Response**
   - [ ] Identify the scope of the incident
   - [ ] Isolate affected systems
   - [ ] Revoke compromised credentials immediately
   - [ ] Document all actions taken

2. **Investigation**
   - [ ] Review audit logs for unauthorized access
   - [ ] Check for data exfiltration
   - [ ] Analyze attack vectors
   - [ ] Document findings

3. **Recovery**
   - [ ] Generate new API credentials
   - [ ] Update all affected configurations
   - [ ] Test system functionality
   - [ ] Monitor for continued suspicious activity

4. **Prevention**
   - [ ] Update security measures
   - [ ] Patch identified vulnerabilities
   - [ ] Update documentation
   - [ ] Conduct security training

### Emergency Contacts
```python
SECURITY_CONTACTS = {
    "security_team": "security@yourcompany.com",
    "platform_support": {
        "instagram": "https://business.facebook.com/support",
        "youtube": "https://support.google.com/youtube/",
        "twitter": "https://help.twitter.com/",
    }
}
```

## 📋 Regular Security Maintenance

### Weekly Tasks
- [ ] Review access logs for suspicious activity
- [ ] Rotate temporary credentials
- [ ] Update security patches
- [ ] Clean up temporary files
- [ ] Test backup and recovery procedures

### Monthly Tasks  
- [ ] Review and update API credentials
- [ ] Audit user permissions
- [ ] Update security documentation
- [ ] Conduct security training
- [ ] Review platform policy changes

### Quarterly Tasks
- [ ] Security assessment and penetration testing
- [ ] Review and update incident response procedures
- [ ] Compliance audit
- [ ] Update security tools and dependencies

## 🛡️ Security Tools Integration

### Dependency Scanning
```bash
# Check for vulnerable dependencies
pip install safety
safety check

# Update requirements with security patches
pip-audit --fix
```

### Secret Scanning
```bash
# Scan for committed secrets
pip install detect-secrets
detect-secrets scan --all-files
```

### Code Quality
```bash
# Static code analysis for security issues
pip install bandit
bandit -r src/
```

---

## 📞 Security Support

For security issues or questions:
- Email: security@kiincontentfactory.com
- Emergency: Follow incident response procedures
- Documentation: Review this guide regularly

Remember: Security is everyone's responsibility. When in doubt, err on the side of caution and consult the security team.

---

**Last Updated:** January 2024  
**Review Schedule:** Quarterly  
**Next Review:** April 2024