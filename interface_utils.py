import re

def get_sql_code_from_response(response: str):
    '''
    This function extracts the SQL code from the response of the LLM model.
    Params:
    -response: the response from the LLM model as a string.
    Returns:
    -sql_code: the SQL code cleaned and ready to execute.
    '''
    match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
    
    if match:
        sql_code = match.group(1)
        return sql_code.strip()  # Eliminate leading and trailing whitespaces
    else:
        print("SQL code not found in response.")
        return None
 

def get_plotly_code_from_response(response: str):
    '''
    This function extracts the Plotly code from the response of the LLM model.
    Params:
    -response: the response from the LLM model as a string.
    Returns:
    -plotly_code: the Plotly code cleaned and ready to execute.
    '''
    match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
    
    if match:
        plotly_code = match.group(1)
        return plotly_code.strip()  # Eliminate leading and trailing whitespaces
    else:
        print("Plotly code not found in response.")
        return None