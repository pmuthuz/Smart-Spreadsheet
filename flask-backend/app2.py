import os
import pandas as pd
import numpy as np
from math import isnan
import datetime
# Load the Excel file
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
data_list = []
indexes_list = []
# Assuming 'df' is your DataFrame
for index, row in df.iterrows():
    #print()
    for col_name in df.columns:
        cell_value = row[col_name]
        #print(index,col_name,cell_value, type(cell_value))
        if( isinstance(cell_value, float) or isinstance(cell_value, int) )and not isnan(cell_value) :
            
            number = cell_value

            for col_number in range(col_name, -1,-1):
                x_move = row[col_number]
                #print('x', x_move)
                if isinstance(x_move, str) :
                    col_name_of_value = x_move
                    break

            for row_number in range(index, -1,-1):
                y_move = df.iat[row_number, col_name]
                #print(row_number, col_name)
                #print('searching y',y_move, type(y_move))
                #print()
                if isinstance(y_move, str) or isinstance(y_move, datetime.datetime) :
                    row_name_of_value = y_move
                    break
            
            table_name = df.iat[row_number, col_number]
            if isinstance(row_name_of_value, datetime.datetime) and number < 5 and number > 0:
                pass
            else:
                if isinstance(table_name,str):
                    data_list.append([table_name, col_name_of_value, row_name_of_value, number])
                else:
                    data_list.append([' ', col_name_of_value, row_name_of_value, number])
            #indexes_list.append([col_number, row_number])


# Create Langchain Agent
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo-1106",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True
)

pandas_df_agent = create_pandas_dataframe_agent(
    llm,
    df=data_list,
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

