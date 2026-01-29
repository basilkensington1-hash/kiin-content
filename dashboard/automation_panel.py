#!/usr/bin/env python3
"""
Kiin Content Factory - Automation Control Panel
All automations, one dashboard, click to execute.
"""

import json
import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
import queue

app = Flask(__name__)
app.secret_key = 'kiin-automation-panel-2026'

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"

# Job tracking
running_jobs: Dict[str, dict] = {}
job_logs: Dict[str, list] = {}
job_counter = 0


@dataclass
class Automation:
    """Single automation definition"""
    id: str
    name: str
    description: str
    script: str
    category: str
    args: List[str] = None
    output_type: str = "file"  # file, video, text, json


# ============== ALL AUTOMATIONS ==============
AUTOMATIONS: Dict[str, Automation] = {
    # === VIDEO GENERATORS ===
    "validation_v2": Automation(
        id="validation_v2",
        name="Validation Video (V2)",
        description="'You're Not Alone' - Heartfelt validation messages for caregivers",
        script="src/validation_generator_v2.py",
        category="Video Generators",
        output_type="video"
    ),
    "confession_v2": Automation(
        id="confession_v2",
        name="Confession Video (V2)",
        description="'The Quiet Moments' - Raw, honest caregiver confessions",
        script="src/confession_generator_v2.py",
        category="Video Generators",
        output_type="video"
    ),
    "tips_v2": Automation(
        id="tips_v2",
        name="Tips Video (V2)",
        description="'Stop Doing This' - Educational tips in viral format",
        script="src/tips_generator_v2.py",
        category="Video Generators",
        output_type="video"
    ),
    "sandwich_v2": Automation(
        id="sandwich_v2",
        name="Sandwich Video (V2)",
        description="'Sandwich Generation Diaries' - POV juggling kids & aging parents",
        script="src/sandwich_generator_v2.py",
        category="Video Generators",
        output_type="video"
    ),
    "chaos_v2": Automation(
        id="chaos_v2",
        name="Chaos Video (V2)",
        description="'Coordination Chaos' - Before/after care coordination stories",
        script="src/chaos_generator_v2.py",
        category="Video Generators",
        output_type="video"
    ),
    "reflection": Automation(
        id="reflection",
        name="Reflection Video",
        description="Cinematic reflection/nostalgia content (2026 trend)",
        script="src/reflection_generator.py",
        category="Video Generators",
        output_type="video"
    ),
    "facts": Automation(
        id="facts",
        name="Facts Video",
        description="Caregiver facts and statistics",
        script="src/facts_generator.py",
        category="Video Generators",
        output_type="video"
    ),
    "mythbuster": Automation(
        id="mythbuster",
        name="Mythbuster Video",
        description="Debunk common caregiving myths",
        script="src/mythbuster_generator.py",
        category="Video Generators",
        output_type="video"
    ),
    "quickwin": Automation(
        id="quickwin",
        name="Quick Win Video",
        description="Fast, actionable caregiver tips",
        script="src/quickwin_generator.py",
        category="Video Generators",
        output_type="video"
    ),
    
    # === VISUAL GENERATORS ===
    "thumbnail": Automation(
        id="thumbnail",
        name="Thumbnail Generator",
        description="Eye-catching video thumbnails",
        script="src/thumbnail_generator.py",
        category="Visual Generators",
        output_type="file"
    ),
    "quote_card": Automation(
        id="quote_card",
        name="Quote Card Generator",
        description="Shareable quote graphics",
        script="src/quote_card_generator.py",
        category="Visual Generators",
        output_type="file"
    ),
    "carousel": Automation(
        id="carousel",
        name="Carousel Generator",
        description="Instagram carousel slides",
        script="src/carousel_generator.py",
        category="Visual Generators",
        output_type="file"
    ),
    "intro": Automation(
        id="intro",
        name="Intro Generator",
        description="Video intro animations",
        script="src/intro_generator.py",
        category="Visual Generators",
        output_type="video"
    ),
    "outro": Automation(
        id="outro",
        name="Outro Generator",
        description="Video outro with CTA",
        script="src/outro_generator.py",
        category="Visual Generators",
        output_type="video"
    ),
    
    # === CONTENT GENERATORS ===
    "blog": Automation(
        id="blog",
        name="Blog Post Generator",
        description="Long-form blog articles",
        script="src/blog_generator.py",
        category="Content Generators",
        output_type="text"
    ),
    "email": Automation(
        id="email",
        name="Email Generator",
        description="Email campaigns and sequences",
        script="src/email_generator.py",
        category="Content Generators",
        output_type="text"
    ),
    "leadmagnet": Automation(
        id="leadmagnet",
        name="Lead Magnet Generator",
        description="PDF guides and downloads",
        script="src/leadmagnet_generator.py",
        category="Content Generators",
        output_type="file"
    ),
    "faq": Automation(
        id="faq",
        name="FAQ Generator",
        description="FAQ content from common questions",
        script="src/faq_generator.py",
        category="Content Generators",
        output_type="text"
    ),
    "caption": Automation(
        id="caption",
        name="Caption Generator",
        description="Social media captions with hashtags",
        script="src/caption_generator.py",
        category="Content Generators",
        output_type="text"
    ),
    "comment": Automation(
        id="comment",
        name="Comment Responses",
        description="Generate engagement responses",
        script="src/comment_responses.py",
        category="Content Generators",
        output_type="text"
    ),
    
    # === BATCH & AUTOMATION ===
    "batch": Automation(
        id="batch",
        name="Batch Generator",
        description="Generate multiple videos at once",
        script="src/batch_generator.py",
        category="Batch & Automation",
        output_type="video"
    ),
    "generate_all": Automation(
        id="generate_all",
        name="Generate All",
        description="Generate one of each content type",
        script="generate_all.py",
        category="Batch & Automation",
        output_type="video"
    ),
    "repurpose": Automation(
        id="repurpose",
        name="Repurpose Engine",
        description="Adapt content for different platforms",
        script="src/repurpose.py",
        category="Batch & Automation",
        output_type="file"
    ),
    "content_calendar": Automation(
        id="content_calendar",
        name="Content Calendar",
        description="Generate posting schedule",
        script="src/content_calendar.py",
        category="Batch & Automation",
        output_type="json"
    ),
    
    # === TESTING & ANALYTICS ===
    "ab_testing": Automation(
        id="ab_testing",
        name="A/B Testing",
        description="Create A/B test variants",
        script="src/ab_testing.py",
        category="Testing & Analytics",
        output_type="file"
    ),
    "analytics": Automation(
        id="analytics",
        name="Analytics Report",
        description="Generate performance report",
        script="src/analytics.py",
        category="Testing & Analytics",
        output_type="json"
    ),
    "benchmark": Automation(
        id="benchmark",
        name="Performance Benchmark",
        description="Benchmark generator performance",
        script="src/performance_benchmark.py",
        category="Testing & Analytics",
        output_type="text"
    ),
    "test_v2": Automation(
        id="test_v2",
        name="Test All V2 Generators",
        description="Run tests on all V2 generators",
        script="test_all_v2_generators.py",
        category="Testing & Analytics",
        output_type="text"
    ),
    
    # === SOCIAL POSTING ===
    "posting_manager": Automation(
        id="posting_manager",
        name="Social Posting Manager",
        description="Unified social media posting",
        script="src/social/posting_manager.py",
        category="Social Posting",
        output_type="text"
    ),
    "hashtag_optimizer": Automation(
        id="hashtag_optimizer",
        name="Hashtag Optimizer",
        description="Optimize hashtags for reach",
        script="src/social/hashtag_optimizer.py",
        category="Social Posting",
        output_type="json"
    ),
    "repurpose_engine": Automation(
        id="repurpose_engine",
        name="Cross-Platform Repurpose",
        description="Adapt content for all platforms",
        script="src/social/repurpose_engine.py",
        category="Social Posting",
        output_type="file"
    ),
    
    # === AUDIO & EFFECTS ===
    "audio_demo": Automation(
        id="audio_demo",
        name="Audio System Demo",
        description="Demo the complete audio system",
        script="demo_complete_audio_system.py",
        category="Audio & Effects",
        output_type="file"
    ),
    "effects_demo": Automation(
        id="effects_demo",
        name="Effects Library",
        description="Demo visual effects",
        script="src/effects.py",
        category="Audio & Effects",
        output_type="file"
    ),
    
    # === SEO & STRATEGY ===
    "seo_keywords": Automation(
        id="seo_keywords",
        name="Keyword Research",
        description="Research SEO keywords",
        script="src/seo/keyword_research.py",
        category="SEO & Strategy",
        output_type="json"
    ),
    "content_gap": Automation(
        id="content_gap",
        name="Content Gap Analysis",
        description="Find content opportunities",
        script="src/seo/content_gap.py",
        category="SEO & Strategy",
        output_type="json"
    ),
}


def run_automation(job_id: str, automation: Automation, extra_args: List[str] = None):
    """Run an automation in background thread"""
    global running_jobs, job_logs
    
    script_path = PROJECT_ROOT / automation.script
    if not script_path.exists():
        job_logs[job_id].append(f"❌ Script not found: {automation.script}")
        running_jobs[job_id]['status'] = 'error'
        running_jobs[job_id]['ended_at'] = datetime.now().isoformat()
        return
    
    # Use the venv python and set PYTHONPATH to include src
    venv_python = PROJECT_ROOT / "dashboard" / "venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = sys.executable
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(PROJECT_ROOT / "src") + ":" + env.get('PYTHONPATH', '')
    
    cmd = [str(venv_python), str(script_path)]
    if extra_args:
        cmd.extend(extra_args)
    
    job_logs[job_id].append(f"▶️ Running: {' '.join(cmd)}")
    job_logs[job_id].append(f"📂 Working dir: {PROJECT_ROOT}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env
        )
        
        running_jobs[job_id]['pid'] = process.pid
        
        for line in process.stdout:
            job_logs[job_id].append(line.rstrip())
            if len(job_logs[job_id]) > 500:  # Keep last 500 lines
                job_logs[job_id] = job_logs[job_id][-500:]
        
        process.wait()
        
        if process.returncode == 0:
            job_logs[job_id].append(f"✅ Completed successfully!")
            running_jobs[job_id]['status'] = 'completed'
        else:
            job_logs[job_id].append(f"❌ Failed with exit code: {process.returncode}")
            running_jobs[job_id]['status'] = 'error'
            
    except Exception as e:
        job_logs[job_id].append(f"❌ Error: {str(e)}")
        running_jobs[job_id]['status'] = 'error'
    
    running_jobs[job_id]['ended_at'] = datetime.now().isoformat()


# ============== DASHBOARD HTML ==============
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kiin Automation Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --kiin-primary: #4A90B8;
            --kiin-secondary: #6BB3A0;
            --kiin-accent: #F4A460;
            --kiin-dark: #2C3E50;
        }
        body { background: #f5f7fa; font-family: 'Segoe UI', sans-serif; }
        .navbar { background: linear-gradient(135deg, var(--kiin-primary), var(--kiin-secondary)); }
        .category-card { 
            background: white; 
            border-radius: 12px; 
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }
        .category-header { 
            background: var(--kiin-dark); 
            color: white; 
            padding: 12px 20px;
            border-radius: 12px 12px 0 0;
            font-weight: 600;
        }
        .automation-item {
            padding: 16px 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .automation-item:last-child { border-bottom: none; }
        .automation-info h6 { margin: 0; color: var(--kiin-dark); }
        .automation-info p { margin: 0; font-size: 0.85rem; color: #666; }
        .btn-execute {
            background: var(--kiin-primary);
            border: none;
            padding: 8px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn-execute:hover { background: #3a7a9e; transform: scale(1.02); }
        .btn-execute:disabled { background: #ccc; }
        .status-badge { 
            font-size: 0.75rem; 
            padding: 4px 10px; 
            border-radius: 20px;
            margin-left: 10px;
        }
        .status-running { background: #fff3cd; color: #856404; }
        .status-completed { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }
        .log-panel {
            background: #1e1e1e;
            color: #00ff00;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            padding: 16px;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        .jobs-sidebar {
            position: fixed;
            right: 0;
            top: 60px;
            width: 400px;
            height: calc(100vh - 60px);
            background: white;
            box-shadow: -2px 0 12px rgba(0,0,0,0.1);
            transform: translateX(100%);
            transition: transform 0.3s;
            z-index: 1000;
            overflow-y: auto;
        }
        .jobs-sidebar.open { transform: translateX(0); }
        .jobs-toggle {
            position: fixed;
            right: 20px;
            bottom: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--kiin-accent);
            color: white;
            border: none;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1001;
        }
        .job-count { 
            position: absolute; 
            top: -5px; 
            right: -5px; 
            background: #dc3545;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .quick-stats {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }
        .stat-item { text-align: center; }
        .stat-item h2 { color: var(--kiin-primary); margin: 0; }
        .stat-item p { color: #666; margin: 0; font-size: 0.85rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="bi bi-robot"></i> Kiin Automation Panel
            </span>
            <span class="text-white">{{ automation_count }} Automations Ready</span>
        </div>
    </nav>

    <div class="container-fluid py-4">
        <!-- Quick Stats -->
        <div class="quick-stats">
            <div class="row">
                <div class="col stat-item">
                    <h2 id="total-automations">{{ automation_count }}</h2>
                    <p>Total Automations</p>
                </div>
                <div class="col stat-item">
                    <h2 id="running-count">0</h2>
                    <p>Running Now</p>
                </div>
                <div class="col stat-item">
                    <h2 id="completed-count">0</h2>
                    <p>Completed Today</p>
                </div>
                <div class="col stat-item">
                    <h2>{{ category_count }}</h2>
                    <p>Categories</p>
                </div>
            </div>
        </div>

        <!-- Automation Categories -->
        {% for category, automations in categories.items() %}
        <div class="category-card">
            <div class="category-header">
                <i class="bi bi-folder2-open"></i> {{ category }} ({{ automations|length }})
            </div>
            {% for auto in automations %}
            <div class="automation-item" id="auto-{{ auto.id }}">
                <div class="automation-info">
                    <h6>{{ auto.name }}</h6>
                    <p>{{ auto.description }}</p>
                </div>
                <div>
                    <span class="status-badge" id="status-{{ auto.id }}" style="display:none"></span>
                    <button class="btn-execute" onclick="executeAutomation('{{ auto.id }}')">
                        <i class="bi bi-play-fill"></i> Execute
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    </div>

    <!-- Jobs Sidebar -->
    <div class="jobs-sidebar" id="jobsSidebar">
        <div class="p-3 border-bottom">
            <h5 class="m-0"><i class="bi bi-list-task"></i> Running Jobs</h5>
        </div>
        <div id="jobsList" class="p-3">
            <p class="text-muted">No jobs running</p>
        </div>
    </div>

    <!-- Toggle Button -->
    <button class="jobs-toggle" onclick="toggleJobs()">
        <i class="bi bi-terminal"></i>
        <span class="job-count" id="jobCount" style="display:none">0</span>
    </button>

    <!-- Log Modal -->
    <div class="modal fade" id="logModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="logModalTitle">Job Output</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="log-panel" id="logContent">Loading...</div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let runningJobs = {};
        let completedToday = 0;

        function executeAutomation(id) {
            const btn = document.querySelector(`#auto-${id} .btn-execute`);
            btn.disabled = true;
            btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Starting...';

            fetch('/api/execute/' + id, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        runningJobs[data.job_id] = { id: id, name: data.name };
                        updateJobsList();
                        showStatus(id, 'running', 'Running...');
                        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Running';
                    } else {
                        btn.disabled = false;
                        btn.innerHTML = '<i class="bi bi-play-fill"></i> Execute';
                        alert('Failed to start: ' + data.error);
                    }
                });
        }

        function showStatus(id, status, text) {
            const badge = document.getElementById('status-' + id);
            badge.style.display = 'inline';
            badge.className = 'status-badge status-' + status;
            badge.textContent = text;
        }

        function updateJobsList() {
            fetch('/api/jobs')
                .then(r => r.json())
                .then(jobs => {
                    const list = document.getElementById('jobsList');
                    const running = Object.values(jobs).filter(j => j.status === 'running');
                    
                    document.getElementById('running-count').textContent = running.length;
                    document.getElementById('jobCount').textContent = running.length;
                    document.getElementById('jobCount').style.display = running.length > 0 ? 'flex' : 'none';

                    if (Object.keys(jobs).length === 0) {
                        list.innerHTML = '<p class="text-muted">No jobs running</p>';
                        return;
                    }

                    let html = '';
                    for (const [jobId, job] of Object.entries(jobs)) {
                        const statusClass = job.status === 'running' ? 'warning' : 
                                          job.status === 'completed' ? 'success' : 'danger';
                        html += `
                            <div class="card mb-2">
                                <div class="card-body py-2">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>${job.name}</strong><br>
                                            <small class="text-muted">${job.started_at}</small>
                                        </div>
                                        <div>
                                            <span class="badge bg-${statusClass}">${job.status}</span>
                                            <button class="btn btn-sm btn-outline-secondary ms-2" 
                                                    onclick="showLog('${jobId}', '${job.name}')">
                                                <i class="bi bi-terminal"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;

                        // Update automation status
                        if (job.status !== 'running') {
                            const btn = document.querySelector(`#auto-${job.automation_id} .btn-execute`);
                            if (btn) {
                                btn.disabled = false;
                                btn.innerHTML = '<i class="bi bi-play-fill"></i> Execute';
                            }
                            showStatus(job.automation_id, job.status, 
                                job.status === 'completed' ? 'Done!' : 'Error');
                            
                            if (job.status === 'completed') {
                                completedToday++;
                                document.getElementById('completed-count').textContent = completedToday;
                            }
                        }
                    }
                    list.innerHTML = html;
                });
        }

        function showLog(jobId, name) {
            document.getElementById('logModalTitle').textContent = name + ' - Output';
            const modal = new bootstrap.Modal(document.getElementById('logModal'));
            modal.show();
            
            function updateLog() {
                fetch('/api/log/' + jobId)
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('logContent').textContent = data.log.join('\\n');
                        if (data.status === 'running') {
                            setTimeout(updateLog, 1000);
                        }
                    });
            }
            updateLog();
        }

        function toggleJobs() {
            document.getElementById('jobsSidebar').classList.toggle('open');
        }

        // Poll for updates every 2 seconds
        setInterval(updateJobsList, 2000);
        updateJobsList();
    </script>
</body>
</html>
"""


# ============== API ROUTES ==============

@app.route('/')
def dashboard():
    """Main automation panel"""
    # Group by category
    categories = {}
    for auto in AUTOMATIONS.values():
        if auto.category not in categories:
            categories[auto.category] = []
        categories[auto.category].append(auto)
    
    return render_template_string(
        DASHBOARD_HTML,
        categories=categories,
        automation_count=len(AUTOMATIONS),
        category_count=len(categories)
    )


@app.route('/api/automations')
def api_automations():
    """List all automations"""
    return jsonify({
        auto.id: {
            'name': auto.name,
            'description': auto.description,
            'category': auto.category,
            'script': auto.script
        }
        for auto in AUTOMATIONS.values()
    })


@app.route('/api/execute/<automation_id>', methods=['POST'])
def api_execute(automation_id):
    """Execute an automation"""
    global job_counter
    
    if automation_id not in AUTOMATIONS:
        return jsonify({'success': False, 'error': 'Unknown automation'}), 400
    
    automation = AUTOMATIONS[automation_id]
    job_counter += 1
    job_id = f"job_{job_counter}_{automation_id}"
    
    running_jobs[job_id] = {
        'automation_id': automation_id,
        'name': automation.name,
        'status': 'running',
        'started_at': datetime.now().strftime('%H:%M:%S'),
        'ended_at': None,
        'pid': None
    }
    job_logs[job_id] = []
    
    # Get extra args from request
    extra_args = request.json.get('args', []) if request.is_json else []
    
    # Start in background thread
    thread = threading.Thread(
        target=run_automation,
        args=(job_id, automation, extra_args)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'name': automation.name,
        'message': f'Started {automation.name}'
    })


@app.route('/api/jobs')
def api_jobs():
    """Get all jobs status"""
    return jsonify(running_jobs)


@app.route('/api/log/<job_id>')
def api_log(job_id):
    """Get job log"""
    if job_id not in job_logs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'log': job_logs.get(job_id, []),
        'status': running_jobs.get(job_id, {}).get('status', 'unknown')
    })


@app.route('/api/kill/<job_id>', methods=['POST'])
def api_kill(job_id):
    """Kill a running job"""
    if job_id not in running_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = running_jobs[job_id]
    if job['pid'] and job['status'] == 'running':
        try:
            import signal
            os.kill(job['pid'], signal.SIGTERM)
            job['status'] = 'killed'
            job_logs[job_id].append('⚠️ Job killed by user')
            return jsonify({'success': True})
        except:
            pass
    
    return jsonify({'success': False, 'error': 'Could not kill job'})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5002, help='Port')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎮 KIIN AUTOMATION PANEL")
    print("=" * 60)
    print(f"📍 Dashboard: http://localhost:{args.port}")
    print(f"🤖 Automations: {len(AUTOMATIONS)}")
    print("=" * 60)
    print("Starting server...")
    import sys
    sys.stdout.flush()
    
    app.run(debug=False, host='0.0.0.0', port=args.port, threaded=True)
