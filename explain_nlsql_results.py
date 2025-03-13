import google.generativeai as genai
import json
import pandas as pd
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def explain_result(sql_prompt, sql_result, sql_query):
    """Generates a human-readable summary of SQL results and includes the SQL query in the response."""

    user_prompt = f"""Summarize the results from the SQL query in less than or up to four sentences. 
    The result is from the following query: {sql_prompt}.
    Result: {sql_result}. 
    In the response, do not mention database-related words like SQL, rows, timestamps, etc."""

    models = genai.GenerativeModel('gemini-2.0-flash')
    response = models.generate_content(user_prompt)
    explanation = response.text.strip()
    
    result_list = None
    if not sql_result.empty:
        result_list = sql_result.to_json(orient='records')  # ✅ Convert DataFrame to JSON

    return {
        "summary": explanation,
        "results": result_list,
        "sql_query": sql_query  # ✅ Include the executed SQL query
    }
