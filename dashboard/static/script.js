// Kiin Content Factory Dashboard - Frontend JavaScript

class KiinDashboard {
    constructor() {
        this.activeGenerations = new Set();
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadRecentVideos();
        this.updateStats();
        this.startPeriodicUpdates();
    }

    bindEvents() {
        // Bind generate buttons
        document.querySelectorAll('.btn-generate').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const contentType = e.currentTarget.getAttribute('data-type');
                this.generateContent(contentType);
            });
        });

        // Auto-refresh every 30 seconds
        setInterval(() => this.updateStats(), 30000);
    }

    async generateContent(contentType) {
        if (this.activeGenerations.has(contentType)) {
            return; // Already generating
        }

        const button = document.querySelector(`[data-type="${contentType}"]`);
        const overlay = document.getElementById(`overlay-${contentType}`);
        const card = document.querySelector(`[data-type="${contentType}"]`).closest('.content-card');

        try {
            // Start generation
            this.activeGenerations.add(contentType);
            button.disabled = true;
            overlay.classList.add('active');

            this.showNotification(
                'Generation Started', 
                `Creating your ${this.getContentTitle(contentType)} video...`,
                'info'
            );

            const response = await fetch(`/api/generate/${contentType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(
                    'Video Generated!', 
                    `${result.message} File: ${result.filename}`,
                    'success'
                );
                
                // Update the preview
                this.updateVideoPreview(contentType, result.filename);
                
                // Refresh recent videos and stats
                this.loadRecentVideos();
                this.updateStats();

                // Add celebration animation
                this.celebrateSuccess(card);
                
            } else {
                this.showNotification(
                    'Generation Failed', 
                    result.error || 'Unknown error occurred',
                    'error'
                );
            }

        } catch (error) {
            console.error('Generation error:', error);
            this.showNotification(
                'Network Error', 
                'Could not connect to the server. Please try again.',
                'error'
            );
        } finally {
            // Clean up
            this.activeGenerations.delete(contentType);
            button.disabled = false;
            overlay.classList.remove('active');
        }
    }

    updateVideoPreview(contentType, filename) {
        const card = document.querySelector(`[data-type="${contentType}"]`).closest('.content-card');
        const previewArea = card.querySelector('.card-preview');
        
        previewArea.innerHTML = `
            <div class="preview-item">
                <i class="fas fa-video"></i>
                <span class="preview-name">${filename}</span>
                <span class="preview-badge new">NEW</span>
            </div>
        `;

        // Remove "new" badge after 5 seconds
        setTimeout(() => {
            const badge = previewArea.querySelector('.preview-badge.new');
            if (badge) {
                badge.remove();
            }
        }, 5000);
    }

    celebrateSuccess(card) {
        // Add a subtle success animation
        card.style.transform = 'scale(1.02)';
        card.style.transition = 'transform 0.3s ease';
        
        setTimeout(() => {
            card.style.transform = '';
        }, 300);

        // Add confetti-like effect
        this.createSuccessParticles(card);
    }

    createSuccessParticles(element) {
        const rect = element.getBoundingClientRect();
        const colors = ['#4A90E2', '#50C878', '#7ED3C3', '#48BB78'];
        
        for (let i = 0; i < 12; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: fixed;
                width: 8px;
                height: 8px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                border-radius: 50%;
                pointer-events: none;
                z-index: 1000;
                left: ${rect.left + rect.width/2}px;
                top: ${rect.top + rect.height/2}px;
                animation: particle-${Math.random().toString(36).substr(2, 9)} 2s ease-out forwards;
            `;

            const angle = (Math.PI * 2 * i) / 12;
            const distance = 100 + Math.random() * 100;
            const endX = Math.cos(angle) * distance;
            const endY = Math.sin(angle) * distance;

            const keyframes = `
                @keyframes particle-${particle.style.animationName.split('-')[1]} {
                    to {
                        transform: translate(${endX}px, ${endY}px);
                        opacity: 0;
                        scale: 0;
                    }
                }
            `;

            const styleSheet = document.createElement('style');
            styleSheet.textContent = keyframes;
            document.head.appendChild(styleSheet);

            document.body.appendChild(particle);

            // Clean up
            setTimeout(() => {
                particle.remove();
                styleSheet.remove();
            }, 2000);
        }
    }

    async loadRecentVideos() {
        try {
            const response = await fetch('/api/videos');
            const videos = await response.json();

            const container = document.getElementById('recent-videos');
            
            if (videos.length === 0) {
                container.innerHTML = `
                    <div class="loading-placeholder">
                        <i class="fas fa-video"></i>
                        No videos generated yet. Create your first one above!
                    </div>
                `;
                return;
            }

            container.innerHTML = videos.map(video => {
                const date = new Date(video.created);
                const timeAgo = this.getTimeAgo(date);
                const sizeInMB = (video.size / (1024 * 1024)).toFixed(1);
                const typeInfo = this.getContentTypeInfo(video.type);

                return `
                    <div class="activity-item" data-video="${video.filename}">
                        <div class="activity-icon" style="background-color: ${typeInfo.color}">
                            <i class="fas fa-video"></i>
                        </div>
                        <div class="activity-details">
                            <div class="activity-title">${video.filename}</div>
                            <div class="activity-meta">
                                ${typeInfo.title} • ${sizeInMB} MB • ${timeAgo}
                            </div>
                        </div>
                        <div class="activity-actions">
                            <button class="btn-preview" onclick="dashboard.previewVideo('${video.filename}')">
                                <i class="fas fa-play"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');

        } catch (error) {
            console.error('Failed to load recent videos:', error);
            document.getElementById('recent-videos').innerHTML = `
                <div class="loading-placeholder">
                    <i class="fas fa-exclamation-triangle"></i>
                    Failed to load recent videos
                </div>
            `;
        }
    }

    async updateStats() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();

            // Update total videos count
            const totalVideos = Object.values(status).reduce((sum, type) => {
                return sum + (type.latest_video ? 1 : 0);
            }, 0);

            document.getElementById('total-videos').textContent = `${totalVideos} videos`;
            document.getElementById('last-updated').textContent = 'Just updated';

            // Update individual content cards
            Object.entries(status).forEach(([key, data]) => {
                const card = document.querySelector(`[data-type="${key}"]`).closest('.content-card');
                if (!card) return;

                const countElement = card.querySelector('.content-count');
                if (countElement) {
                    countElement.textContent = `${data.count} stories available`;
                }

                // Update preview if there's a latest video
                if (data.latest_video) {
                    const previewArea = card.querySelector('.card-preview');
                    if (!previewArea.querySelector('.preview-item')) {
                        previewArea.innerHTML = `
                            <div class="preview-item">
                                <i class="fas fa-video"></i>
                                <span class="preview-name">${data.latest_video}</span>
                            </div>
                        `;
                    }
                }
            });

        } catch (error) {
            console.error('Failed to update stats:', error);
        }
    }

    startPeriodicUpdates() {
        // Update recent videos every 2 minutes
        setInterval(() => this.loadRecentVideos(), 120000);
        
        // Update stats every minute
        setInterval(() => this.updateStats(), 60000);
    }

    previewVideo(filename) {
        // This would ideally open a modal or new window with video preview
        const videoPath = `/Users/nick/clawd/kiin-content/output/${filename}`;
        this.showNotification(
            'Video Location', 
            `Video saved at: ${videoPath}`,
            'info'
        );
    }

    showNotification(title, message, type = 'info') {
        const container = document.getElementById('notifications');
        const notification = document.createElement('div');
        
        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };

        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon ${iconMap[type]}"></i>
                <div class="notification-text">
                    <div class="notification-title">${title}</div>
                    <div class="notification-message">${message}</div>
                </div>
            </div>
        `;

        container.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);

        // Auto-remove after delay
        const delay = type === 'error' ? 8000 : 5000;
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => container.removeChild(notification), 300);
        }, delay);
    }

    getContentTitle(type) {
        const titles = {
            'validation': "You're Not Alone",
            'confessions': 'The Quiet Moments',
            'tips': 'Stop Doing This',
            'sandwich': 'Sandwich Generation Diaries',
            'chaos': 'Coordination Chaos'
        };
        return titles[type] || type;
    }

    getContentTypeInfo(type) {
        const info = {
            'validation': { title: "You're Not Alone", color: '#4A90E2' },
            'confessions': { title: 'The Quiet Moments', color: '#50C878' },
            'tips': { title: 'Stop Doing This', color: '#FF6B6B' },
            'sandwich': { title: 'Sandwich Generation Diaries', color: '#9B59B6' },
            'chaos': { title: 'Coordination Chaos', color: '#F39C12' },
            'unknown': { title: 'Unknown Type', color: '#718096' }
        };
        return info[type] || info.unknown;
    }

    getTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new KiinDashboard();
});

// Add some nice CSS for the success particles and preview badges
const additionalStyles = `
.preview-badge {
    background: #48BB78;
    color: white;
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 10px;
    margin-left: auto;
    font-weight: 600;
    text-transform: uppercase;
}

.preview-badge.new {
    background: #F6AD55;
    animation: pulse 2s infinite;
}

.btn-preview {
    background: var(--kiin-primary);
    color: white;
    border: none;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-preview:hover {
    background: var(--kiin-accent);
    transform: scale(1.1);
}

.activity-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);