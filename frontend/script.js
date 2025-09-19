// API Configuration
const API_BASE_URL = 'https://pm-internship-engine.onrender.com/api';

// DOM Elements
const candidateForm = document.getElementById('candidateForm');
const profileForm = document.getElementById('profileForm');
const resultsContainer = document.getElementById('resultsContainer');
const loadingContainer = document.getElementById('loadingContainer');
const recommendationsList = document.getElementById('recommendationsList');

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    setupFormSubmission();
    setupAccessibility();
});

function setupFormSubmission() {
    candidateForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = collectFormData();
        
        // Validate form data
        if (!validateFormData(formData)) {
            return;
        }
        
        // Show loading state
        showLoading();
        
        try {
            // Get recommendations from API
            const recommendations = await getRecommendations(formData);
            
            // Display results
            displayRecommendations(recommendations);
            
        } catch (error) {
            showError(error.message);
        }
    });
}

function collectFormData() {
    const formData = new FormData(candidateForm);
    
    // Collect selected skills
    const selectedSkills = [];
    const skillCheckboxes = document.querySelectorAll('input[name="skills"]:checked');
    skillCheckboxes.forEach(checkbox => {
        selectedSkills.push(checkbox.value);
    });
    
    // Collect selected interests
    const selectedInterests = [];
    const interestCheckboxes = document.querySelectorAll('input[name="interests"]:checked');
    interestCheckboxes.forEach(checkbox => {
        selectedInterests.push(checkbox.value);
    });
    
    return {
        education: formData.get('education'),
        skills: selectedSkills,
        interests: selectedInterests,
        location: formData.get('location')
    };
}

function validateFormData(data) {
    // Check required fields
    if (!data.education) {
        showAlert('Please select your education level');
        return false;
    }
    
    if (!data.location) {
        showAlert('Please select your preferred location');
        return false;
    }
    
    if (data.skills.length === 0) {
        showAlert('Please select at least one skill');
        return false;
    }
    
    if (data.interests.length === 0) {
        showAlert('Please select at least one area of interest');
        return false;
    }
    
    return true;
}

async function getRecommendations(candidateData) {
    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(candidateData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to get recommendations. Please try again.');
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to get recommendations');
        }
        
        return data.recommendations;
        
    } catch (error) {
        // If API is not available, show mock recommendations
        console.warn('API not available, showing mock data:', error.message);
        return getMockRecommendations(candidateData);
    }
}

function getMockRecommendations(candidateData) {
    // Mock recommendations for demonstration
    const mockRecommendations = [
        {
            id: 1,
            title: "Frontend Developer Intern",
            company: "TechCorp India",
            location: "Bangalore",
            duration: "6 months",
            stipend: "₹15,000/month",
            sector: "Technology",
            description: "Work on modern web applications using React and JavaScript",
            requirements: ["Computer Skills", "Communication"],
            match_score: 95,
            match_reason: "Perfect match for your computer skills and technology interest"
        },
        {
            id: 2,
            title: "Digital Marketing Intern",
            company: "Growth Solutions",
            location: "Mumbai",
            duration: "4 months",
            stipend: "₹12,000/month",
            sector: "Marketing",
            description: "Learn social media marketing and content creation",
            requirements: ["Communication", "Computer Skills"],
            match_score: 87,
            match_reason: "Great fit for your communication skills and marketing interests"
        },
        {
            id: 3,
            title: "Data Entry Specialist",
            company: "InfoSys Ltd",
            location: "Remote",
            duration: "3 months",
            stipend: "₹10,000/month",
            sector: "Information Technology",
            description: "Handle data processing and administrative tasks",
            requirements: ["Computer Skills", "Accounting"],
            match_score: 78,
            match_reason: "Matches your computer and accounting skills"
        }
    ];
    
    // Filter based on user preferences
    return mockRecommendations.filter(internship => {
        const skillMatch = candidateData.skills.some(skill => 
            internship.requirements.some(req => req.toLowerCase().includes(skill))
        );
        const locationMatch = candidateData.location === 'any' || 
                            internship.location.toLowerCase().includes(candidateData.location) ||
                            internship.location.toLowerCase() === 'remote';
        
        return skillMatch && locationMatch;
    }).slice(0, 5); // Return top 5 matches
}

function displayRecommendations(recommendations) {
    hideLoading();
    
    if (recommendations.length === 0) {
        showNoResults();
        return;
    }
    
    // Generate HTML for recommendations
    const recommendationsHTML = recommendations.map(internship => 
        createRecommendationCard(internship)
    ).join('');
    
    recommendationsList.innerHTML = recommendationsHTML;
    showResults();
}

function createRecommendationCard(internship) {
    return `
        <div class="recommendation-card">
            <h3>${internship.title}</h3>
            <div class="company">${internship.company}</div>
            
            <div class="details">
                <div class="detail-item">📍 ${internship.location}</div>
                <div class="detail-item">⏰ ${internship.duration}</div>
                <div class="detail-item">💰 ${internship.stipend}</div>
                <div class="detail-item">🏢 ${internship.sector}</div>
            </div>
            
            <div class="match-reason">
                <div class="reason-title">✨ Why this matches you:</div>
                <div class="reason-text">${internship.match_reason}</div>
            </div>
            
            <p style="margin-bottom: 16px; color: #6b7280; font-size: 14px;">
                ${internship.description}
            </p>
            
            <button class="apply-btn" onclick="applyToInternship(${internship.id})">
                🚀 Apply Now
            </button>
        </div>
    `;
}

function applyToInternship(internshipId) {
    // For now, show a simple alert
    showAlert('This will redirect you to the application page. Feature coming soon!');
}

function showLoading() {
    profileForm.style.display = 'none';
    resultsContainer.style.display = 'none';
    loadingContainer.style.display = 'block';
}

function hideLoading() {
    loadingContainer.style.display = 'none';
}

function showResults() {
    profileForm.style.display = 'none';
    resultsContainer.style.display = 'block';
}

function showForm() {
    resultsContainer.style.display = 'none';
    loadingContainer.style.display = 'none';
    profileForm.style.display = 'block';
}

function showNoResults() {
    hideLoading();
    recommendationsList.innerHTML = `
        <div style="text-align: center; padding: 48px 24px; color: #6b7280;">
            <div style="font-size: 48px; margin-bottom: 16px;">😔</div>
            <h3>No matches found</h3>
            <p>Try selecting different skills or interests to find more internships.</p>
        </div>
    `;
    showResults();
}

function showError(message) {
    hideLoading();
    showAlert(message);
}

function showAlert(message) {
    // Create a simple alert modal
    const alertModal = document.createElement('div');
    alertModal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 20px;
    `;
    
    alertModal.innerHTML = `
        <div style="
            background: white;
            border-radius: 12px;
            padding: 24px;
            max-width: 400px;
            width: 100%;
            text-align: center;
        ">
            <div style="font-size: 24px; margin-bottom: 16px;">⚠️</div>
            <h3 style="margin-bottom: 16px; color: #1f2937;">Attention</h3>
            <p style="color: #6b7280; margin-bottom: 24px;">${message}</p>
            <button onclick="this.closest('div').remove()" style="
                background: #4f46e5;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
            ">Okay</button>
        </div>
    `;
    
    document.body.appendChild(alertModal);
    
    // Remove alert after clicking outside
    alertModal.addEventListener('click', function(e) {
        if (e.target === alertModal) {
            alertModal.remove();
        }
    });
}

function setupAccessibility() {
    // Add keyboard navigation support
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Add focus indicators
    const interactiveElements = document.querySelectorAll('button, select, input, .skill-item, .interest-item');
    interactiveElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid #4f46e5';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = 'none';
        });
    });
}

// Make functions globally available
window.showForm = showForm;
window.applyToInternship = applyToInternship;