import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
from IPython.display import Markdown, HTML, display
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_experimental.tools import PythonREPLTool
from langchain.sql_database import SQLDatabase
from langchain_openai import AzureChatOpenAI
from langchain_groq import ChatGroq

from sqlalchemy import create_engine
import pandas as pd

# Define the model for the request body
class PromptRequest(BaseModel):
    prompt: str
    model_name: str

# Initialize FastAPI app
app = FastAPI()

MSSQL_AGENT_PREFIX = """

You are an agent designed to interact with a SQL database.
## Instructions:
- Given an input question, create a syntactically correct {dialect} query
to run, then look at the results of the query and return the answer.
- Unless the user specifies a specific number of examples they wish to
obtain, **ALWAYS** limit your query to at most {top_k} results.
- You can order the results by a relevant column to return the most
interesting examples in the database.
- Never query for all the columns from a specific table, only ask for
the relevant columns given the question.
- You have access to tools for interacting with the database.
- You MUST double check your query before executing it.If you get an error
while executing a query,rewrite the query and try again.
- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)
to the database.
- DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE, ONLY USE THE RESULTS
OF THE CALCULATIONS YOU HAVE DONE.
- Your response should be in Markdown. However, **when running  a SQL Query
in "Action Input", do not include the markdown backticks**.
Those are only for formatting the response, not for executing the command.
- ALWAYS, as part of your final answer, explain how you got to the answer
on a section that starts with: "Explanation:". Include the SQL query as
part of the explanation section.
- If the question does not seem related to the database, just return
"I don\'t know" as the answer.
- Only use the below tools. Only use the information returned by the
below tools to construct your query and final answer.
- Do not make up table names, only use the tables returned by any of the
tools below.

## Tools:

"""

MSSQL_AGENT_FORMAT_INSTRUCTIONS = """

## Use the following format:

Question: the input question you must answer.
Thought: you should always think about what to do.
Action: the action to take, should be one of [{tool_names}].
Action Input: the input to the action.
Observation: the result of the action.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer.
Final Answer: the final answer to the original input question.

Example of Final Answer:
<=== Beginning of example

Action: query_sql_db
Action Input: 
SELECT TOP (10) [death]
FROM covidtracking 
WHERE state = 'TX' AND date LIKE '2020%'

Observation:
[(27437.0,), (27088.0,), (26762.0,), (26521.0,), (26472.0,), (26421.0,), (26408.0,)]
Thought:I now know the final answer
Final Answer: There were 27437 people who died of covid in Texas in 2020.

Explanation:
I queried the `covidtracking` table for the `death` column where the state
is 'TX' and the date starts with '2020'. The query returned a list of tuples
with the number of deaths for each day in 2020. To answer the question,
I took the sum of all the deaths in the list, which is 27437.
I used the following query

```sql
SELECT [death] FROM covidtracking WHERE state = 'TX' AND date LIKE '2020%'"
```
===> End of Example

"""

@app.post("/query")
async def query_db(request: PromptRequest):
    prompt = request.prompt
    model_name = request.model_name
    
    llm = ChatGroq(
        temperature=0,
        groq_api_key="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",
        model_name=model_name
    )

    # Use the hard-coded path for the CSV file
    csv_file_path = "PO.csv"
    df = pd.read_csv(csv_file_path).fillna(value=0)

    # Path to your SQLite database file
    database_file_path = "test.db"

    # Create an engine to connect to the SQLite database
    engine = create_engine(f'sqlite:///{database_file_path}')
    df.to_sql(
        'PO',
        con=engine,
        if_exists='replace',
        index=False
    )

    db = SQLDatabase.from_uri(f'sqlite:///{database_file_path}')
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    python_repl_tool = PythonREPLTool()


    agent_executor_SQL = create_sql_agent(
        prefix=MSSQL_AGENT_PREFIX,
        format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS,
        llm=llm,
        toolkit=toolkit, 
        top_k=30,
        verbose=True
    )

    try:
        response = agent_executor_SQL.invoke(prompt)
        response_text = response['output']
        return {"response": response_text}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)