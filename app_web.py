import threading
from flask import Flask, render_template, jsonify, request
from core.db import get_dashboard_data, mark_as_read, get_sources, add_source, delete_source, get_sources_with_counts, update_source
from pipeline import run_pipeline
from core.summarizer import generate_daily_summary
import pandas as pd

app = Flask(__name__)

# Global status to track if pipeline is running
pipeline_status = {"running": False}

def background_pipeline():
    pipeline_status["running"] = True
    try:
        run_pipeline()
    finally:
        pipeline_status["running"] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pipeline/status')
def api_pipeline_status():
    return jsonify(pipeline_status)

@app.route('/api/pipeline/run', methods=['POST'])
def api_run_pipeline():
    if not pipeline_status["running"]:
        thread = threading.Thread(target=background_pipeline)
        thread.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already_running"})

@app.route('/api/insights')
def api_insights():
    # 1. Get raw data
    data = get_dashboard_data()
    # 2. Get official sources to map names and categories
    db_sources = get_sources()
    # Map: URL -> {name, category}
    official_map = {}
    for s in db_sources:
        # Use registered name or clean domain as fallback
        name = s.name if s.name else s.url.split('//')[-1].split('/')[0].replace('www.', '')
        official_map[s.url] = {"name": name, "category": s.category}

    insights = []
    for row in data:
        item = dict(row._mapping)
        if item.get('created_at'):
            item['created_at'] = item['created_at'].isoformat()
        
        if item.get('published_at'):
            item['published_at'] = item['published_at'].strftime('%Y-%m-%d %H:%M')
        
        # Determine type for icon/badge logic
        raw_source = item['source']
        if raw_source.startswith("YouTube: "): item['type'] = "YouTube"
        elif raw_source.startswith("Scraper: "): item['type'] = "Scraper"
        elif raw_source.startswith("GitHub: "): item['type'] = "GitHub"
        else: item['type'] = "RSS"

        # FORCE OFFICIAL NAME AND CATEGORY
        # This cleans up any "garbage" names from old runs
        matched = False
        for url, meta in official_map.items():
            if url in item['url']: # Check if the article URL belongs to a source URL
                item['source'] = meta['name']
                item['category'] = meta['category']
                matched = True
                break
        
        if not matched:
            # Fallback if no source matches perfectly
            item['source'] = raw_source.replace("Scraper: ", "").replace("YouTube: ", "").split(" - ")[0]
            item['category'] = "General"

        insights.append(item)
    
    return jsonify(insights)

@app.route('/api/read/<int:insight_id>', methods=['POST'])
def api_mark_read(insight_id):
    mark_as_read(insight_id)
    return jsonify({"status": "success"})

@app.route('/api/sources')
def api_get_sources():
    db_sources = get_sources_with_counts()
    return jsonify(db_sources)

@app.route('/api/sources', methods=['POST'])
def api_add_source():
    data = request.json
    url = data.get('url')
    stype = data.get('type')
    category = data.get('category', 'General')
    limit = int(data.get('limit', 10))
    name = data.get('name', '')
    
    if not url or not stype:
        return jsonify({"status": "error", "message": "Missing URL or Type"}), 400
        
    success = add_source(url, stype, category, limit, name)
    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Source already exists"}), 400

@app.route('/api/sources/update/<int:source_id>', methods=['POST'])
def api_update_source(source_id):
    data = request.json
    # Clean up data to only include valid columns
    valid_fields = ['url', 'type', 'category', 'item_limit', 'name']
    update_data = {k: v for k, v in data.items() if k in valid_fields}
    
    if 'item_limit' in update_data:
        update_data['item_limit'] = int(update_data['item_limit'])
        
    update_source(source_id, **update_data)
    return jsonify({"status": "success"})

@app.route('/api/sources/delete/<int:source_id>', methods=['POST'])
def api_delete_source(source_id):
    delete_source(source_id)
    return jsonify({"status": "success"})

@app.route('/api/summary/daily')
def api_daily_summary():
    summary = generate_daily_summary()
    return jsonify(summary)

if __name__ == '__main__':
    # Start pipeline once on startup
    print("🚀 Initializing Pipeline Thread...")
    startup_thread = threading.Thread(target=background_pipeline)
    startup_thread.start()
    
    print("🚀 InsightEngine Web Server starting at http://127.0.0.1:5001")
    app.run(debug=False, port=5001) # Debug=False to avoid double thread start
