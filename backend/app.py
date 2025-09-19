from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import os
from recommendation_engine import RecommendationEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Get the absolute path to the project directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')

# Initialize recommendation engine
rec_engine = RecommendationEngine()

@app.route('/', methods=['GET'])
def home():
    """Always serve frontend for browsers, only return JSON for specific API requests"""
    accept_header = request.headers.get('Accept', '')
    
    # Only return JSON for explicit API requests
    if ('application/json' in accept_header and 'text/html' not in accept_header):
        return jsonify({
            "message": "PM Internship Recommender API",
            "version": "1.0.0",
            "status": "active",
            "frontend_available": os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))
        })
    
    # For everything else (browsers, direct links, etc.), serve frontend
    try:
        # Try multiple paths for index.html
        html_paths = [
            os.path.join(FRONTEND_DIR, 'index.html'),
            './frontend/index.html',
            'frontend/index.html'
        ]
        
        for html_path in html_paths:
            if os.path.exists(html_path):
                return send_file(html_path)
        
        # If none found, show diagnostic page
            # If file not found, create a simple redirect page
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>PM Internship Finder</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body>
                <h1>🎯 PM Internship Finder</h1>
                <p>Loading application...</p>
                <script>
                    console.log('Frontend path issue - redirecting...');
                    // Try to load the main app
                    fetch('/api/sectors')
                        .then(response => response.json())
                        .then(data => {
                            console.log('API working:', data);
                            document.body.innerHTML = '<h1>✅ API Working</h1><p>Frontend files not found. Check deployment.</p>';
                        })
                        .catch(error => {
                            console.error('API Error:', error);
                        });
                </script>
            </body>
            </html>
            ''', 200, {'Content-Type': 'text/html'}
    except Exception as e:
        return jsonify({
            'error': 'Could not serve frontend',
            'message': str(e),
            'debug': {
                'frontend_dir': FRONTEND_DIR,
                'file_exists': os.path.exists(os.path.join(FRONTEND_DIR, 'index.html')),
                'current_dir': os.getcwd(),
                'files_in_frontend': os.listdir(FRONTEND_DIR) if os.path.exists(FRONTEND_DIR) else 'Directory not found'
            }
        }), 200

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    try:
        # Get candidate profile from request
        candidate_data = request.get_json()
        
        # Validate required fields
        required_fields = ['education', 'skills', 'interests', 'location']
        for field in required_fields:
            if field not in candidate_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get recommendations
        recommendations = rec_engine.recommend_internships(candidate_data)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total': len(recommendations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/internships', methods=['GET'])
def get_all_internships():
    try:
        internships = rec_engine.get_all_internships()
        return jsonify({
            'success': True,
            'internships': internships,
            'total': len(internships)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    try:
        sectors = rec_engine.get_available_sectors()
        return jsonify({
            'success': True,
            'sectors': sectors
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/internships/search', methods=['GET'])
def search_internships():
    try:
        # Get query parameters
        sector = request.args.get('sector')
        location = request.args.get('location')
        is_remote = request.args.get('remote', '').lower() == 'true'
        
        # Search internships
        results = rec_engine.search_internships(
            sector=sector,
            location=location,
            is_remote=is_remote
        )
        
        return jsonify({
            'success': True,
            'internships': results,
            'total': len(results),
            'filters': {
                'sector': sector,
                'location': location,
                'remote': is_remote
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/internships/<internship_id>', methods=['GET'])
def get_internship_details(internship_id):
    try:
        internship = rec_engine.get_internship_by_id(internship_id)
        if not internship:
            return jsonify({'error': 'Internship not found'}), 404
        
        return jsonify({
            'success': True,
            'internship': internship
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Debug route to check file structure
@app.route('/debug')
def debug_files():
    """Debug route to check file system structure"""
    debug_info = {
        'current_dir': os.getcwd(),
        'project_root': PROJECT_ROOT,
        'frontend_dir': FRONTEND_DIR,
        'frontend_exists': os.path.exists(FRONTEND_DIR)
    }
    
    if os.path.exists(FRONTEND_DIR):
        debug_info['frontend_files'] = os.listdir(FRONTEND_DIR)
        debug_info['index_html_exists'] = os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))
    
    # Also check current directory
    debug_info['current_dir_files'] = os.listdir('.')
    
    # Check if frontend is in current directory
    if os.path.exists('./frontend'):
        debug_info['local_frontend_files'] = os.listdir('./frontend')
    
    return jsonify(debug_info)

# Static file serving for frontend assets
@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files (CSS, JS, images, etc.)"""
    # Skip API routes
    if filename.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    try:
        # Try FRONTEND_DIR first, then current directory
        if os.path.exists(os.path.join(FRONTEND_DIR, filename)):
            return send_from_directory(FRONTEND_DIR, filename)
        elif os.path.exists(os.path.join('./frontend', filename)):
            return send_from_directory('./frontend', filename)
        else:
            raise FileNotFoundError(f'File {filename} not found in any location')
    except Exception as e:
        # If file not found, return 404
        return jsonify({
            'error': f'File {filename} not found',
            'searched_paths': [FRONTEND_DIR, './frontend'],
            'message': str(e)
        }), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
