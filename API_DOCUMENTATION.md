# PM Internship Recommender API Documentation

## Base URL
- **Production**: `https://pm-internship-engine.onrender.com`
- **Local Development**: `http://localhost:5000`

## API Endpoints

### 1. Health Check
**GET /** 

Returns basic API information and health status.

**Response:**
```json
{
  "message": "PM Internship Recommender API",
  "version": "1.0.0",
  "status": "active"
}
```

### 2. Get Personalized Recommendations
**POST /api/recommend**

Get personalized internship recommendations based on candidate profile.

**Request Body:**
```json
{
  "education": "undergraduate",
  "skills": ["computer", "communication"],
  "interests": ["technology"],
  "location": "bangalore"
}
```

**Required Fields:**
- `education`: Education level (10th, 12th, diploma, undergraduate, postgraduate)
- `skills`: Array of skills (computer, communication, accounting, teaching, healthcare, agriculture, design, sales)
- `interests`: Array of interests (technology, healthcare, education, finance, manufacturing, agriculture, retail)
- `location`: Preferred location (mumbai, delhi, bangalore, chennai, kolkata, pune, hyderabad, remote, any)

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "id": "INT001",
      "title": "Frontend Developer Intern",
      "company": "TechCorp India",
      "sector": "technology",
      "location": "Bangalore",
      "duration": "6 months",
      "stipend": "₹15,000/month",
      "description": "Work on modern web applications...",
      "match_score": 100,
      "match_reason": "Strong skills match (100.0%). Matches your interest in technology",
      "requirements": ["computer", "communication"],
      "skills_offered": ["React", "JavaScript", "HTML/CSS", "UI/UX Design"],
      "is_remote": true,
      "certification": true,
      "full_time_potential": true
    }
  ],
  "total": 5
}
```

### 3. Get All Internships
**GET /api/internships**

Retrieve all available internships.

**Response:**
```json
{
  "success": true,
  "internships": [...],
  "total": 8
}
```

### 4. Get Available Sectors
**GET /api/sectors**

Get list of all available sectors.

**Response:**
```json
{
  "success": true,
  "sectors": [
    "agriculture",
    "education",
    "finance",
    "healthcare",
    "retail",
    "technology"
  ]
}
```

### 5. Search Internships
**GET /api/internships/search**

Search internships with filters.

**Query Parameters:**
- `sector` (optional): Filter by sector
- `location` (optional): Filter by location
- `remote` (optional): Filter by remote work (true/false)

**Examples:**
- `/api/internships/search?sector=technology`
- `/api/internships/search?location=bangalore`
- `/api/internships/search?remote=true`
- `/api/internships/search?sector=healthcare&location=chennai`

**Response:**
```json
{
  "success": true,
  "internships": [...],
  "total": 3,
  "filters": {
    "sector": "technology",
    "location": null,
    "remote": false
  }
}
```

### 6. Get Internship Details
**GET /api/internships/{internship_id}**

Get detailed information about a specific internship.

**Path Parameters:**
- `internship_id`: Unique internship identifier

**Example:** `/api/internships/INT001`

**Response:**
```json
{
  "success": true,
  "internship": {
    "id": "INT001",
    "title": "Frontend Developer Intern",
    "company": "TechCorp India",
    // ... full internship details
  }
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing required fields)
- `404`: Not Found (for specific internship requests)
- `500`: Internal Server Error

**Error Response Format:**
```json
{
  "error": "Missing required field: education"
}
```

## Data Models

### Candidate Profile
```json
{
  "education": "string (required)",
  "skills": ["string"] (required, min: 1),
  "interests": ["string"] (required, min: 1),
  "location": "string (required)"
}
```

### Internship Object
```json
{
  "id": "string",
  "title": "string",
  "company": "string",
  "sector": "string",
  "location": "string",
  "is_remote": "boolean",
  "duration": "string",
  "stipend": "string",
  "description": "string",
  "requirements": ["string"],
  "preferred_education": ["string"],
  "skills_offered": ["string"],
  "benefits": ["string"],
  "certification": "boolean",
  "full_time_potential": "boolean",
  "application_deadline": "string",
  "start_date": "string",
  "contact_email": "string",
  "company_size": "string",
  "language_requirements": ["string"],
  "accessibility": {
    "rural_friendly": "boolean",
    "low_bandwidth_work": "boolean",
    "flexible_hours": "boolean"
  }
}
```

## Rate Limiting
Currently no rate limiting is implemented, but it's recommended for production use.

## Authentication
Currently no authentication is required. This is suitable for public access but should be secured for production deployments with sensitive data.

## CORS
CORS is enabled for all origins to support frontend integration.