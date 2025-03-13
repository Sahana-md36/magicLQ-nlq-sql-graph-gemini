import pandas as pd
import gencode
from datetime import datetime
import nl_sql_result
import run_sql
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')
from execute_gen_code import execute_code
import os
from dotenv import load_dotenv, find_dotenv
import explain_nlsql_results  
load_dotenv(find_dotenv())

api_key = os.getenv('GEMINI_API_KEY')
app = Flask(__name__)
CORS(app)

MAX_GEN_RETRY = 3

@app.route('/gencode/', methods=['GET', 'POST'])
def prompt_process():
    """Handles user prompts, generates SQL, executes it, and optionally creates a graph."""

    sql_prompt = request.args.get('prompt')
    if not sql_prompt:
        return jsonify({"error": "No prompt given. Please provide a prompt."}), 400

    seed = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    print(f'Seed generated: {seed}')

    # Detect if a graph is needed
    graph_keywords = ["plot", "generate", "display", "chart", "graph"]
    graph_needed = any(word in sql_prompt.lower() for word in graph_keywords)

    success_run = False
    sql_result = None
    sql_query = None
    generated_code = None
    summary = None
    user_prompt = sql_prompt

    for _ in range(MAX_GEN_RETRY):
        try:
            sql_result, sql_query = nl_sql_result.nl_sql_nl_gemini(sql_prompt)

            if graph_needed:
                generated_code = gencode.nl_python_gemini(sql_prompt, sql_result, seed)
                execute_code(generated_code)  # Run the generated code to create the graph

            summary_data = explain_nlsql_results.explain_result(sql_prompt, sql_result, sql_query)
            summary = summary_data["summary"]

            success_run = True
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

    if success_run:
        if graph_needed:
            image_path = f'graph_{seed}.png'
            try:
                print(f'Sending back graph image: {image_path}')
                return send_file(image_path, mimetype='image/png')
            except Exception as e:
                return jsonify({"error": f"Graph image not found: {e}"}), 404

        return jsonify({
            "user_prompt": user_prompt,
            "summary": summary,
            "sql_query": sql_query.replace("\n", " "),
            "sql_result": sql_result.to_dict(orient="records") if not sql_result.empty else [],
            "message": "Query executed successfully. No graph requested."
        })

    return jsonify({"error": "Could not process the request."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
