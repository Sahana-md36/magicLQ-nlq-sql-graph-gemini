import google.generativeai as genai
import os
import pandas as pd
import importlib.util

# Gemini API Safety Settings
safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

def nl_python_gemini(user_prompt, dataframe, seed):
    """
    Calls Gemini to generate a Python script for plotting a graph using the given dataframe.
    Saves the script to a file and executes it safely.
    """

    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is missing.")
        return None
    genai.configure(api_key=api_key)

    print(f'🔹 SEED SENT TO PROMPT: {seed}')
    
    # Ensure DataFrame is properly formatted as a string
    dataframe_str = dataframe.to_string()

    # Prompt for Gemini AI
    prompt = f"""
You are an expert Python coder. Return ONLY Python code (no explanations or markdown).

### INSTRUCTIONS:
1. Write a Python function named `generated_code()`:
   - Uses Matplotlib to plot a time series graph from the given dataframe.
   - X-axis: `TimeStamp`
   - Y-axis: `NumberOfInfoLogs`
   - Saves the graph as "graph_{seed}.png" (do NOT show it).
   - Calls `plt.savefig('graph_{seed}.png', bbox_inches='tight')` to save.
   - Calls `plt.close()` to free memory.

2. Import necessary libraries (`pandas`, `matplotlib.pyplot`).

3. **DATA CLEANING BEFORE PLOTTING:**
   - If `TimeStamp` contains `None` or `NaT`, remove those rows:
     ```python
     df.dropna(subset=['TimeStamp'], inplace=True)
     ```
   - Convert `TimeStamp` to datetime format safely:
     ```python
     df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')
     ```
   - Sort the dataframe by `TimeStamp` to ensure proper time series order:
     ```python
     df = df.sort_values(by='TimeStamp')
     ```
   - Convert `TimeStamp` to string format for safe plotting:
     ```python
     df['TimeStamp'] = df['TimeStamp'].astype(str)
     ```

4. If the prompt contains ["Plot", "Display", "Generate", "Chart", "Graph"], add `plt.show()`.

This is the instruction for which you have to write a code, to draw and save the graph: {user_prompt}.

This is the dataframe to use:
{dataframe_str}
"""



    # Generate code using Gemini
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.0),
        safety_settings=safety_settings
    )

    generated_code = response.text.strip()

    # Debug: Print Gemini response
    print("🔍 Gemini Response:\n", generated_code)

    # If Gemini returns an empty response, stop execution
    if not generated_code:
        print("❌ Error: Gemini did not return valid Python code.")
        return None

    # Clean Gemini's response (remove any unwanted Markdown formatting)
    if generated_code.startswith("```python"):
        generated_code = generated_code.replace("```python", "").strip()
    if generated_code.endswith("```"):
        generated_code = generated_code.replace("```", "").strip()

    # Save the cleaned code to a Python file
    script_path = "gemini_generated_code.py"
    with open(script_path, "w") as file:
        file.write(generated_code)

    # Debug: Print saved file contents
    print(f"✅ Generated code saved to {script_path}")
    with open(script_path, "r") as file:
        print("🔍 Saved File Contents:\n", file.read())

    # Function to safely execute the generated script
    def run_generated_script(script_path):
        spec = importlib.util.spec_from_file_location("generated", script_path)
        generated = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generated)
        
        # Explicitly call the generated function if it exists
        if hasattr(generated, "generated_code"):
            print("✅ Running generated_code() function...")
            generated.generated_code()
        else:
            print("❌ Error: No function `generated_code()` found in the script.")

    # Run the generated script
    run_generated_script(script_path)

    # Verify if the graph image is created
    image_path = f'graph_{seed}.png'
    if os.path.exists(image_path):
        print(f'✅ Graph image created successfully at {image_path}')
    else:
        print(f'❌ Error: Graph image not found at {image_path}')

    return generated_code
