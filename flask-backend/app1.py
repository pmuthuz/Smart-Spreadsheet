import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load the Excel file
dataset_path = "example_0.xlsx"

# Read the Excel file to identify the tables
df = pd.read_excel(dataset_path, sheet_name='Analysis Output', header=None)

# Define the start and end rows for each table
table_ranges = [
    (0, 17),
    (18, 37),
    (38, 49),
    (50, 60),
    (61, 65),
    (66, 71),
    (72, 82),
    (83, 94)
]
tables = []
for start, end in table_ranges:
    table = df.iloc[start:end+1].reset_index(drop=True)
    table.columns = table.iloc[0]
    print(table.columns)
    table = table.drop(0).reset_index(drop=True)  # Drop the header row
    table = table.dropna(axis=1, how='all')  # Remove columns that are entirely NaN
    tables.append(table)

# Extract the tables based on the defined ranges
tables = [df.iloc[start:end+1].reset_index(drop=True) for start, end in table_ranges]

# Combine all tables into one DataFrame with multi-index
combined_df = pd.concat(tables, keys=[f'Table {i+1}' for i in range(len(tables))])

# Create Langchain Agent
llm = ChatOpenAI(
    temperature=0, 
    model="gpt-3.5-turbo-1106", 
    openai_api_key=os.getenv("OPENAI_API_KEY"), 
    streaming=True
)

pandas_df_agent = create_pandas_dataframe_agent(
    llm,
    df=combined_df,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Process the question using the Langchain agent
    response = pandas_df_agent.run(question)
    return jsonify({"answer": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

