import base64
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize Chat LLM that supports multi-modal (image + text)
# NOTE: Must use ChatGoogleGenerativeAI, NOT GoogleGenerativeAI
#       GoogleGenerativeAI is text-only and cannot process images.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=api_key,
    temperature=0.1
)

def encode(image_bytes):
    return base64.b64encode(image_bytes).decode()

def analyze_ultrasound(image_bytes, plane, part):
    img64 = encode(image_bytes)

    # Force AI to detect coordinates and orientation
    prompt = f"""
    You are a Senior Radiologist. Analyze this ultrasound image.
    Detected Plane: {plane}
    Target Part: {part}

    TASK:
    1. Define Orientation: Choose from [Cephalic, Breech, Transverse, Longitudinal].
    2. Define Coordinates: Return the bounding box [x_min, y_min, x_max, y_max] for the {part}.
    
    STRICT RULES:
    - Use normalized scale 0-1000 for coordinates.
    - DO NOT return [0,0,0,0]. Estimate the location.
    - Return ONLY valid JSON. No extra text before or after the JSON.

    JSON Format:
    {{
        "analysis_results": {{
            "orientation": "VALUE",
            "coordinates": [x1, y1, x2, y2]
        }}
    }}
    """
    
    # Build multimodal message with correct image_url format
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img64}"}
            }
        ]
    )

    try:
        # ChatGoogleGenerativeAI returns an AIMessage with .content
        res = llm.invoke([message])
        content = res.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        
        # Extracting nested result
        if "analysis_results" in data:
            return data["analysis_results"]
        return data
    except Exception as e:
        print(f"Gemini Error: {e}")
        return {"error": str(e)}