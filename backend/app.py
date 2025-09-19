from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from recommendation_engine import RecommendationEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize recommendation engine
rec_engine = RecommendationEngine()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "PM Internship Recommender API",
        "version": "1.0.0",
        "status": "active"
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
