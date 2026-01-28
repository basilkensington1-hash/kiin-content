# 🎬 Kiin Content Factory Dashboard

A beautiful, intuitive web interface for generating caregiver content videos.

## 🚀 Quick Start

```bash
cd /Users/nick/clawd/kiin-content/dashboard
./run_dashboard.sh
```

The dashboard will open automatically in your browser at `http://localhost:5000`

## 📁 What's Inside

- **`app.py`** - Flask backend with API endpoints
- **`templates/index.html`** - Main dashboard interface
- **`static/style.css`** - Kiin-branded styling
- **`static/script.js`** - Interactive frontend functionality
- **`run_dashboard.sh`** - One-click launcher script

## 🎨 Features

### Content Types
- **You're Not Alone** - Validation Series (Blue)
- **The Quiet Moments** - Caregiver Confessions (Green)
- **Stop Doing This** - Educational Tips (Red)
- **Sandwich Generation Diaries** - POV Content (Purple)
- **Coordination Chaos** - Before/After Stories (Orange)

### Dashboard Features
- ✨ One-click video generation
- 📊 Real-time content statistics
- 🎥 Recent video preview
- 📱 Mobile-responsive design
- 🎉 Success animations and notifications
- ⚡ Auto-refreshing status

## 🎯 How to Use

1. **Launch**: Run `./run_dashboard.sh`
2. **Generate**: Click any "Generate Video" button
3. **Watch**: Monitor progress with real-time notifications
4. **Review**: Check recent videos in the activity feed
5. **Share**: Videos are saved to `/output/` directory

## 🛠️ Technical Details

### API Endpoints
- `GET /` - Main dashboard
- `POST /api/generate/<type>` - Generate content
- `GET /api/status` - Get content statistics
- `GET /api/videos` - List recent videos

### Content Types
- `validation` - Validation messages
- `confessions` - Caregiver confessions
- `tips` - Educational tips
- `sandwich` - Sandwich generation stories
- `chaos` - Coordination scenarios

## 🎨 Design System

### Colors (Kiin Brand)
- **Primary Blue**: #4A90E2
- **Secondary Green**: #50C878
- **Accent Teal**: #7ED3C3
- **Soft Blue**: #E8F4FD
- **Soft Green**: #F0FDF4

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

## 📝 Customization

### Adding New Content Types
1. Update `CONTENT_TYPES` in `app.py`
2. Add new generator logic to `/api/generate/<type>`
3. Update frontend colors and descriptions
4. Add corresponding JSON config file

### Styling Changes
- Edit `static/style.css` for visual changes
- Modify CSS variables at the top for global theme changes
- Update `static/script.js` for behavior changes

## 🔧 Troubleshooting

### Port Already in Use
The launcher automatically tries port 5001 if 5000 is busy.

### Missing Dependencies
The launcher checks and installs Flask automatically.

### Virtual Environment Issues
Delete `/venv/` and re-run the launcher to rebuild.

### Generator Errors
Check the main project's `requirements.txt` is installed.

---

**Made with ❤️ for the caregiver community**