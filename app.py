# app.py - Flask Backend for Blog Website (Vercel Compatible)
from flask import Flask, request, jsonify, render_template, send_from_directory
import os, json, uuid, base64
from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict

app = Flask(__name__)

# Vercel-compatible paths - use /tmp for temporary storage
BLOG_DIR = "/tmp/blogs" if os.environ.get('VERCEL') else "blogs"
IMAGES_DIR = "/tmp/static/images/blogs" if os.environ.get('VERCEL') else "static/images/blogs"
DB_PATH = "/tmp/analytics.db" if os.environ.get('VERCEL') else "analytics.db"

# Analytics Database Setup
def init_analytics_db():
    # Ensure directories exist
    os.makedirs(BLOG_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Page views table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            visitor_ip TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT
        )
    ''')
    
    # Blog posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_posts (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT,
            views INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            post_count INTEGER DEFAULT 0,
            total_views INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_analytics_db()

# Analytics tracking middleware
@app.before_request
def track_page_view():
    if request.endpoint and 'static' not in request.endpoint:
        page_name = request.endpoint.replace('_page', '').replace('_', '')
        if page_name == 'home':
            page_name = 'index'
        
        visitor_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        session_id = request.cookies.get('session_id', str(uuid.uuid4()))
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO page_views (page_name, visitor_ip, user_agent, session_id)
            VALUES (?, ?, ?, ?)
        ''', (page_name, visitor_ip, user_agent, session_id))
        conn.commit()
        conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/blog")
def write_blog():
    return render_template("blog.html")

@app.route("/architecture")
def architecture_page():
    return render_template("architecture.html")

@app.route("/sculpture")
def sculpture_page():
    return render_template("sculpture.html")

@app.route("/sciences")
def sciences_page():
    return render_template("sciences.html")

@app.route("/blogs")
def view_blogs():
    return render_template("blogs.html")

# Analytics API Endpoints
@app.route("/api/analytics/overview")
def get_analytics_overview():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total page views (last 30 days)
    cursor.execute('''
        SELECT COUNT(*) FROM page_views 
        WHERE timestamp >= datetime('now', '-30 days')
    ''')
    total_views = cursor.fetchone()[0]
    
    # Unique visitors (last 30 days)
    cursor.execute('''
        SELECT COUNT(DISTINCT visitor_ip) FROM page_views 
        WHERE timestamp >= datetime('now', '-30 days')
    ''')
    unique_visitors = cursor.fetchone()[0]
    
    # Page views by page
    cursor.execute('''
        SELECT page_name, COUNT(*) as views FROM page_views 
        WHERE timestamp >= datetime('now', '-30 days')
        GROUP BY page_name
        ORDER BY views DESC
    ''')
    page_stats = dict(cursor.fetchall())
    
    # Blog posts count
    cursor.execute('SELECT COUNT(*) FROM blog_posts')
    blog_posts = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'blog_posts': blog_posts,
        'page_stats': page_stats
    })

@app.route("/api/analytics/page/<page_name>")
def get_page_analytics(page_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Page views for specific page
    cursor.execute('''
        SELECT COUNT(*) FROM page_views 
        WHERE page_name = ? AND timestamp >= datetime('now', '-30 days')
    ''', (page_name,))
    views = cursor.fetchone()[0]
    
    # Today's views
    cursor.execute('''
        SELECT COUNT(*) FROM page_views 
        WHERE page_name = ? AND date(timestamp) = date('now')
    ''', (page_name,))
    today_views = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'page_name': page_name,
        'total_views': views,
        'today_views': today_views
    })

@app.route("/api/analytics/categories")
def get_category_analytics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get category stats
    cursor.execute('''
        SELECT name, post_count, total_views FROM categories
        ORDER BY total_views DESC
    ''')
    categories = []
    for row in cursor.fetchall():
        categories.append({
            'name': row[0],
            'post_count': row[1],
            'total_views': row[2]
        })
    
    conn.close()
    return jsonify(categories)

@app.route("/api/analytics/realtime")
def get_realtime_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Current online users (last 5 minutes)
    cursor.execute('''
        SELECT COUNT(DISTINCT visitor_ip) FROM page_views 
        WHERE timestamp >= datetime('now', '-5 minutes')
    ''')
    online_users = cursor.fetchone()[0]
    
    # Today's page views
    cursor.execute('''
        SELECT COUNT(*) FROM page_views 
        WHERE date(timestamp) = date('now')
    ''')
    today_views = cursor.fetchone()[0]
    
    # This week's page views
    cursor.execute('''
        SELECT COUNT(*) FROM page_views 
        WHERE timestamp >= datetime('now', '-7 days')
    ''')
    week_views = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'online_users': online_users,
        'today_views': today_views,
        'week_views': week_views
    })

# Utility function to save base64 images to files
def save_image_from_base64(image_data, blog_id):
    """Save a base64 image to the file system and return the relative path."""
    try:
        # Extract the image data and format
        if ',' in image_data:
            header, data = image_data.split(',', 1)
            # Extract file extension from header (e.g., "data:image/jpeg;base64")
            if 'image/jpeg' in header:
                ext = '.jpg'
            elif 'image/png' in header:
                ext = '.png'
            elif 'image/webp' in header:
                ext = '.webp'
            else:
                ext = '.jpg'  # default
        else:
            data = image_data
            ext = '.jpg'
        
        # Generate unique filename
        image_id = str(uuid.uuid4())
        filename = f"{blog_id}_{image_id}{ext}"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Decode and save the image
        image_bytes = base64.b64decode(data)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Return relative path for web access
        return f"static/images/blogs/{filename}"
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

# Route to serve uploaded images
@app.route('/static/images/blogs/<filename>')
def serve_blog_image(filename):
    return send_from_directory(IMAGES_DIR, filename)

# Util: Load All Blogs
@app.route("/api/blogs")
def get_blogs():
    blogs = []
    try:
        for filename in os.listdir(BLOG_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(BLOG_DIR, filename)) as f:
                    blog = json.load(f)
                    blog['id'] = filename.replace(".json", "")
                    blogs.append(blog)
        blogs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    except Exception as e:
        print(f"Error loading blogs: {e}")
        # Return empty list if directory doesn't exist or other errors
        pass
    return jsonify(blogs)

# Util: Get Single Blog
@app.route("/api/blogs/<blog_id>")
def get_blog(blog_id):
    path = os.path.join(BLOG_DIR, f"{blog_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Not found"}), 404

# Save Blog (Draft or Publish)
@app.route("/api/blogs", methods=["POST"])
def save_blog():
    data = request.json
    blog_id = data.get("id") or str(uuid.uuid4())
    
    # Process images - convert base64 to file paths
    processed_images = []
    for image in data.get("images", []):
        if image.get("data") and image["data"].startswith("data:image"):
            # Save base64 image to file system
            saved_path = save_image_from_base64(image["data"], blog_id)
            if saved_path:
                processed_images.append({
                    "id": image.get("id"),
                    "name": image.get("name", ""),
                    "caption": image.get("caption", ""),
                    "path": saved_path,
                    "type": image.get("type", "image/jpeg")
                })
        elif image.get("path"):
            # Image already saved, keep existing data
            processed_images.append(image)
    
    blog_data = {
        "title": data["title"],
        "subtitle": data.get("subtitle", ""),
        "content": data["content"],
        "category": data.get("category", "general"),
        "tags": data.get("tags", []),
        "images": processed_images,
        "published": data.get("published", False),
        "created_at": data.get("created_at") or datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Save to JSON file
    with open(os.path.join(BLOG_DIR, f"{blog_id}.json"), "w") as f:
        json.dump(blog_data, f, indent=2)
    
    # Update analytics database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert or update blog post
    cursor.execute('''
        INSERT OR REPLACE INTO blog_posts (id, title, category, created_at)
        VALUES (?, ?, ?, ?)
    ''', (blog_id, blog_data["title"], blog_data["category"], blog_data["created_at"]))
    
    # Update category stats
    category = blog_data["category"]
    cursor.execute('''
        INSERT OR IGNORE INTO categories (name) VALUES (?)
    ''', (category,))
    
    cursor.execute('''
        UPDATE categories SET post_count = (
            SELECT COUNT(*) FROM blog_posts WHERE category = ?
        ) WHERE name = ?
    ''', (category, category))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "id": blog_id})

# Delete Blog
@app.route("/api/blogs/<blog_id>", methods=["DELETE"])
def delete_blog(blog_id):
    path = os.path.join(BLOG_DIR, f"{blog_id}.json")
    if os.path.exists(path):
        os.remove(path)
        
        # Update analytics database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get category before deleting
        cursor.execute('SELECT category FROM blog_posts WHERE id = ?', (blog_id,))
        result = cursor.fetchone()
        if result:
            category = result[0]
            
            # Delete from blog_posts
            cursor.execute('DELETE FROM blog_posts WHERE id = ?', (blog_id,))
            
            # Update category count
            cursor.execute('''
                UPDATE categories SET post_count = (
                    SELECT COUNT(*) FROM blog_posts WHERE category = ?
                ) WHERE name = ?
            ''', (category, category))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404

# Vercel requires this for serverless deployment
app.debug = False

if __name__ == "__main__":
    app.run(debug=True)