from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, Website, WebsiteBadge, WebsiteCategory, WebsiteContrCategory, WebsitePrice, WebsiteSEOMetric, WebsiteTraffic, WebsiteTrafficGeo
from config import Config
import pandas as pd
import json
from sqlalchemy import or_
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)  # Enable CORS for all routes

# Database configuration from environment variables for MySQL
# Update the DB_CONFIG to use app.config values
DB_CONFIG = {
    'host': app.config['DB_HOST'],
    'port': app.config['DB_PORT'],
    'database': app.config['DB_NAME'],
    'user': app.config['DB_USER'],
    'password': app.config['DB_PASSWORD']
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Define available columns for the table view
AVAILABLE_COLUMNS = {
    'name': 'Website Name',
    'url': 'URL',
    'countries': 'Countries',
    'language': 'Language',
    'rating_text': 'Rating',
    'count_review': 'Review Count',
    'domain_age': 'Domain Age',
    'domain_zone': 'Domain Zone',
    'speed': 'Speed',
    'amount_total_deals': 'Total Deals'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/websites')
def website_list():
    # Check if this is an export request
    if request.args.get('export'):
        return website_export()
    
    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    # Get selected columns for table view
    selected_columns = request.args.getlist('columns')
    if not selected_columns:
        selected_columns = ['name', 'url', 'countries', 'language']  # Default columns
    
    # Build query with filters
    query = Website.query
    
    # Search filter
    if search:
        query = query.filter(or_(
            Website.name.ilike(f'%{search}%'),
            Website.url.ilike(f'%{search}%'),
            Website.countries.ilike(f'%{search}%')
        ))
    
    # Filter by category if provided
    category = request.args.get('category')
    if category:
        query = query.join(WebsiteCategory).filter(WebsiteCategory.category_name == category)
    
    # Filter by country if provided
    country = request.args.get('country')
    if country:
        query = query.filter(Website.countries.ilike(f'%{country}%'))
    
    # Filter by language if provided
    language = request.args.get('language')
    if language:
        query = query.filter(Website.language == language)
    
    # Filter by announcement type
    announcement_type = request.args.get('announcement_type')
    if announcement_type == 'free':
        query = query.filter(Website.is_free_announcement == True)
    elif announcement_type == 'paid':
        query = query.filter(Website.is_paid_announcement == True)
    
    # Get paginated results
    websites = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get unique values for filter dropdowns
    categories = WebsiteCategory.query.with_entities(WebsiteCategory.category_name).distinct().all()
    countries = Website.query.with_entities(Website.countries).filter(Website.countries.isnot(None)).distinct().all()
    languages = Website.query.with_entities(Website.language).filter(Website.language.isnot(None)).distinct().all()
    
    # Process countries (they are stored as comma-separated values)
    country_list = set()
    for country in countries:
        if country[0]:
            for c in country[0].split(','):
                country_list.add(c.strip())
    
    # Remove 'page' from request.args for safe pagination links
    request_args_no_page = {k: v for k, v in request.args.items() if k != 'page'}
    return render_template('website_list.html', 
                         websites=websites,
                         categories=[c[0] for c in categories],
                         countries=sorted(country_list),
                         languages=[l[0] for l in languages],
                         available_columns=AVAILABLE_COLUMNS,
                         selected_columns=selected_columns,
                         search=search,
                         request_args_no_page=request_args_no_page)

@app.route('/website/<int:website_id>')
def website_detail(website_id):
    website = Website.query.get_or_404(website_id)
    return render_template('website_detail.html', website=website)

@app.route('/charts')
def charts():
    return render_template('charts.html')

@app.route('/api/seo_metrics')
def api_seo_metrics():
    # Get top websites by various SEO metrics
    limit = request.args.get('limit', 10, type=int)
    
    metrics_data = {
        'ahrefs_dr': Website.query.join(WebsiteSEOMetric).filter(
            WebsiteSEOMetric.ahrefs_dr.isnot(None)
        ).order_by(WebsiteSEOMetric.ahrefs_dr.desc()).limit(limit).all(),
        'ahrefs_traffic': Website.query.join(WebsiteSEOMetric).filter(
            WebsiteSEOMetric.ahrefs_traffic.isnot(None)
        ).order_by(WebsiteSEOMetric.ahrefs_traffic.desc()).limit(limit).all(),
        'da_moz': Website.query.join(WebsiteSEOMetric).filter(
            WebsiteSEOMetric.da_moz.isnot(None)
        ).order_by(WebsiteSEOMetric.da_moz.desc()).limit(limit).all()
    }
    
    # Prepare data for charts
    charts_data = {}
    for metric, websites in metrics_data.items():
        charts_data[metric] = {
            'names': [w.name for w in websites],
            'values': [getattr(w.seo_metrics.first(), metric) for w in websites if w.seo_metrics.first()]
        }
    
    return jsonify(charts_data)

@app.route('/websites/export')
def website_export():
    # Get filter parameters (same as website_list)
    search = request.args.get('search', '')
    
    # Build query with filters
    query = Website.query
    
    # Search filter
    if search:
        query = query.filter(or_(
            Website.name.ilike(f'%{search}%'),
            Website.url.ilike(f'%{search}%'),
            Website.countries.ilike(f'%{search}%')
        ))
    
    # Filter by category if provided
    category = request.args.get('category')
    if category:
        query = query.join(WebsiteCategory).filter(WebsiteCategory.category_name == category)
    
    # Filter by country if provided
    country = request.args.get('country')
    if country:
        query = query.filter(Website.countries.ilike(f'%{country}%'))
    
    # Filter by language if provided
    language = request.args.get('language')
    if language:
        query = query.filter(Website.language == language)
    
    # Filter by announcement type
    announcement_type = request.args.get('announcement_type')
    if announcement_type == 'free':
        query = query.filter(Website.is_free_announcement == True)
    elif announcement_type == 'paid':
        query = query.filter(Website.is_paid_announcement == True)
    
    # Get all results (no pagination for export)
    websites = query.all()
    
    # Get selected columns
    selected_columns = request.args.getlist('columns')
    if not selected_columns:
        selected_columns = ['name', 'url', 'countries', 'language']
    
    # Prepare data for export
    data = []
    for website in websites:
        item = {}
        for col in selected_columns:
            if col == 'name':
                item['name'] = website.name
            elif col == 'url':
                item['url'] = website.url
            elif col == 'countries':
                item['countries'] = website.countries
            elif col == 'language':
                item['language'] = website.language
            elif col == 'rating_text':
                item['rating'] = website.rating_text
            elif col == 'count_review':
                item['review_count'] = website.count_review
            elif col == 'domain_age':
                item['domain_age'] = website.domain_age
            elif col == 'domain_zone':
                item['domain_zone'] = website.domain_zone
            elif col == 'speed':
                item['speed'] = website.speed
            elif col == 'amount_total_deals':
                item['total_deals'] = website.amount_total_deals
        data.append(item)
    
    # Handle different export formats
    export_format = request.args.get('export', 'csv')
    
    if export_format == 'json':
        return jsonify(data)
    else:  # CSV
        import csv
        from io import StringIO
        
        si = StringIO()
        if data:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(si, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        output = si.getvalue()
        si.close()
        
        response = app.response_class(
            response=output,
            status=200,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=websites_export.csv'}
        )
        return response

@app.route('/api/traffic_sources')
def api_traffic_sources():
    # Get traffic sources distribution
    website_id = request.args.get('website_id', type=int)
    
    if website_id:
        traffic_data = WebsiteTraffic.query.filter_by(website_id=website_id).all()
        return jsonify({
            'sources': [t.traffic_source for t in traffic_data],
            'values': [float(t.value_clean) for t in traffic_data if t.value_clean]
        })
    
    return jsonify({'error': 'Website ID required'}), 400

@app.route('/api/geo_distribution')
def api_geo_distribution():
    # Get geographical distribution for a website
    website_id = request.args.get('website_id', type=int)
    
    if website_id:
        geo_data = WebsiteTrafficGeo.query.filter_by(website_id=website_id).all()
        return jsonify({
            'countries': [g.country_name for g in geo_data],
            'percentages': [float(g.percent_clean) for g in geo_data if g.percent_clean]
        })
    
    return jsonify({'error': 'Website ID required'}), 400

# New API endpoints from the provided code
@app.route('/api', methods=['GET'])
def api_search():
    website_name = request.args.get('name')
    
    if not website_name:
        return jsonify({
            "status": "error",
            "message": "Website name parameter is required. Use ?name=website.com",
            "code": 400
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "status": "error",
            "message": "Database connection failed",
            "code": 500
        }), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # First get basic website info
        query_basic = "SELECT * FROM websites WHERE name = %s OR url = %s OR external_url = %s LIMIT 1"
        cursor.execute(query_basic, (website_name, website_name, website_name))
        website = cursor.fetchone()
        
        if not website:
            return jsonify({
                "status": "error",
                "message": f"No website found with name: {website_name}",
                "code": 404,
                "search_term": website_name
            }), 404
        
        # Get related data from other tables
        website_id = website['id']
        
        # Get badges
        cursor.execute("SELECT * FROM website_badges WHERE website_id = %s", (website_id,))
        badges = cursor.fetchall()
        
        # Get categories
        cursor.execute("SELECT * FROM website_categories WHERE website_id = %s", (website_id,))
        categories = cursor.fetchall()
        
        # Get contributor categories
        cursor.execute("SELECT * FROM website_contr_categories WHERE website_id = %s", (website_id,))
        contr_categories = cursor.fetchall()
        
        # Get prices
        cursor.execute("SELECT * FROM website_prices WHERE website_id = %s", (website_id,))
        prices = cursor.fetchall()
        
        # Get traffic
        cursor.execute("SELECT * FROM website_traffic WHERE website_id = %s", (website_id,))
        traffic = cursor.fetchall()
        
        # Get traffic geo
        cursor.execute("SELECT * FROM website_traffic_geo WHERE website_id = %s", (website_id,))
        traffic_geo = cursor.fetchall()
        
        # Get SEO metrics
        cursor.execute("SELECT * FROM website_seo_metrics WHERE website_id = %s", (website_id,))
        seo_metrics = cursor.fetchone()  # Assuming one record per website
        
        result = {
            **website,
            "badges": badges,
            "categories": categories,
            "contr_categories": contr_categories,
            "prices": prices,
            "traffic": traffic,
            "traffic_geo": traffic_geo,
            "seo_metrics": seo_metrics
        }
        
        return jsonify({
            "status": "success",
            "code": 200,
            "search_term": website_name,
            "data": result
        })
        
    except Error as e:
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}",
            "code": 500
        }), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', True))