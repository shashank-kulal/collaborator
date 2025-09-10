from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'vefogix-mysql-vefogix.d.aivencloud.com'),
    'port': int(os.getenv('DB_PORT', 12345)),
    'database': os.getenv('DB_NAME', 'defaultdb'),
    'user': os.getenv('DB_USER', 'avnadmin'),
    'password': os.getenv('DB_PASSWORD', ''),
    'ssl_disabled': True  # Disable SSL for free hosting compatibility
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

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
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', False))