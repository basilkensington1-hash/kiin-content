#!/usr/bin/env python3
"""
Kiin Content Factory Dashboard
A beautiful web interface for generating caregiver content
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import subprocess
import random

# Add the parent src directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir / "src"))

app = Flask(__name__)
app.secret_key = 'kiin-content-factory-2024'

# Content type configurations
CONTENT_TYPES = {
    'validation': {
        'title': "You're Not Alone",
        'description': 'Validation Series - Heartfelt messages that remind caregivers they are seen and understood',
        'generator': 'validation_generator.py',
        'config': 'config/validation_messages.json',
        'color': '#4A90E2'
    },
    'confessions': {
        'title': 'The Quiet Moments',
        'description': 'Caregiver Confessions - Raw, honest moments that caregivers recognize but rarely talk about',
        'generator': 'confession_generator.py',
        'config': 'config/confessions.json',
        'color': '#50C878'
    },
    'tips': {
        'title': 'Stop Doing This',
        'description': 'Educational Tips - Practical advice to make caregiving easier and more effective',
        'generator': 'tips_generator.py',
        'config': 'config/caregiver_tips.json',
        'color': '#FF6B6B'
    },
    'sandwich': {
        'title': 'Sandwich Generation Diaries',
        'description': 'POV Content - First-person stories of juggling kids, aging parents, and everything in between',
        'generator': 'sandwich_generator.py', 
        'config': 'config/sandwich_scenarios.json',
        'color': '#9B59B6'
    },
    'chaos': {
        'title': 'Coordination Chaos',
        'description': 'Before/After Stories - Dramatic transformations from scattered to organized care coordination',
        'generator': 'chaos_generator.py',
        'config': 'config/coordination_scenarios.json',
        'color': '#F39C12'
    }
}

def get_config_count(config_path):
    """Get the number of items in a JSON config file"""
    try:
        full_path = parent_dir / config_path
        with open(full_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return len(data)
            elif isinstance(data, dict):
                # Count items in different possible structures
                for key in ['tips', 'confessions', 'validations', 'scenarios']:
                    if key in data:
                        return len(data[key])
                return len(data)
    except Exception as e:
        print(f"Error reading config {config_path}: {e}")
        return 0

def get_latest_video(content_type):
    """Get the most recent video file for a content type"""
    output_dir = parent_dir / "output"
    if not output_dir.exists():
        return None
    
    # Pattern matching for different types
    patterns = {
        'validation': ['validation_*.mp4', '*validation*.mp4'],
        'confessions': ['confession_*.mp4', '*confession*.mp4'],
        'tips': ['tip_*.mp4', '*tip*.mp4'],
        'sandwich': ['sandwich_*.mp4', '*sandwich*.mp4'],
        'chaos': ['chaos_*.mp4', '*coordination*.mp4', '*chaos*.mp4']
    }
    
    latest_file = None
    latest_time = 0
    
    for pattern in patterns.get(content_type, []):
        for file_path in output_dir.glob(pattern):
            if file_path.stat().st_mtime > latest_time:
                latest_time = file_path.stat().st_mtime
                latest_file = file_path
    
    return str(latest_file.name) if latest_file else None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    # Add counts and latest videos to content types
    content_data = {}
    for key, config in CONTENT_TYPES.items():
        content_data[key] = {
            **config,
            'count': get_config_count(config['config']),
            'latest_video': get_latest_video(key)
        }
    
    return render_template('index.html', content_types=content_data)

@app.route('/api/generate/<content_type>', methods=['POST'])
def generate_content(content_type):
    """Generate content for specified type"""
    if content_type not in CONTENT_TYPES:
        return jsonify({'error': 'Invalid content type'}), 400
    
    try:
        config = CONTENT_TYPES[content_type]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output filename
        output_name = f"{content_type}_{timestamp}.mp4"
        
        # Build command based on generator
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
        
        # Change to parent directory to run the command
        result = subprocess.run(
            cmd,
            cwd=parent_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'video_path': f'output/{output_name}',
                'filename': output_name,
                'message': f'{config["title"]} video generated successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Generation failed: {result.stderr}'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Generation timed out (5 minutes)'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/status')
def api_status():
    """Get current status of all content types"""
    status_data = {}
    for key, config in CONTENT_TYPES.items():
        status_data[key] = {
            'title': config['title'],
            'count': get_config_count(config['config']),
            'latest_video': get_latest_video(key),
            'color': config['color']
        }
    
    return jsonify(status_data)

@app.route('/api/videos')
def list_videos():
    """List recent videos"""
    output_dir = parent_dir / "output"
    if not output_dir.exists():
        return jsonify([])
    
    videos = []
    for video_file in output_dir.glob("*.mp4"):
        stat = video_file.stat()
        videos.append({
            'filename': video_file.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'type': detect_video_type(video_file.name)
        })
    
    # Sort by creation time, newest first
    videos.sort(key=lambda x: x['created'], reverse=True)
    return jsonify(videos[:20])  # Return last 20 videos

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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    print("🚀 Starting Kiin Content Factory Dashboard...")
    print(f"📱 Dashboard will be available at: http://localhost:{args.port}")
    print("🎬 Ready to generate amazing content!")
    app.run(debug=True, host='0.0.0.0', port=args.port)