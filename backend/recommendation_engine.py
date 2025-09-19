import json
import os
from typing import List, Dict, Any
from datetime import datetime

class RecommendationEngine:
    def __init__(self):
        self.internships = self.load_internships()
        
    def load_internships(self) -> List[Dict]:
        """Load internship data from JSON file"""
        try:
            # Get the path to the data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(os.path.dirname(current_dir), 'data', 'sample_internships.json')
            
            with open(data_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            # Return empty list if file not found
            return []
        except json.JSONDecodeError:
            # Return empty list if JSON is invalid
            return []
    
    def recommend_internships(self, candidate_profile: Dict[str, Any]) -> List[Dict]:
        """
        Generate personalized internship recommendations based on candidate profile
        
        Args:
            candidate_profile: Dictionary containing candidate's education, skills, interests, and location
            
        Returns:
            List of recommended internships with match scores and reasons
        """
        if not self.internships:
            return []
        
        # Calculate match scores for all internships
        scored_internships = []
        for internship in self.internships:
            score, reason = self.calculate_match_score(candidate_profile, internship)
            if score > 0:  # Only include internships with some match
                internship_with_score = internship.copy()
                internship_with_score['match_score'] = score
                internship_with_score['match_reason'] = reason
                scored_internships.append(internship_with_score)
        
        # Sort by match score (highest first) and return top 5
        scored_internships.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_internships[:5]
    
    def calculate_match_score(self, candidate: Dict[str, Any], internship: Dict[str, Any]) -> tuple:
        """
        Calculate match score between candidate and internship
        
        Returns:
            tuple: (score, reason) where score is 0-100 and reason explains the match
        """
        score = 0
        match_reasons = []
        
        # 1. Skills matching (40% weight)
        skills_score = self.calculate_skills_match(candidate.get('skills', []), internship.get('requirements', []))
        score += skills_score * 0.4
        if skills_score > 70:
            match_reasons.append(f"Strong skills match ({skills_score}%)")
        elif skills_score > 40:
            match_reasons.append(f"Good skills alignment ({skills_score}%)")
        
        # 2. Interest/Sector matching (30% weight)
        sector_score = self.calculate_sector_match(candidate.get('interests', []), internship.get('sector', ''))
        score += sector_score * 0.3
        if sector_score > 0:
            match_reasons.append(f"Matches your interest in {internship.get('sector', '')}")
        
        # 3. Location matching (20% weight)
        location_score = self.calculate_location_match(candidate.get('location', ''), internship)
        score += location_score * 0.2
        if location_score > 80:
            match_reasons.append("Perfect location match")
        elif location_score > 40:
            match_reasons.append("Good location fit")
        
        # 4. Education matching (10% weight)
        education_score = self.calculate_education_match(candidate.get('education', ''), internship.get('preferred_education', []))
        score += education_score * 0.1
        if education_score > 80:
            match_reasons.append("Education level perfectly matches requirements")
        
        # Generate human-readable reason
        if not match_reasons:
            reason = "Basic compatibility with your profile"
        else:
            reason = ". ".join(match_reasons[:2])  # Use top 2 reasons
        
        return min(100, max(0, int(score))), reason
    
    def calculate_skills_match(self, candidate_skills: List[str], required_skills: List[str]) -> float:
        """Calculate percentage match between candidate skills and job requirements"""
        if not required_skills:
            return 50  # Neutral score if no requirements specified
        
        if not candidate_skills:
            return 0
        
        # Normalize skills for comparison
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        matches = 0
        for req_skill in required_skills_lower:
            for candidate_skill in candidate_skills_lower:
                if candidate_skill in req_skill or req_skill in candidate_skill:
                    matches += 1
                    break
        
        return (matches / len(required_skills)) * 100
    
    def calculate_sector_match(self, candidate_interests: List[str], internship_sector: str) -> float:
        """Calculate match between candidate interests and internship sector"""
        if not candidate_interests or not internship_sector:
            return 0
        
        internship_sector_lower = internship_sector.lower()
        
        for interest in candidate_interests:
            interest_lower = interest.lower()
            if interest_lower == internship_sector_lower:
                return 100  # Perfect match
            elif interest_lower in internship_sector_lower or internship_sector_lower in interest_lower:
                return 75   # Good match
        
        return 0  # No match
    
    def calculate_location_match(self, candidate_location: str, internship: Dict[str, Any]) -> float:
        """Calculate location compatibility"""
        if not candidate_location:
            return 50  # Neutral if no preference
        
        candidate_location_lower = candidate_location.lower()
        internship_location_lower = internship.get('location', '').lower()
        
        # Perfect matches
        if candidate_location_lower == 'any':
            return 100
        
        if internship.get('is_remote', False) and candidate_location_lower in ['remote', 'any']:
            return 100
        
        if candidate_location_lower in internship_location_lower or internship_location_lower in candidate_location_lower:
            return 100
        
        # Remote work is always an option for flexibility
        if internship.get('is_remote', False):
            return 80
        
        # Check if location is in same region/state (simplified)
        if self.is_same_region(candidate_location_lower, internship_location_lower):
            return 60
        
        return 20  # Low score for distant locations
    
    def is_same_region(self, loc1: str, loc2: str) -> bool:
        """Check if two locations are in the same region (simplified logic)"""
        # This is a simplified implementation
        # In a real system, you'd use proper geographical data
        metro_cities = {
            'mumbai': 'west',
            'pune': 'west',
            'bangalore': 'south',
            'chennai': 'south',
            'hyderabad': 'south',
            'delhi': 'north',
            'kolkata': 'east'
        }
        
        region1 = metro_cities.get(loc1)
        region2 = metro_cities.get(loc2)
        
        return region1 == region2 and region1 is not None
    
    def calculate_education_match(self, candidate_education: str, preferred_education: List[str]) -> float:
        """Calculate education level compatibility"""
        if not preferred_education:
            return 100  # If no preference, all are welcome
        
        if not candidate_education:
            return 0
        
        candidate_education_lower = candidate_education.lower()
        
        for pref_edu in preferred_education:
            if candidate_education_lower == pref_edu.lower():
                return 100  # Exact match
        
        # Check if candidate's education level is higher than minimum required
        education_levels = ['10th', '12th', 'diploma', 'undergraduate', 'postgraduate']
        
        try:
            candidate_level = education_levels.index(candidate_education.lower())
            min_required_level = min([education_levels.index(pref.lower()) for pref in preferred_education if pref.lower() in education_levels])
            
            if candidate_level >= min_required_level:
                return 80  # Qualified (higher education is acceptable)
            else:
                return 30  # Under-qualified but might still be considered
        except (ValueError, IndexError):
            return 50  # Unknown education levels
    
    def get_all_internships(self) -> List[Dict]:
        """Return all available internships"""
        return self.internships
    
    def get_available_sectors(self) -> List[str]:
        """Return list of all available sectors"""
        sectors = set()
        for internship in self.internships:
            if internship.get('sector'):
                sectors.add(internship['sector'])
        return sorted(list(sectors))
    
    def get_internship_by_id(self, internship_id: str) -> Dict:
        """Get specific internship by ID"""
        for internship in self.internships:
            if internship.get('id') == internship_id:
                return internship
        return {}
    
    def search_internships(self, sector: str = None, location: str = None, is_remote: bool = None) -> List[Dict]:
        """Search internships based on filters"""
        results = self.internships.copy()
        
        if sector:
            results = [i for i in results if i.get('sector', '').lower() == sector.lower()]
        
        if location:
            results = [i for i in results if 
                      location.lower() in i.get('location', '').lower() or 
                      (location.lower() == 'remote' and i.get('is_remote', False))]
        
        if is_remote is not None:
            results = [i for i in results if i.get('is_remote', False) == is_remote]
        
        return results
