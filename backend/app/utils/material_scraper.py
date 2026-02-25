import os
from typing import List, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class MaterialScraper:
    """
    Service to fetch verified academic materials using the Google Gen AI SDK.
    Uses Gemini 2.5 Flash with Google Search grounding to return real URLs.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables.", flush=True)
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    def _interpret_query(self, raw_query: str) -> str:
        """
        Rewrites a natural language student query into a search-optimized
        academic topic before passing it to the resource fetcher.
        """
        prompt = f"""A software engineering student typed this search query: "{raw_query}"

Rewrite it as a clear, specific academic topic suitable for finding tutorials and articles.
- Map it to its formal computer science or mathematics concept if applicable
- Make it specific enough to find a dedicated article (not a homepage)
- Keep it concise (3-7 words max)
- Return ONLY the rewritten topic, nothing else.

Examples:
"sequence of equations" → "systems of linear equations discrete math"
"how do loops work" → "iteration and loops programming"
"why is my sort slow" → "sorting algorithm time complexity"
"how computers remember things" → "memory management computer science"
"""
        response = self.client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0),
        )
        interpreted = response.text.strip()
        print(f"  Query interpreted: '{raw_query}' → '{interpreted}'", flush=True)
        return interpreted

    def fetch_academic_materials(self, course_name: str) -> List[Dict]:
        """
        Generates a list of academic resources using Gemini's grounding metadata
        to extract real URLs rather than relying on generated text URLs.
        URL verification removed — grounding_chunks URLs are already real search results.
        """
        if not self.client:
            print("Scraper aborted: No API key.", flush=True)
            return []

        try:
            course_name = self._interpret_query(course_name)
            print(f"Asking Gemini to find resources for: {course_name}...", flush=True)

            prompt = f"""Find the best free learning resources for a software engineering student studying: "{course_name}".

For each resource you find, provide:
- The title of the page
- The full URL
- One sentence describing what it covers

Prioritize resources that show full content immediately without login — tutorials, articles, documentation, and reference pages.
Do not include resources that require registration or payment."""

            response = self.client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0,
                ),
            )

            # Extract URLs from grounding metadata — these are guaranteed real
            materials = []
            grounding = getattr(response.candidates[0], 'grounding_metadata', None)
            chunks = getattr(grounding, 'grounding_chunks', None) if grounding else None

            if chunks:
                for chunk in chunks:
                    web = getattr(chunk, 'web', None)
                    if not web:
                        continue
                    url = getattr(web, 'uri', None)
                    title = getattr(web, 'title', None)
                    if not url or not title:
                        continue
                    if not url.startswith('http'):
                        continue
                    materials.append({
                        "title": title,
                        "url": url,
                        "type": "textbook",
                        "learning_style_tag": "Read/Write"
                    })
                    print(f"  ✓ Added: {url}", flush=True)

                    if len(materials) >= 5:
                        break

            print(f"Successfully found {len(materials)} materials!", flush=True)
            return materials

        except Exception as e:
            print(f"\n!!! Error fetching materials from Gemini: {e} !!!\n", flush=True)
            return []