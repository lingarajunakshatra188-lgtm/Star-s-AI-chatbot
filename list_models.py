import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Read the API key
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)

print("Available Models:\n")

# Print all models that support generateContent
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)