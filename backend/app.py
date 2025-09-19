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
    """Serve HTML application"""
    return get_html_app()

# Function to generate HTML app
def get_html_app():
    """Return the complete HTML application"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PM Internship Finder</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #4f46e5; font-size: 2em; margin-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 8px; color: #333; }
        select, input { width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; }
        .skills-grid, .interests-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px; }
        .skill-item, .interest-item { display: flex; align-items: center; padding: 10px; border: 2px solid #e5e7eb; border-radius: 8px; cursor: pointer; }
        .skill-item input, .interest-item input { width: auto; margin-right: 8px; }
        .submit-btn { width: 100%; padding: 15px; background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        .results { margin-top: 30px; }
        .card { background: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 2px solid #e5e7eb; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 PM Internship Finder</h1>
            <p>Find internships that match your skills</p>
        </div>
        
        <form id="internshipForm">
            <div class="form-group">
                <label>📚 Your Education Level</label>
                <select name="education" required>
                    <option value="">Choose your level</option>
                    <option value="10th">10th Pass</option>
                    <option value="12th">12th Pass</option>
                    <option value="diploma">Diploma</option>
                    <option value="undergraduate">Bachelor's Degree</option>
                    <option value="postgraduate">Master's Degree</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>💡 Your Skills (Select all that apply)</label>
                <div class="skills-grid">
                    <label class="skill-item"><input type="checkbox" name="skills" value="computer"> 💻 Computer Skills</label>
                    <label class="skill-item"><input type="checkbox" name="skills" value="communication"> 🗣️ Communication</label>
                    <label class="skill-item"><input type="checkbox" name="skills" value="design"> 🎨 Design</label>
                    <label class="skill-item"><input type="checkbox" name="skills" value="accounting"> 📊 Accounting</label>
                </div>
            </div>
            
            <div class="form-group">
                <label>🎯 Which sectors interest you?</label>
                <div class="interests-grid">
                    <label class="interest-item"><input type="checkbox" name="interests" value="technology"> 💻 Technology</label>
                    <label class="interest-item"><input type="checkbox" name="interests" value="healthcare"> 🏥 Healthcare</label>
                    <label class="interest-item"><input type="checkbox" name="interests" value="education"> 📚 Education</label>
                    <label class="interest-item"><input type="checkbox" name="interests" value="finance"> 💰 Finance</label>
                </div>
            </div>
            
            <div class="form-group">
                <label>📍 Your Preferred Location</label>
                <select name="location" required>
                    <option value="">Choose location</option>
                    <option value="mumbai">Mumbai</option>
                    <option value="delhi">Delhi</option>
                    <option value="bangalore">Bangalore</option>
                    <option value="chennai">Chennai</option>
                    <option value="remote">Work from Home</option>
                </select>
            </div>
            
            <button type="submit" class="submit-btn">🔍 Find My Internships</button>
        </form>
        
        <div id="results" class="results hidden"></div>
    </div>
    
    <script>
        document.getElementById('internshipForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const skills = Array.from(formData.getAll('skills'));
            const interests = Array.from(formData.getAll('interests'));
            
            const candidateData = {
                education: formData.get('education'),
                skills: skills,
                interests: interests,
                location: formData.get('location')
            };
            
            try {
                const response = await fetch('/api/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(candidateData)
                });
                
                const data = await response.json();
                const resultsDiv = document.getElementById('results');
                
                if (data.success && data.recommendations.length > 0) {
                    const html = data.recommendations.map(rec => `
                        <div class="card">
                            <h3>${rec.title}</h3>
                            <p><strong>${rec.company}</strong></p>
                            <p>📍 ${rec.location} | ⏰ ${rec.duration} | 💰 ${rec.stipend}</p>
                            <p>${rec.description}</p>
                            <p style="background: #ecfdf5; padding: 10px; border-radius: 5px;">✨ ${rec.match_reason}</p>
                        </div>
                    `).join('');
                    
                    resultsDiv.innerHTML = '<h2>✨ Perfect Matches for You</h2>' + html;
                    resultsDiv.classList.remove('hidden');
                } else {
                    resultsDiv.innerHTML = '<h2>No matches found</h2><p>Try adjusting your preferences.</p>';
                    resultsDiv.classList.remove('hidden');
                }
            } catch (error) {
                document.getElementById('results').innerHTML = '<h2>Error</h2><p>Could not load recommendations. Please try again.</p>';
                document.getElementById('results').classList.remove('hidden');
            }
        });
    </script>
</body>
</html>
        ''', 200, {'Content-Type': 'text/html; charset=utf-8'}

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

# Explicit HTML route for testing
@app.route('/app')
def serve_app():
    """Explicit HTML route that always works"""
    return get_html_app()

# API status route
@app.route('/api-status')
def api_status():
    """Explicit API status endpoint"""
    return jsonify({
        "message": "PM Internship Recommender API",
        "version": "1.0.0",
        "status": "active",
        "frontend_available": True
    })

# Debug route to check file structure
@app.route('/debug')
def debug_files():
    """Debug route to check file system structure"""
    try:
        debug_info = {
            'current_dir': os.getcwd(),
            'project_root': PROJECT_ROOT,
            'frontend_dir': FRONTEND_DIR,
            'frontend_exists': os.path.exists(FRONTEND_DIR)
        }
        
        try:
            debug_info['current_dir_files'] = os.listdir('.')
        except Exception as e:
            debug_info['current_dir_error'] = str(e)
        
        if os.path.exists(FRONTEND_DIR):
            try:
                debug_info['frontend_files'] = os.listdir(FRONTEND_DIR)
                debug_info['index_html_exists'] = os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))
            except Exception as e:
                debug_info['frontend_error'] = str(e)
        
        # Check if frontend is in current directory
        if os.path.exists('./frontend'):
            try:
                debug_info['local_frontend_files'] = os.listdir('./frontend')
            except Exception as e:
                debug_info['local_frontend_error'] = str(e)
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': 'Debug route failed', 'message': str(e)})

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
