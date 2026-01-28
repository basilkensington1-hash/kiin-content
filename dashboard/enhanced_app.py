#!/usr/bin/env python3
"""
Kiin Content Factory Analytics Dashboard
Comprehensive analytics and management interface for caregiver content
"""

import asyncio
import json
import os
import sys
import sqlite3
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
import subprocess
import random
import glob
from collections import defaultdict, Counter
import mimetypes

# Add the parent src directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir / "src"))

app = Flask(__name__)
app.secret_key = 'kiin-analytics-dashboard-2024'

# Initialize database
def init_db():
    """Initialize SQLite database for tracking analytics"""
    db_path = parent_dir / "data" / "analytics.db"
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS video_generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            filename TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT TRUE,
            file_size INTEGER,
            duration REAL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS content_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            platform TEXT NOT NULL,
            scheduled_date DATE NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            platform TEXT NOT NULL,
            filename TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0.0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Content type configurations with enhanced metadata
CONTENT_TYPES = {
    'validation': {
        'title': "You're Not Alone",
        'description': 'Validation Series - Heartfelt messages that remind caregivers they are seen and understood',
        'generator': 'validation_generator.py',
        'config': 'config/validation_messages.json',
        'color': '#4A90B8',  # Brand primary
        'icon': 'heart',
        'platforms': ['TikTok', 'Instagram', 'YouTube']
    },
    'confessions': {
        'title': 'The Quiet Moments',
        'description': 'Caregiver Confessions - Raw, honest moments that caregivers recognize but rarely talk about',
        'generator': 'confession_generator.py',
        'config': 'config/confessions.json',
        'color': '#6BB3A0',  # Brand secondary
        'icon': 'comment-dots',
        'platforms': ['TikTok', 'Instagram']
    },
    'tips': {
        'title': 'Stop Doing This',
        'description': 'Educational Tips - Practical advice to make caregiving easier and more effective',
        'generator': 'tips_generator.py',
        'config': 'config/caregiver_tips.json',
        'color': '#F4A460',  # Brand accent
        'icon': 'lightbulb',
        'platforms': ['TikTok', 'Instagram', 'YouTube']
    },
    'sandwich': {
        'title': 'Sandwich Generation Diaries',
        'description': 'POV Content - First-person stories of juggling kids, aging parents, and everything in between',
        'generator': 'sandwich_generator.py', 
        'config': 'config/sandwich_scenarios.json',
        'color': '#9B59B6',
        'icon': 'users',
        'platforms': ['TikTok', 'Instagram']
    },
    'chaos': {
        'title': 'Coordination Chaos',
        'description': 'Before/After Stories - Dramatic transformations from scattered to organized care coordination',
        'generator': 'chaos_generator.py',
        'config': 'config/coordination_scenarios.json',
        'color': '#F39C12',
        'icon': 'sync-alt',
        'platforms': ['TikTok', 'YouTube']
    }
}

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(parent_dir / "data" / "analytics.db")

def get_config_data(config_path):
    """Get data from a JSON config file"""
    try:
        full_path = parent_dir / config_path
        with open(full_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'tips' in data:
                return data['tips']
            elif isinstance(data, dict) and 'confessions' in data:
                return data['confessions']
            elif isinstance(data, list):
                return data
            return data
    except Exception as e:
        print(f"Error reading config {config_path}: {e}")
        return []

def get_config_count(config_path):
    """Get the number of items in a JSON config file"""
    data = get_config_data(config_path)
    return len(data) if isinstance(data, list) else 0

def get_video_stats():
    """Get video generation statistics"""
    output_dir = parent_dir / "output"
    if not output_dir.exists():
        return {}
    
    videos = list(output_dir.glob("*.mp4"))
    stats = {
        'total_videos': len(videos),
        'total_size_mb': sum(v.stat().st_size for v in videos) / (1024 * 1024),
        'types': defaultdict(int),
        'success_rate': 100.0,  # Placeholder
        'avg_generation_time': 45.0  # Placeholder in seconds
    }
    
    for video in videos:
        content_type = detect_video_type(video.name)
        stats['types'][content_type] += 1
    
    return stats

def get_scheduled_content():
    """Get scheduled content from database"""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT content_type, platform, scheduled_date, status, COUNT(*) as count
        FROM content_schedule 
        WHERE scheduled_date >= date('now')
        GROUP BY content_type, platform, scheduled_date, status
        ORDER BY scheduled_date
    ''')
    
    schedule = []
    for row in cursor.fetchall():
        schedule.append({
            'content_type': row[0],
            'platform': row[1],
            'date': row[2],
            'status': row[3],
            'count': row[4]
        })
    
    conn.close()
    return schedule

def detect_video_type(filename):
    """Detect content type from filename"""
    filename = filename.lower()
    if 'validation' in filename:
        return 'validation'
    elif 'confession' in filename:
        return 'confessions'
    elif 'tip' in filename:
        return 'tips'
    elif 'sandwich' in filename:
        return 'sandwich'
    elif 'chaos' in filename or 'coordination' in filename:
        return 'chaos'
    return 'unknown'

def get_performance_data():
    """Get performance metrics (placeholder data for demo)"""
    return {
        'views_by_type': {
            'validation': random.randint(15000, 45000),
            'confessions': random.randint(25000, 55000),
            'tips': random.randint(18000, 35000),
            'sandwich': random.randint(12000, 28000),
            'chaos': random.randint(8000, 22000)
        },
        'engagement_rates': {
            'validation': round(random.uniform(3.5, 7.2), 1),
            'confessions': round(random.uniform(4.1, 8.5), 1),
            'tips': round(random.uniform(2.8, 6.1), 1),
            'sandwich': round(random.uniform(3.9, 7.8), 1),
            'chaos': round(random.uniform(2.5, 5.9), 1)
        },
        'platform_performance': {
            'TikTok': {'views': 125000, 'engagement': 6.2},
            'Instagram': {'views': 89000, 'engagement': 4.8},
            'YouTube': {'views': 42000, 'engagement': 3.1}
        }
    }

@app.route('/')
def dashboard():
    """Main analytics dashboard"""
    return render_template('analytics.html', content_types=CONTENT_TYPES)

@app.route('/api/overview')
def api_overview():
    """Content library overview API"""
    overview = {}
    for key, config in CONTENT_TYPES.items():
        count = get_config_count(config['config'])
        overview[key] = {
            'title': config['title'],
            'count': count,
            'color': config['color'],
            'icon': config['icon']
        }
    
    video_stats = get_video_stats()
    
    return jsonify({
        'content_types': overview,
        'video_stats': video_stats,
        'storage_usage': {
            'total_mb': round(video_stats.get('total_size_mb', 0), 1),
            'total_videos': video_stats.get('total_videos', 0)
        }
    })

@app.route('/api/calendar')
def api_calendar():
    """Content calendar API"""
    # Get scheduled content
    scheduled = get_scheduled_content()
    
    # Generate some upcoming content for demo
    calendar_data = []
    for i in range(30):  # Next 30 days
        date = datetime.now() + timedelta(days=i)
        content_for_day = []
        
        # Add some random scheduled content
        if random.random() > 0.6:  # 40% chance of content per day
            content_type = random.choice(list(CONTENT_TYPES.keys()))
            platform = random.choice(CONTENT_TYPES[content_type]['platforms'])
            content_for_day.append({
                'content_type': content_type,
                'platform': platform,
                'title': CONTENT_TYPES[content_type]['title'],
                'color': CONTENT_TYPES[content_type]['color']
            })
        
        calendar_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'content': content_for_day
        })
    
    return jsonify(calendar_data)

@app.route('/api/performance')
def api_performance():
    """Performance metrics API"""
    return jsonify(get_performance_data())

@app.route('/api/content/<content_type>')
def api_content_browse(content_type):
    """Content database browser API"""
    if content_type not in CONTENT_TYPES:
        return jsonify({'error': 'Invalid content type'}), 400
    
    config = CONTENT_TYPES[content_type]
    data = get_config_data(config['config'])
    
    # Add metadata
    for item in data:
        if isinstance(item, dict):
            item['content_type'] = content_type
    
    return jsonify({
        'content_type': content_type,
        'title': config['title'],
        'total_items': len(data),
        'items': data
    })

@app.route('/api/generate/<content_type>', methods=['POST'])
def api_generate(content_type):
    """Enhanced content generation with analytics tracking"""
    if content_type not in CONTENT_TYPES:
        return jsonify({'error': 'Invalid content type'}), 400
    
    try:
        config = CONTENT_TYPES[content_type]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{content_type}_{timestamp}.mp4"
        
        # Track generation attempt
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO video_generations (content_type, filename, success) VALUES (?, ?, ?)',
            (content_type, output_name, False)  # Will update to True on success
        )
        generation_id = conn.lastrowid
        conn.commit()
        conn.close()
        
        # Build generation command
        if content_type == 'validation':
            cmd = [sys.executable, 'src/validation_generator.py', '--output', output_name]
        elif content_type == 'confessions':
            cmd = [sys.executable, 'src/confession_generator.py', '--output', output_name]
        elif content_type == 'tips':
            cmd = [sys.executable, 'generate_tip.py', '--output', f'{content_type}_{timestamp}']
        elif content_type == 'sandwich':
            cmd = [sys.executable, 'src/sandwich_generator.py', '--output', output_name]
        elif content_type == 'chaos':
            cmd = [sys.executable, 'src/chaos_generator.py', '--output', output_name]
        
        # Execute generation
        result = subprocess.run(
            cmd,
            cwd=parent_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            # Update success status and file info
            output_path = parent_dir / "output" / output_name
            file_size = output_path.stat().st_size if output_path.exists() else 0
            
            conn = get_db_connection()
            conn.execute(
                'UPDATE video_generations SET success = ?, file_size = ? WHERE id = ?',
                (True, file_size, generation_id)
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'video_path': f'output/{output_name}',
                'filename': output_name,
                'message': f'{config["title"]} video generated successfully!',
                'file_size': file_size
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Generation failed: {result.stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/schedule', methods=['POST'])
def api_schedule_content():
    """Schedule content for publication"""
    data = request.json
    
    required_fields = ['content_type', 'platform', 'date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['content_type'] not in CONTENT_TYPES:
        return jsonify({'error': 'Invalid content type'}), 400
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO content_schedule (content_type, platform, scheduled_date) VALUES (?, ?, ?)',
        (data['content_type'], data['platform'], data['date'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Content scheduled successfully'})

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    args = parser.parse_args()
    
    print("🚀 Starting Kiin Content Factory Analytics Dashboard...")
    print(f"📊 Dashboard will be available at: http://localhost:{args.port}")
    print("🎬 Analytics, calendar, and content management ready!")
    app.run(debug=True, host='0.0.0.0', port=args.port)