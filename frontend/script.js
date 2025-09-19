// API Configuration - Use relative URLs for unified deployment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:5000/api'  // Local development
    : '/api';  // Production: same domain as frontend

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
    registerServiceWorker();
    loadSavedPreferences();
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
    
    const userData = {
        education: formData.get('education'),
        skills: selectedSkills,
        interests: selectedInterests,
        location: formData.get('location')
    };
    
    // Save preferences to localStorage
    saveUserPreferences(userData);
    
    return userData;
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
            if (response.status === 503) {
                // Offline response from service worker
                const errorData = await response.json();
                if (errorData.offline) {
                    showOfflineNotification();
                    return getMockRecommendations(candidateData);
                }
            }
            throw new Error('Failed to get recommendations. Please try again.');
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to get recommendations');
        }
        
        return data.recommendations;
        
    } catch (error) {
        // Check if we're offline
        if (!navigator.onLine) {
            showOfflineNotification();
            return getMockRecommendations(candidateData);
        }
        
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
    
    // Save recommendations for sharing
    try {
        localStorage.setItem('lastRecommendations', JSON.stringify(recommendations));
    } catch (error) {
        console.warn('Could not save recommendations:', error);
    }
    
    // Generate HTML for recommendations
    const recommendationsHTML = recommendations.map(internship => 
        createRecommendationCard(internship)
    ).join('');
    
    recommendationsList.innerHTML = recommendationsHTML;
    showResults();
}

function createRecommendationCard(internship) {
    const isRemote = internship.is_remote;
    const hasDeadline = internship.application_deadline;
    const matchScore = internship.match_score || 0;
    const skillsOffered = internship.skills_offered || [];
    const benefits = internship.benefits || [];
    
    // Calculate urgency based on deadline
    let urgencyClass = '';
    let urgencyText = '';
    if (hasDeadline) {
        const deadline = new Date(hasDeadline);
        const now = new Date();
        const daysLeft = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));
        
        if (daysLeft <= 7) {
            urgencyClass = 'urgent';
            urgencyText = `⚡ Only ${daysLeft} days left!`;
        } else if (daysLeft <= 30) {
            urgencyClass = 'moderate';
            urgencyText = `⏳ ${daysLeft} days remaining`;
        }
    }
    
    return `
        <div class="recommendation-card fade-in" style="animation-delay: ${Math.random() * 0.3}s">
            <div class="card-header">
                <div class="title-section">
                    <h3>${internship.title}</h3>
                    <div class="company">${internship.company}</div>
                </div>
                <div class="match-score">
                    <div class="score-circle">${matchScore}%</div>
                    <div class="score-label">Match</div>
                </div>
            </div>
            
            ${urgencyText ? `<div class="urgency ${urgencyClass}">${urgencyText}</div>` : ''}
            
            <div class="details">
                <div class="detail-item">📍 ${internship.location}${isRemote ? ' (Remote)' : ''}</div>
                <div class="detail-item">⏰ ${internship.duration}</div>
                <div class="detail-item">💰 ${internship.stipend}</div>
                <div class="detail-item">🏢 ${internship.sector}</div>
            </div>
            
            <div class="match-reason">
                <div class="reason-title">✨ Why this matches you:</div>
                <div class="reason-text">${internship.match_reason}</div>
            </div>
            
            <p class="description">
                ${internship.description}
            </p>
            
            ${skillsOffered.length > 0 ? `
                <div class="skills-section">
                    <div class="skills-title">🎯 Skills you'll learn:</div>
                    <div class="skills-tags">
                        ${skillsOffered.slice(0, 3).map(skill => 
                            `<span class="skill-tag">${skill}</span>`
                        ).join('')}
                        ${skillsOffered.length > 3 ? `<span class="skill-tag">+${skillsOffered.length - 3} more</span>` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${benefits.length > 0 ? `
                <div class="benefits-section">
                    <div class="benefits-title">🎁 Benefits:</div>
                    <div class="benefits-list">
                        ${benefits.slice(0, 3).map(benefit => 
                            `<span class="benefit-tag">• ${benefit}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
            
            <div class="card-actions">
                <button class="apply-btn" onclick="applyToInternship('${internship.id}')">
                    🚀 Apply Now
                </button>
                <button class="share-btn" onclick="shareInternship('${internship.id}')">
                    📤 Share
                </button>
            </div>
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
    
    // Show skeleton loading in results container as well
    showSkeletonLoading();
}

function showSkeletonLoading() {
    const skeletonHTML = Array(3).fill().map(() => `
        <div class="skeleton-card">
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-company"></div>
            <div class="skeleton-details">
                <div class="skeleton skeleton-detail"></div>
                <div class="skeleton skeleton-detail"></div>
                <div class="skeleton skeleton-detail"></div>
                <div class="skeleton skeleton-detail"></div>
            </div>
            <div class="skeleton skeleton-description"></div>
            <div class="skeleton skeleton-description"></div>
            <div class="skeleton skeleton-description"></div>
        </div>
    `).join('');
    
    recommendationsList.innerHTML = skeletonHTML;
    resultsContainer.style.display = 'block';
    
    // Hide skeleton and show loading spinner after 1 second
    setTimeout(() => {
        resultsContainer.style.display = 'none';
    }, 1000);
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

function showOfflineNotification() {
    // Show a non-intrusive offline notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 16px;
        right: 16px;
        background: #f59e0b;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 14px;
        z-index: 999;
        display: flex;
        align-items: center;
        max-width: 300px;
    `;
    
    notification.innerHTML = `
        <span style="margin-right: 8px;">📶</span>
        <span>You're offline. Showing sample recommendations.</span>
        <button onclick="this.parentElement.remove()" style="
            background: transparent;
            border: none;
            color: white;
            margin-left: 8px;
            cursor: pointer;
            font-size: 16px;
        ">×</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
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
    
    // Add touch-friendly interactions for mobile
    const skillItems = document.querySelectorAll('.skill-item, .interest-item');
    skillItems.forEach(item => {
        // Add touch feedback
        item.addEventListener('touchstart', function(e) {
            this.style.transform = 'scale(0.98)';
        });
        
        item.addEventListener('touchend', function(e) {
            this.style.transform = 'scale(1)';
            // Small delay to show visual feedback
            setTimeout(() => {
                const checkbox = this.querySelector('input[type="checkbox"]');
                if (checkbox && e.target !== checkbox) {
                    checkbox.click();
                }
            }, 100);
        });
        
        item.addEventListener('touchcancel', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Prevent double-tap zoom on buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('touchend', function(e) {
            e.preventDefault();
        });
    });
}

// Register Service Worker for PWA functionality
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js')
            .then((registration) => {
                console.log('SW registered successfully:', registration);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New content available
                            showUpdateAvailableNotification();
                        }
                    });
                });
            })
            .catch((error) => {
                console.log('SW registration failed:', error);
            });
    }
}

function showUpdateAvailableNotification() {
    // Show a subtle notification that an update is available
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        bottom: 16px;
        left: 16px;
        right: 16px;
        background: #4f46e5;
        color: white;
        padding: 16px;
        border-radius: 8px;
        text-align: center;
        z-index: 1000;
        font-size: 14px;
    `;
    notification.innerHTML = `
        New version available! 
        <button onclick="window.location.reload()" style="
            background: white;
            color: #4f46e5;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            margin-left: 8px;
            cursor: pointer;
            font-size: 12px;
        ">Update Now</button>
        <button onclick="this.parentElement.remove()" style="
            background: transparent;
            color: white;
            border: 1px solid white;
            padding: 4px 8px;
            border-radius: 4px;
            margin-left: 4px;
            cursor: pointer;
            font-size: 12px;
        ">Later</button>
    `;
    document.body.appendChild(notification);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 10000);
}

// Local Storage Functions
function saveUserPreferences(userData) {
    try {
        localStorage.setItem('pmInternshipPreferences', JSON.stringify({
            ...userData,
            timestamp: Date.now()
        }));
    } catch (error) {
        console.warn('Could not save preferences to localStorage:', error);
    }
}

function loadSavedPreferences() {
    try {
        const saved = localStorage.getItem('pmInternshipPreferences');
        if (saved) {
            const preferences = JSON.parse(saved);
            
            // Check if preferences are not too old (7 days)
            const isRecent = (Date.now() - preferences.timestamp) < 7 * 24 * 60 * 60 * 1000;
            
            if (isRecent) {
                populateFormWithPreferences(preferences);
                showWelcomeBackMessage(preferences);
            }
        }
    } catch (error) {
        console.warn('Could not load saved preferences:', error);
    }
}

function populateFormWithPreferences(preferences) {
    // Set education
    if (preferences.education) {
        const educationSelect = document.getElementById('education');
        if (educationSelect) educationSelect.value = preferences.education;
    }
    
    // Set location
    if (preferences.location) {
        const locationSelect = document.getElementById('location');
        if (locationSelect) locationSelect.value = preferences.location;
    }
    
    // Set skills
    if (preferences.skills) {
        preferences.skills.forEach(skill => {
            const checkbox = document.querySelector(`input[name="skills"][value="${skill}"]`);
            if (checkbox) checkbox.checked = true;
        });
    }
    
    // Set interests
    if (preferences.interests) {
        preferences.interests.forEach(interest => {
            const checkbox = document.querySelector(`input[name="interests"][value="${interest}"]`);
            if (checkbox) checkbox.checked = true;
        });
    }
}

function showWelcomeBackMessage(preferences) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 16px;
        right: 16px;
        background: #4f46e5;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 14px;
        z-index: 999;
        max-width: 300px;
        display: flex;
        align-items: center;
    `;
    
    notification.innerHTML = `
        <span style="margin-right: 8px;">👋</span>
        <span>Welcome back! We've restored your preferences.</span>
        <button onclick="this.parentElement.remove()" style="
            background: transparent;
            border: none;
            color: white;
            margin-left: 8px;
            cursor: pointer;
            font-size: 16px;
        ">×</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 4000);
}

function clearSavedPreferences() {
    try {
        localStorage.removeItem('pmInternshipPreferences');
        showAlert('Your saved preferences have been cleared.');
    } catch (error) {
        console.warn('Could not clear preferences:', error);
    }
}

// Share functionality
function shareInternship(internshipId) {
    const internships = JSON.parse(localStorage.getItem('lastRecommendations') || '[]');
    const internship = internships.find(i => i.id === internshipId);
    
    if (!internship) {
        showAlert('Internship details not found');
        return;
    }
    
    const shareText = `🎯 Found a great internship opportunity!

${internship.title} at ${internship.company}
📍 ${internship.location}
💰 ${internship.stipend}
⏰ ${internship.duration}

Apply through PM Internship Scheme portal`;
    
    if (navigator.share) {
        // Use native sharing on mobile
        navigator.share({
            title: internship.title,
            text: shareText,
            url: window.location.href
        }).catch(error => {
            console.log('Error sharing:', error);
            fallbackShare(shareText);
        });
    } else {
        fallbackShare(shareText);
    }
}

function fallbackShare(text) {
    // Copy to clipboard
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Internship details copied to clipboard! You can now paste and share.');
        }).catch(() => {
            showShareDialog(text);
        });
    } else {
        showShareDialog(text);
    }
}

function showShareDialog(text) {
    const modal = document.createElement('div');
    modal.style.cssText = `
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
    
    modal.innerHTML = `
        <div style="
            background: white;
            border-radius: 12px;
            padding: 24px;
            max-width: 400px;
            width: 100%;
        ">
            <h3 style="margin-bottom: 16px; color: #1f2937;">Share Internship</h3>
            <textarea readonly style="
                width: 100%;
                height: 150px;
                padding: 12px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-family: inherit;
                font-size: 14px;
                resize: none;
                margin-bottom: 16px;
            ">${text}</textarea>
            <div style="display: flex; gap: 8px;">
                <button onclick="
                    this.closest('div').querySelector('textarea').select();
                    document.execCommand('copy');
                    this.textContent = 'Copied!';
                " style="
                    flex: 1;
                    background: #4f46e5;
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 8px;
                    cursor: pointer;
                ">Copy Text</button>
                <button onclick="this.closest('div').remove()" style="
                    background: #6b7280;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                ">Close</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on outside click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Make functions globally available
window.showForm = showForm;
window.applyToInternship = applyToInternship;
window.shareInternship = shareInternship;
window.clearSavedPreferences = clearSavedPreferences;
