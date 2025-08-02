import google.generativeai as genai

# 🔑 STEP 1: Add your API key here
GOOGLE_API_KEY = "AIzaSyAkFgvDKHHP2bkd639tWQzTgmkK-Lm1qPc"
genai.configure(api_key=GOOGLE_API_KEY)

# 🔄 STEP 2: Load your cleaned context
with open("cleaned_context.txt", "r", encoding="utf-8") as file:
    context_text = file.read()

# 🧠 STEP 3: Construct the prompt
prompt = f"""
You are a document processing expert who extracts structured data from lighting plan drawings and general notes.

The text below was extracted from a construction lighting drawing. Your task is to:

1. Identify all **General Notes** present in the text.
2. Extract the **Lighting Schedule Table**, which typically includes:
   - Symbol
   - Description
   - Mount
   - Voltage
   - Lumens
   - Any other available attributes

Return the output strictly in the following JSON structure:

{{
  "rulebook": [
    {{
      "type": "note",
      "text": "Text of the note",
      "source_sheet": "Sheet name or page number if available"
    }},
    {{
      "type": "table_row",
      "symbol": "A1E",
      "description": "Exit/Emergency Combo Unit",
      "mount": "Ceiling",
      "voltage": "277V",
      "lumens": "1500lm",
      "source_sheet": "Lighting Schedule - E3"
    }}
  ]
}}

### CONTEXT START ###
{context_text}
### CONTEXT END ###

Do not include any explanation. Just return the JSON.
"""

# 💬 STEP 4: Load Gemini model and generate
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content(prompt)

# 📁 STEP 5: Save output
with open("rulebook_output.json", "w", encoding="utf-8") as f:
    f.write(response.text)

print("✅ Rulebook JSON saved to rulebook_output.json")
