// Kiin Content Factory Analytics Dashboard - JavaScript

class KiinAnalyticsDashboard {
    constructor() {
        this.currentSection = 'overview';
        this.charts = {};
        this.currentMonth = new Date();
        this.selectedContentType = 'validation';
        this.contentData = {};
        
        this.init();
    }

    init() {
        console.log('🚀 Initializing Kiin Analytics Dashboard');
        this.bindEvents();
        this.loadInitialData();
        this.initializeCharts();
        this.loadOverviewData();
        this.startPeriodicUpdates();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                this.navigateToSection(section);
            });
        });

        // Generation buttons
        document.querySelectorAll('.btn-generate').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const contentType = e.currentTarget.getAttribute('data-type');
                this.generateContent(contentType);
            });
        });

        // Calendar navigation
        document.getElementById('prev-month')?.addEventListener('click', () => {
            this.currentMonth.setMonth(this.currentMonth.getMonth() - 1);
            this.renderCalendar();
        });

        document.getElementById('next-month')?.addEventListener('click', () => {
            this.currentMonth.setMonth(this.currentMonth.getMonth() + 1);
            this.renderCalendar();
        });

        // Content type tabs
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const contentType = e.currentTarget.getAttribute('data-type');
                this.selectContentType(contentType);
            });
        });

        // Modal controls
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.currentTarget.closest('.modal');
                this.closeModal(modal.id);
            });
        });

        // Schedule form
        document.getElementById('schedule-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitSchedule();
        });

        // Batch generation
        document.getElementById('start-batch')?.addEventListener('click', () => {
            this.startBatchGeneration();
        });

        // Search
        document.getElementById('content-search')?.addEventListener('input', (e) => {
            this.filterContent(e.target.value);
        });

        // Quick generate
        document.getElementById('quick-generate')?.addEventListener('click', () => {
            this.quickGenerate();
        });

        // Schedule content button
        document.getElementById('schedule-content')?.addEventListener('click', () => {
            this.openModal('schedule-modal');
        });

        // Modal background clicks
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }

    async loadInitialData() {
        try {
            // Load overview data
            const overviewResponse = await fetch('/api/overview');
            this.overviewData = await overviewResponse.json();
            
            // Load calendar data
            const calendarResponse = await fetch('/api/calendar');
            this.calendarData = await calendarResponse.json();
            
            // Load performance data
            const performanceResponse = await fetch('/api/performance');
            this.performanceData = await performanceResponse.json();
            
            console.log('✅ Initial data loaded');
        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
            this.showNotification('Error', 'Failed to load dashboard data', 'error');
        }
    }

    navigateToSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(section).classList.add('active');

        // Update header
        this.updateHeader(section);

        // Load section-specific data
        this.loadSectionData(section);
        
        this.currentSection = section;
    }

    updateHeader(section) {
        const headers = {
            overview: {
                title: 'Content Library Overview',
                subtitle: 'Comprehensive analytics and management for caregiver content'
            },
            calendar: {
                title: 'Content Calendar',
                subtitle: 'Schedule and manage content across all platforms'
            },
            performance: {
                title: 'Performance Analytics',
                subtitle: 'Track engagement and optimize your content strategy'
            },
            generation: {
                title: 'Content Generation',
                subtitle: 'Create new videos with AI-powered content systems'
            },
            database: {
                title: 'Content Database',
                subtitle: 'Browse, search, and manage your content library'
            }
        };

        const headerInfo = headers[section] || headers.overview;
        document.querySelector('.page-title').textContent = headerInfo.title;
        document.querySelector('.page-subtitle').textContent = headerInfo.subtitle;
    }

    async loadSectionData(section) {
        switch (section) {
            case 'overview':
                this.loadOverviewData();
                break;
            case 'calendar':
                this.renderCalendar();
                break;
            case 'performance':
                this.renderPerformanceCharts();
                break;
            case 'generation':
                this.updateGenerationCounts();
                break;
            case 'database':
                this.loadContentDatabase();
                break;
        }
    }

    async loadOverviewData() {
        if (!this.overviewData) return;

        // Update content types grid
        const contentTypesGrid = document.getElementById('content-types-grid');
        if (contentTypesGrid) {
            contentTypesGrid.innerHTML = '';
            
            Object.entries(this.overviewData.content_types).forEach(([key, data]) => {
                const item = document.createElement('div');
                item.className = 'content-type-item';
                item.style.borderLeftColor = data.color;
                
                item.innerHTML = `
                    <div class="content-type-icon" style="background-color: ${data.color};">
                        <i class="fas fa-${data.icon}"></i>
                    </div>
                    <div class="content-type-title">${data.title}</div>
                    <div class="content-type-count">${data.count}</div>
                `;
                
                contentTypesGrid.appendChild(item);
            });
        }

        // Update storage stats
        const stats = this.overviewData.video_stats;
        document.getElementById('total-videos').textContent = stats.total_videos || 0;
        document.getElementById('storage-used').textContent = `${stats.total_size_mb?.toFixed(1) || 0} MB`;
        document.getElementById('success-rate').textContent = `${stats.success_rate || 100}%`;

        // Update header stats
        const totalContent = Object.values(this.overviewData.content_types)
            .reduce((sum, type) => sum + type.count, 0);
        document.getElementById('total-content').textContent = totalContent;
        document.getElementById('month-videos').textContent = stats.total_videos || 0;

        // Load recent activity
        this.loadRecentActivity();
        
        // Update generation chart
        this.updateGenerationChart();
    }

    async loadRecentActivity() {
        try {
            const response = await fetch('/api/videos');
            const videos = await response.json();
            
            const activityFeed = document.getElementById('activity-feed');
            if (!activityFeed) return;
            
            if (videos.length === 0) {
                activityFeed.innerHTML = `
                    <div class="activity-item">
                        <div class="activity-icon">
                            <i class="fas fa-info-circle"></i>
                        </div>
                        <div class="activity-details">
                            <div class="activity-title">No videos generated yet</div>
                            <div class="activity-time">Start creating content above!</div>
                        </div>
                    </div>
                `;
                return;
            }

            activityFeed.innerHTML = videos.slice(0, 10).map(video => {
                const timeAgo = this.getTimeAgo(new Date(video.created));
                const contentType = this.getContentTypeInfo(video.type);
                
                return `
                    <div class="activity-item">
                        <div class="activity-icon" style="background-color: ${contentType.color};">
                            <i class="fas fa-video"></i>
                        </div>
                        <div class="activity-details">
                            <div class="activity-title">${video.filename}</div>
                            <div class="activity-time">${contentType.title} • ${timeAgo}</div>
                        </div>
                    </div>
                `;
            }).join('');
            
        } catch (error) {
            console.error('Failed to load recent activity:', error);
        }
    }

    initializeCharts() {
        // Generation Chart
        const genCtx = document.getElementById('generation-chart');
        if (genCtx) {
            this.charts.generation = new Chart(genCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: ['#4A90B8', '#6BB3A0', '#F4A460', '#9B59B6', '#F39C12'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }
    }

    updateGenerationChart() {
        if (!this.charts.generation || !this.overviewData) return;

        const contentTypes = this.overviewData.content_types;
        const labels = Object.values(contentTypes).map(type => type.title);
        const data = Object.values(contentTypes).map(type => type.count);
        const colors = Object.values(contentTypes).map(type => type.color);

        this.charts.generation.data.labels = labels;
        this.charts.generation.data.datasets[0].data = data;
        this.charts.generation.data.datasets[0].backgroundColor = colors;
        this.charts.generation.update();
    }

    renderCalendar() {
        const calendarGrid = document.getElementById('calendar-grid');
        const calendarTitle = document.getElementById('calendar-title');
        
        if (!calendarGrid || !calendarTitle) return;

        // Update title
        calendarTitle.textContent = this.currentMonth.toLocaleDateString('en-US', { 
            month: 'long', 
            year: 'numeric' 
        });

        // Get calendar data for current month
        const year = this.currentMonth.getFullYear();
        const month = this.currentMonth.getMonth();
        
        // First day of month and number of days
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay()); // Start from Sunday
        
        // Clear grid and add day headers
        calendarGrid.innerHTML = '';
        
        ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            calendarGrid.appendChild(dayHeader);
        });
        
        // Add calendar days
        for (let day = 0; day < 42; day++) { // 6 weeks
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + day);
            
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            
            const isCurrentMonth = date.getMonth() === month;
            const dateStr = date.toISOString().split('T')[0];
            
            let dayContent = `<div class="calendar-day-number">${date.getDate()}</div>`;
            
            // Add scheduled content for this day
            if (this.calendarData && isCurrentMonth) {
                const dayData = this.calendarData.find(d => d.date === dateStr);
                if (dayData && dayData.content.length > 0) {
                    dayData.content.forEach(content => {
                        const platformColor = this.getPlatformColor(content.platform);
                        dayContent += `
                            <div class="calendar-content-item" style="background-color: ${platformColor};">
                                ${content.platform.charAt(0)}${content.platform.charAt(content.platform.length-1)}
                            </div>
                        `;
                    });
                }
            }
            
            dayElement.innerHTML = dayContent;
            
            if (!isCurrentMonth) {
                dayElement.style.opacity = '0.3';
            }
            
            calendarGrid.appendChild(dayElement);
        }
    }

    getPlatformColor(platform) {
        const colors = {
            'TikTok': '#FF0050',
            'Instagram': '#E4405F',
            'YouTube': '#FF0000'
        };
        return colors[platform] || '#6B7280';
    }

    renderPerformanceCharts() {
        if (!this.performanceData) return;

        this.renderViewsChart();
        this.renderEngagementChart();
        this.renderPlatformStats();
        this.renderTopContent();
    }

    renderViewsChart() {
        const ctx = document.getElementById('views-chart');
        if (!ctx || this.charts.views) return;

        const viewsData = this.performanceData.views_by_type;
        
        this.charts.views = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(viewsData).map(key => this.getContentTypeInfo(key).title),
                datasets: [{
                    label: 'Views',
                    data: Object.values(viewsData),
                    backgroundColor: Object.keys(viewsData).map(key => this.getContentTypeInfo(key).color),
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    renderEngagementChart() {
        const ctx = document.getElementById('engagement-chart');
        if (!ctx || this.charts.engagement) return;

        const engagementData = this.performanceData.engagement_rates;
        
        this.charts.engagement = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Object.keys(engagementData).map(key => this.getContentTypeInfo(key).title),
                datasets: [{
                    label: 'Engagement Rate (%)',
                    data: Object.values(engagementData),
                    borderColor: '#4A90B8',
                    backgroundColor: 'rgba(74, 144, 184, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#4A90B8',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    renderPlatformStats() {
        const container = document.getElementById('platform-stats');
        if (!container || !this.performanceData.platform_performance) return;

        container.innerHTML = '';
        
        Object.entries(this.performanceData.platform_performance).forEach(([platform, data]) => {
            const item = document.createElement('div');
            item.className = 'platform-item';
            
            item.innerHTML = `
                <div class="platform-name">${platform}</div>
                <div class="platform-metrics">
                    <div class="metric-item">
                        <div class="metric-value">${data.views.toLocaleString()}</div>
                        <div class="metric-label">Views</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value">${data.engagement}%</div>
                        <div class="metric-label">Engagement</div>
                    </div>
                </div>
            `;
            
            container.appendChild(item);
        });
    }

    renderTopContent() {
        const container = document.getElementById('top-content');
        if (!container) return;

        // Generate mock top-performing content
        const topContent = [
            { title: "Validation #142", views: 45200, engagement: 8.7, type: 'validation' },
            { title: "Confession #89", views: 38900, engagement: 7.2, type: 'confessions' },
            { title: "Tip #67", views: 31500, engagement: 6.8, type: 'tips' },
            { title: "Sandwich #34", views: 28100, engagement: 6.1, type: 'sandwich' },
            { title: "Chaos #23", views: 22800, engagement: 5.9, type: 'chaos' }
        ];

        container.innerHTML = topContent.map(content => {
            const typeInfo = this.getContentTypeInfo(content.type);
            return `
                <div class="content-item" style="border-left-color: ${typeInfo.color};">
                    <div class="content-item-header">
                        <div class="content-item-title">${content.title}</div>
                    </div>
                    <div class="content-item-text">
                        ${content.views.toLocaleString()} views • ${content.engagement}% engagement
                    </div>
                </div>
            `;
        }).join('');
    }

    async generateContent(contentType) {
        const button = document.querySelector(`[data-type="${contentType}"] .btn-generate`);
        const overlay = document.getElementById(`overlay-${contentType}`);
        
        if (!button || !overlay) return;

        try {
            // Show loading state
            button.disabled = true;
            overlay.classList.add('active');

            this.showNotification(
                'Generation Started',
                `Creating your ${this.getContentTypeInfo(contentType).title} video...`,
                'info'
            );

            const response = await fetch(`/api/generate/${contentType}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(
                    'Video Generated!',
                    `${result.message} File: ${result.filename}`,
                    'success'
                );

                // Refresh data
                this.loadOverviewData();
                this.loadRecentActivity();
                
                // Add success animation
                this.addSuccessAnimation(button.closest('.generation-card'));
                
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
            button.disabled = false;
            overlay.classList.remove('active');
        }
    }

    async updateGenerationCounts() {
        if (!this.overviewData) return;

        Object.entries(this.overviewData.content_types).forEach(([key, data]) => {
            const countElement = document.getElementById(`count-${key}`);
            if (countElement) {
                countElement.textContent = `${data.count} stories available`;
            }
        });
    }

    selectContentType(contentType) {
        // Update tabs
        document.querySelectorAll('.tab-button').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-type="${contentType}"]`).classList.add('active');

        this.selectedContentType = contentType;
        this.loadContentDatabase();
    }

    async loadContentDatabase() {
        try {
            const response = await fetch(`/api/content/${this.selectedContentType}`);
            const data = await response.json();
            
            this.contentData[this.selectedContentType] = data;
            this.renderContentItems(data.items);
            
        } catch (error) {
            console.error('Failed to load content database:', error);
            this.showNotification('Error', 'Failed to load content data', 'error');
        }
    }

    renderContentItems(items) {
        const container = document.getElementById('content-items');
        if (!container || !items) return;

        container.innerHTML = '';

        items.forEach(item => {
            const element = document.createElement('div');
            element.className = 'content-item';
            
            const typeInfo = this.getContentTypeInfo(this.selectedContentType);
            element.style.borderLeftColor = typeInfo.color;
            
            let content = '';
            if (item.hook && item.confession) {
                // Confession format
                content = `
                    <div class="content-item-header">
                        <div class="content-item-title">${item.hook}</div>
                        <div class="content-item-id">#${item.id}</div>
                    </div>
                    <div class="content-item-text">${item.confession}</div>
                `;
            } else if (item.hook && item.wrong) {
                // Tips format
                content = `
                    <div class="content-item-header">
                        <div class="content-item-title">${item.hook}</div>
                        <div class="content-item-id">#${item.id}</div>
                    </div>
                    <div class="content-item-text">❌ ${item.wrong}<br>✅ ${item.right}</div>
                `;
            } else if (item.message) {
                // Validation format
                content = `
                    <div class="content-item-header">
                        <div class="content-item-title">Validation Message</div>
                        <div class="content-item-id">#${item.id}</div>
                    </div>
                    <div class="content-item-text">${item.message}</div>
                `;
            } else {
                // Generic format
                content = `
                    <div class="content-item-header">
                        <div class="content-item-title">${typeInfo.title} Content</div>
                        <div class="content-item-id">#${item.id}</div>
                    </div>
                    <div class="content-item-text">${JSON.stringify(item, null, 2)}</div>
                `;
            }

            content += `
                <div class="content-item-actions">
                    <button class="btn-icon" onclick="dashboard.editContent('${this.selectedContentType}', ${item.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" onclick="dashboard.previewContent('${this.selectedContentType}', ${item.id})" title="Preview">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon" onclick="dashboard.generateFromContent('${this.selectedContentType}', ${item.id})" title="Generate Video">
                        <i class="fas fa-video"></i>
                    </button>
                </div>
            `;

            element.innerHTML = content;
            container.appendChild(element);
        });
    }

    filterContent(searchTerm) {
        const items = document.querySelectorAll('.content-item');
        const term = searchTerm.toLowerCase();
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(term)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async submitSchedule() {
        const form = document.getElementById('schedule-form');
        const formData = new FormData(form);
        
        const scheduleData = {
            content_type: document.getElementById('schedule-type').value,
            platform: document.getElementById('schedule-platform').value,
            date: document.getElementById('schedule-date').value
        };

        try {
            const response = await fetch('/api/schedule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(scheduleData)
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification(
                    'Content Scheduled!',
                    'Your content has been added to the calendar.',
                    'success'
                );
                this.closeModal('schedule-modal');
                
                // Refresh calendar if we're on that section
                if (this.currentSection === 'calendar') {
                    this.renderCalendar();
                }
            } else {
                this.showNotification(
                    'Scheduling Failed',
                    result.error || 'Could not schedule content',
                    'error'
                );
            }
        } catch (error) {
            console.error('Scheduling error:', error);
            this.showNotification(
                'Network Error',
                'Could not connect to the server',
                'error'
            );
        }
    }

    async startBatchGeneration() {
        const selectedTypes = Array.from(document.querySelectorAll('.batch-options input:checked'))
            .map(input => input.value);
        
        if (selectedTypes.length === 0) {
            this.showNotification('No Selection', 'Please select content types to generate', 'warning');
            return;
        }

        const quantity = parseInt(document.getElementById('batch-quantity').value);
        const progressBar = document.getElementById('batch-progress');
        const progressFill = progressBar.querySelector('.progress-fill');
        const progressStatus = progressBar.querySelector('.progress-status');
        
        progressBar.style.display = 'block';
        progressFill.style.width = '0%';
        
        let completed = 0;
        const total = selectedTypes.length * quantity;
        
        progressStatus.textContent = `Generating videos... ${completed}/${total} complete`;

        for (const contentType of selectedTypes) {
            for (let i = 0; i < quantity; i++) {
                try {
                    await this.generateContent(contentType);
                    completed++;
                    
                    const percentage = (completed / total) * 100;
                    progressFill.style.width = `${percentage}%`;
                    progressStatus.textContent = `Generating videos... ${completed}/${total} complete`;
                    
                    // Small delay between generations
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                } catch (error) {
                    console.error(`Batch generation error for ${contentType}:`, error);
                }
            }
        }

        this.showNotification(
            'Batch Generation Complete!',
            `Successfully generated ${completed} videos`,
            'success'
        );
        
        setTimeout(() => {
            progressBar.style.display = 'none';
        }, 3000);
    }

    quickGenerate() {
        // Generate one video from each content type
        const contentTypes = ['validation', 'confessions', 'tips'];
        const randomType = contentTypes[Math.floor(Math.random() * contentTypes.length)];
        this.generateContent(randomType);
    }

    // Modal Management
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // Content Management Functions
    editContent(contentType, id) {
        this.showNotification('Edit Content', `Editing ${contentType} content #${id}`, 'info');
        // Would open edit modal in real implementation
    }

    previewContent(contentType, id) {
        this.showNotification('Preview Content', `Previewing ${contentType} content #${id}`, 'info');
        // Would show preview modal in real implementation
    }

    generateFromContent(contentType, id) {
        this.showNotification('Generate Video', `Generating video from ${contentType} #${id}`, 'info');
        this.generateContent(contentType);
    }

    addNewContent() {
        this.showNotification('Add Content', 'Opening content editor...', 'info');
        // Would open add content modal in real implementation
    }

    // Utility Functions
    getContentTypeInfo(type) {
        const info = {
            'validation': { title: "You're Not Alone", color: '#4A90B8', icon: 'heart' },
            'confessions': { title: 'The Quiet Moments', color: '#6BB3A0', icon: 'comment-dots' },
            'tips': { title: 'Stop Doing This', color: '#F4A460', icon: 'lightbulb' },
            'sandwich': { title: 'Sandwich Generation Diaries', color: '#9B59B6', icon: 'users' },
            'chaos': { title: 'Coordination Chaos', color: '#F39C12', icon: 'sync-alt' },
            'unknown': { title: 'Unknown Type', color: '#6B7280', icon: 'question' }
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

    addSuccessAnimation(element) {
        element.classList.add('success-animation');
        setTimeout(() => {
            element.classList.remove('success-animation');
        }, 600);
    }

    showNotification(title, message, type = 'info') {
        const container = document.getElementById('notifications');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };

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

        // Auto-remove
        const delay = type === 'error' ? 8000 : 5000;
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    container.removeChild(notification);
                }
            }, 300);
        }, delay);
    }

    startPeriodicUpdates() {
        // Refresh overview data every 5 minutes
        setInterval(() => {
            if (this.currentSection === 'overview') {
                this.loadOverviewData();
            }
        }, 300000);

        // Refresh recent activity every 2 minutes
        setInterval(() => {
            this.loadRecentActivity();
        }, 120000);
    }

    refreshActivity() {
        this.loadRecentActivity();
        this.showNotification('Refreshed', 'Activity feed updated', 'success');
    }
}

// Global functions for onclick handlers
window.refreshActivity = () => dashboard.refreshActivity();
window.previewContent = (type, id) => dashboard.previewContent(type, id);
window.editContent = (type, id) => dashboard.editContent(type, id);
window.generateFromContent = (type, id) => dashboard.generateFromContent(type, id);
window.scheduleContent = (type) => {
    dashboard.openModal('schedule-modal');
    if (type) {
        document.getElementById('schedule-type').value = type;
    }
};
window.addNewContent = () => dashboard.addNewContent();
window.closeModal = (modalId) => dashboard.closeModal(modalId);

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new KiinAnalyticsDashboard();
    console.log('🎬 Kiin Analytics Dashboard initialized successfully!');
});

// Add responsive sidebar toggle for mobile
function initMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    // Add mobile menu button
    const mobileMenuBtn = document.createElement('button');
    mobileMenuBtn.className = 'mobile-menu-btn';
    mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
    mobileMenuBtn.style.cssText = `
        display: none;
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 1001;
        background: var(--kiin-primary);
        color: white;
        border: none;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: var(--shadow-lg);
    `;
    
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024 && 
            !sidebar.contains(e.target) && 
            !mobileMenuBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
    
    // Show/hide mobile menu button based on screen size
    const checkScreenSize = () => {
        if (window.innerWidth <= 1024) {
            mobileMenuBtn.style.display = 'flex';
            mobileMenuBtn.style.alignItems = 'center';
            mobileMenuBtn.style.justifyContent = 'center';
        } else {
            mobileMenuBtn.style.display = 'none';
            sidebar.classList.remove('open');
        }
    };
    
    window.addEventListener('resize', checkScreenSize);
    checkScreenSize();
    
    document.body.appendChild(mobileMenuBtn);
}

// Initialize mobile sidebar when DOM loads
document.addEventListener('DOMContentLoaded', initMobileSidebar);