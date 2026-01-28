from app.models.course import Course
import requests

class ResourceService:
    @staticmethod
    def search_resources(course_id, topic=None):
        course = Course.query.get(course_id)
        if not course:
            return []
            
        query = f"{course.name}"
        if topic:
            query += f" {topic}"
        else:
            query += " tutorial"
            
        # Mocking YouTube API response because we don't have a real API Key
        # In production this would call:
        # url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key=YOUR_API_KEY"
        
        print(f"Searching YouTube for: {query}")
        
        # Mock Data
        mock_results = [
            {"title": f"{course.name} Full Course", "url": "https://youtube.com/watch?v=mock1", "channel": "NileUni Tech"},
            {"title": f"Understanding {topic if topic else 'Key Concepts'} in {course.code}", "url": "https://youtube.com/watch?v=mock2", "channel": "EduHub"},
            {"title": f"{course.name} Exam Prep", "url": "https://youtube.com/watch?v=mock3", "channel": "StudySmart"}
        ]
        
        return mock_results
