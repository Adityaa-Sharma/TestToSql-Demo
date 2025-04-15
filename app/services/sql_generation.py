import json
import sys
import os
import re
from typing import Dict, Any

# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.schemas.sql_schema import SQLQueryRequest, SQLQueryResponse, DatabaseSchema
from app.services.llm import client

def schema_to_string(schema: DatabaseSchema) -> str:
    """Convert database schema to a formatted string representation."""
    schema_str = "DATABASE SCHEMA:\n\n"
    
    for table in schema.tables:
        schema_str += f"Table: {table.name}\n"
        schema_str += "Columns:\n"
        
        for column in table.columns:
            pk_str = "PRIMARY KEY" if column.is_primary_key else ""
            nullable_str = "NOT NULL" if not column.is_nullable else ""
            fk_str = f"REFERENCES {column.foreign_key}" if column.foreign_key else ""
            
            schema_str += f"  - {column.name} ({column.data_type}) {pk_str} {nullable_str} {fk_str}\n"
        
        schema_str += "\n"
    
    return schema_str

def generate_sql_query(request: SQLQueryRequest) -> SQLQueryResponse:
    """
    Generate SQL query from natural language using the Gemini model.
    """
    try:
        if not request.schema:
            return SQLQueryResponse(
                sql_query="",
                error="Database schema is required"
            )
        
        schema_str = schema_to_string(request.schema)
        
        prompt = f"""
        You are a SQL expert. Given the following database schema and a natural language query,
        generate the SQL query that would answer the question. Return ONLY valid SQL for PostgreSQL.
        
        {schema_str}
        
        User Query: {request.natural_language_query}
        
        Format your response as follows:
        ```sql
        SQL_QUERY_HERE
        ```
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        
        # Extract SQL from the response
        response_text = response.text
        
        # Find SQL query between ```sql and ``` tags
        sql_match = re.search(r'```sql\n(.*?)\n```', response_text, re.DOTALL)
        
        if sql_match:
            sql_query = sql_match.group(1).strip()
            return SQLQueryResponse(
                sql_query=sql_query,
                explanation="SQL query generated successfully"
            )
        else:
            # If no proper formatting, just extract the SQL-looking part
            return SQLQueryResponse(
                sql_query=response_text.strip(),
                explanation="Generated query may need review"
            )
            
    except Exception as e:
        return SQLQueryResponse(
            sql_query="",
            error=f"Error generating SQL query: {str(e)}"
        )
