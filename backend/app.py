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
    """Serve frontend or API status based on Accept header"""
    # If request accepts HTML, serve frontend
    if 'text/html' in request.headers.get('Accept', ''):
        try:
            return send_file(os.path.join(FRONTEND_DIR, 'index.html'))
        except Exception as e:
            return jsonify({
                'error': 'Frontend not found',
                'message': str(e),
                'api_status': 'active'
            }), 200
    
    # Otherwise, return API status (for API testing)
    return jsonify({
        "message": "PM Internship Recommender API",
        "version": "1.0.0",
        "status": "active",
        "frontend_available": os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))
    })

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

# Static file serving for frontend assets
@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files (CSS, JS, images, etc.)"""
    # Skip API routes
    if filename.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    try:
        return send_from_directory(FRONTEND_DIR, filename)
    except Exception as e:
        # If file not found, return 404
        return jsonify({'error': f'File {filename} not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
