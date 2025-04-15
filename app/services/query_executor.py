import sys
import os
from typing import List, Dict, Any, Tuple, Union

# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.connection import get_db_cursor

def execute_query(sql_query: str) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    Execute the SQL query and return the results.
    Returns a tuple: (success, data/error_message)
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(sql_query)
            
            # Check if the query returns data
            try:
                columns = [desc[0] for desc in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return True, results
            except:
                # For queries that don't return data (INSERT, UPDATE, etc.)
                return True, "Query executed successfully. No results to return."
                
    except Exception as e:
        return False, f"Error executing query: {str(e)}"
