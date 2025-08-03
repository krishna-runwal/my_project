import google.generativeai as genai
import os

def get_final_output(filename):
        # Step 1: Setup
        # Step 1: Setup
        GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

        if not GOOGLE_API_KEY:
              raise ValueError("GOOGLE_API_KEY is not set in environment variables")

        genai.configure(api_key=GOOGLE_API_KEY)

        # Step 2: Load cleaned context
        with open("cleaned_context.txt", "r", encoding="utf-8") as f:
            context_text = f.read()

        # Step 3: Prepare prompt
        prompt = f"""
        You are a lighting schedule analysis expert. You will be given text extracted from a lighting layout PDF drawing (including symbols, fixture names, voltage, lumens, etc.).

        Your job is to analyze the data and return a summary in this exact JSON format:
        In this given text the below information you has been given you have to retrieve it appropiately and return the response in as per the given below example.
        Retrieve full data and analyze it properly
        Example given 
        {{
        "pdf_name": f"{filename}",
        "status": "complete",
        "result": {{
            "A1": {{ "count": 12, "description": "2x4 LED Emergency Fixture" }},
            "A1E": {{ "count": 5, "description": "Exit/Emergency Combo Unit" }},
            "W": {{ "count": 9, "description": "Wall-Mounted Emergency LED" }}
        }}
        }}

        Rules:
        - Group fixtures based on **symbols** found near their descriptions.
        - Count how many times each symbol appears.
        - Match each symbol with the most likely **description** from the context.
        - Do NOT include any explanation or comments.
        - The symbol should be a short code (e.g., A1, EM, W, A1E).
        - If symbols are not found, use the nearest text as a key (e.g., EXIT, EMERGENCY).

        ### CONTEXT START ###
        {context_text}
        ### CONTEXT END ###
        """

        # Step 4: Run Gemini
        model = genai.GenerativeModel("gemini-2.5-flash")  # or "gemini-pro" if needed
        response = model.generate_content(prompt)

        # Step 5: Save result
        with open("summary_output.json", "w", encoding="utf-8") as f:
            f.write(response.text)

        print("✅ Summary output saved to summary_output.json")
        return response.text
