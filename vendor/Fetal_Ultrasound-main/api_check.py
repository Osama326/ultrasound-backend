from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os 


# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.1
)
res = llm.invoke("what is Ai in 1 line")
print(res)