import os
import time
import json
import mimetypes
from typing import List, Optional
from google import genai
from google.genai import types
import dotenv

dotenv.load_dotenv()

class VisionAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment or passed to constructor")
        
        self.client = genai.Client(api_key=self.api_key)
        # Using gemini-flash-latest as requested
        self.model_id = "gemini-flash-latest" 

    def analyze_pdf(self, pdf_path: str, story_context: str = "") -> list:
        """
        Analyzes the entire PDF to generate a segmented narrative script.
        Returns a list of segments: [{'pages': [1, 2], 'script': '...', 'style': '...'}]
        """
        print(f"Uploading PDF {pdf_path} to Gemini...")
        file_ref = self._upload_file(pdf_path)
        
        print("Analyzing PDF content (this may take a minute)...")
        
        context_block = ""
        if story_context:
            context_block = f"""
            IMPORTANT CONTEXT FROM WEB (Use this to correctly identify characters and plot points):
            {story_context}
            ---------------------------------------------------
            """

        prompt_intro = f"""
        You are a professional YouTube Manga Recap scriptwriter targeting an ARABIC-speaking audience. 
        Read this entire manga chapter. 
        
        {context_block}
        
        Break the story down into NARRATIVE SEGMENTS (scenes).
        
        For EACH segment, write a script in ARABIC (Modern Standard Arabic or a natural mixed style used by YouTubers):
        1. "start_page": The starting page number of this segment (1-based index).
        2. "end_page": The ending page number of this segment.
        3. "script": A detailed narration script in ARABIC (40-120 words). 
           - Identify ALL main characters by their names (e.g., بوروتو، شيكامارو).
           - Explicitly summarize key dialogues and interactions.
           - Use a gripping, narrative tone in Arabic. Tell the story like you are explaining it to an audience who can't see the text.
        4. "mood": classify the scene into one of: ["Action", "Suspense", "Sad", "Happy", "Neutral"].
        5. "style_instructions": Instructions for the voice actor in English.
        
        RETURN JSON ONLY:
        """
        
        json_template = """
        [
            {
                "start_page": 1,
                "end_page": 2,
                "script": "...",
                "mood": "Action",
                "style_instructions": "..."
            },
            ...
        ]
        """
        
        prompt = prompt_intro + json_template

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_uri(
                                file_uri=file_ref.uri,
                                mime_type=file_ref.mime_type),
                            types.Part.from_text(text=prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=1
                )
            )
            return json.loads(response.text)

        except Exception as e:
            print(f"Error during PDF analysis: {e}")
            raise e

    def _upload_file(self, path: str):
        file_ref = self.client.files.upload(file=path)
        print(f"File uploaded: {file_ref.uri}")
        
        # Wait for processing if it's large (though usually fast for docs)
        while file_ref.state.name == "PROCESSING":
            print("Processing file...")
            time.sleep(1)
            file_ref = self.client.files.get(name=file_ref.name)
            
        if file_ref.state.name == "FAILED":
            raise ValueError("File processing failed.")
            
        return file_ref

if __name__ == "__main__":
    # Test block
    try:
        agent = VisionAgent()
        print("VisionAgent initialized successfully with gemini-1.5-flash")
    except Exception as e:
        print(f"Error: {e}")
