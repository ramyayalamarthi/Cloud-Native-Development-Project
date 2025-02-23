import os
import google.generativeai as genai
import json
from storage import upload_file

genai.configure(api_key=os.environ['GEMINI_API'])

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

PROMPT = """describe the image, description  less than 20 words and 
only as below json formate, no heading, no extra text,just json which easy formate by using json.loads
{
   "title" : "PLACE THE GENERATED TITLE HERE",
   "description" : "PLACE THE GENERATED DESCRIPTION HERE"
}
"""

def upload_to_gemini(bucket_name,image_path):
  uploaded_file = genai.upload_file(image_path, mime_type="image/jpeg")
  response = model.generate_content([uploaded_file, "\n\n", PROMPT])
  json_str = response.text.strip("```json\n").strip("\n```")
  json_data = ""
  try:
    json_data = json.loads(json_str)
  except json.JSONDecodeError as e:
    json_data = json_str

  base_name = os.path.splitext(os.path.basename(image_path))[0]
  output_file_path = f"files/{base_name}.json"
  with open(output_file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
  upload_file(bucket_name, image_path)      
  upload_file(bucket_name,output_file_path)
