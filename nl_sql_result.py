
import run_sql
import google.generativeai as genai
import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


api_key = os.getenv('GEMINI_API_KEY')
safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


MAX_GEN_RETRY=3

def parse_triple_quotes(in_str):
# Parse out the string after ```sql and before ```
  # Using Python's string manipulation methods to extract the SQL query
  start = in_str.find("```sql") + len("```sql\n")  # Start after ```sql and the newline
  end = in_str.rfind("```")  # Find the last occurrence of ```
  out_str = in_str[start:end].strip()  # Extract the SQL query and strip leading/trailing whitespace
  #print(f'OUTPUT STRING {out_str}')
  return out_str

def nl_sql_nl_gemini(sql_prompt):
    """Generates an SQL query and fetches results from the database."""

    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)  

    prompt = f"""
        You are a Microsoft SQL Server expert. Given an input question, create a complete, syntactically correct SQL query.
        - Ensure case-insensitive filtering for string columns.
        - Trim spaces to avoid mismatches.
        - Before applying filters, check if data exists.
        - Use `TOP 5` unless the user specifies a different number.
        - Use `DISTINCT` when listing unique values.
        - Wrap column names in square brackets `[]`.

        The database schema is:
        ```sql
        CREATE TABLE [dbo].[cloudwatch_logs_updated](
            [TimeStamp] [datetime] NULL,
            [SourceApplication] [nvarchar](max) NULL,
            [SourceModule] [nvarchar](max) NULL,
            [Type] [nvarchar](max) NULL,
            [Tags] [nvarchar](max) NULL,
            [Description] [nvarchar](max) NULL,
            [GUID] [nvarchar](max) NULL
        );
        ```

        Generate a SQL query for: {sql_prompt}
    """

    models = genai.GenerativeModel('gemini-2.0-flash')
    response = models.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0))
    sql_string = response.text.strip()

    if "```sql" in sql_string.lower():
        sql_string = parse_triple_quotes(sql_string)

    sql_result = pd.DataFrame()

    # Try running the SQL up to 3 times
    for _ in range(MAX_GEN_RETRY):
        try:
            sql_result = run_sql.execute_query_df(sql_string)
            break  # Exit loop if successful
        except Exception as e:
            print(f" SQL Execution Error: {e}")
            continue  

    return sql_result, sql_string
