import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.services.schema_service import get_database_schema
from app.services.sql_generation import generate_sql_query
from app.services.query_executor import execute_query
from app.schemas.sql_schema import SQLQueryRequest

def process_text_to_sql(query_text: str):
    """
    Main function to process a text query to SQL and execute it.
    """
    # Step 1: Get database schema
    print("Fetching database schema...")
    schema = get_database_schema()
    
    # Step 2: Generate SQL query using LLM
    print(f"Generating SQL for query: {query_text}")
    request = SQLQueryRequest(
        natural_language_query=query_text,
        schema=schema
    )
    
    response = generate_sql_query(request)
    
    if response.error:
        print(f"Error: {response.error}")
        return None
    
    print(f"Generated SQL query: {response.sql_query}")
    
    # Step 3: Execute the query
    success, result = execute_query(response.sql_query)
    
    if not success:
        print(f"Query execution failed: {result}")
        return None
    
    return {
        "query": query_text,
        "sql": response.sql_query,
        "results": result
    }

if __name__ == "__main__":
    # Example usage
    query = input("Enter your query in natural language: ")
    result = process_text_to_sql(query)
    
    if result:
        print("\nResults:")
        print(result["results"])
