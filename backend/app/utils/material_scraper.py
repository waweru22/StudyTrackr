import os
import json
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv  # <--- FIX 1: Import dotenv

load_dotenv()  # <--- FIX 2: Force Python to read your .env file

class MaterialScraper:
    """
    Service to fetch verified academic materials using Gemini API with Google Search Grounding.
    Ensures no hallucinations by strictly using the 'google_search_retrieval' tool.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            # FIX 3: Added flush=True so you actually see this warning if it happens
            print("Warning: GOOGLE_API_KEY not found in environment variables.", flush=True)
        else:
            genai.configure(api_key=self.api_key)

    def fetch_academic_materials(self, course_name: str) -> List[Dict]:
        """
        Generates a list of academic resources for a given course using Gemini with Search Grounding.
        Returns a strict JSON list of materials.
        """
        if not self.api_key:
            print("Scraper aborted: No API key.", flush=True)
            return []

        try:
            print(f"Asking Gemini to search Google for: {course_name}...", flush=True)
            
            # Initialize model with Search Grounding tool
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash-lite', 
                tools=[{'google_search_retrieval': {}}]
            )

            prompt = f"""
            Act as an expert curation assistant for software engineering students.
            Search the live internet to find EXACTLY 7 high-quality, ACTUAL, EXISTING URLs for the course: "{course_name}".
            
            Strict Sourcing Rules:
            - For TEXT/ARTICLES: Prioritize trusted domains like GeeksforGeeks, TutorialsPoint, W3Schools, Medium, and Dev.to.
            - For VIDEOS: Prioritize trusted YouTube channels like freeCodeCamp, MIT OpenCourseWare, Traversy Media, Programming with Mosh, and Computerphile.
            
            ABSOLUTELY NO HALLUCINATIONS. You MUST use the Google Search tool to find real, clickable links that currently exist.
            
            Return ONLY a JSON array of objects. Do not include markdown formatting (like ```json ... ```).
            Each object must have these exact keys:
            - "title": (String) The actual title of the resource.
            - "url": (String) The verified, real URL found via search.
            - "type": (String) Strictly "video" (for YouTube) or "textbook" (for articles/tutorials).
            - "learning_style_tag": (String) Strictly "Visual" (for video) or "Read/Write" (for textbook).
            """

            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            # Parse JSON response
            text_response = response.text.strip()
            
            materials = json.loads(text_response)
            
            # Failsafe: Sometimes Gemini wraps the array in a dictionary (e.g. {"materials": [...]})
            if isinstance(materials, dict):
                # Grab the first list it finds inside the dictionary
                materials = next(iter(materials.values()))

            # Additional validation loop
            valid_materials = []
            for m in materials:
                if all(k in m for k in ["title", "url", "type", "learning_style_tag"]):
                    valid_materials.append(m)
            
            print(f"Successfully found {len(valid_materials)} materials!", flush=True)
            return valid_materials

        except Exception as e:
            # FIX 3: Added flush=True so we can see API crashes
            print(f"\n!!! Error fetching materials from Gemini: {e} !!!\n", flush=True)
            return []