import json
import sys
import os
import re
from typing import Dict, Any

# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.schemas.sql_schema import SQLQueryRequest, SQLQueryResponse, DatabaseSchema
from app.services.llm import client

# Add LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate

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
    Generate SQL query from natural language using the Gemini model with LangChain structured output.
    """
    try:
        if not request.schema:
            return SQLQueryResponse(
                sql_query="",
                error="Database schema is required"
            )
        
        schema_str = schema_to_string(request.schema)
        print(schema_str)
        
        # Create Google Gemini LLM instance through LangChain
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
        
        # Use LangChain's structured output with our SQLQueryResponse class
        structured_llm = llm.with_structured_output(SQLQueryResponse)
        
        # Create the prompt for the LLM
        prompt = f"""
        You are a SQL expert. Given the following database schema and a natural language query,
        generate the SQL query that would answer the question. Return valid SQL for PostgreSQL.
        
        {schema_str}
        
        User Query: {request.natural_language_query}
        
        Generate a SQL query that correctly addresses the user's question based on the schema provided.
        Provide a brief explanation of what the query does.
        """
        
        # Get structured output directly
        response = structured_llm.invoke(prompt)
        return response
            
    except Exception as e:
        return SQLQueryResponse(
            sql_query="",
            error=f"Error generating SQL query: {str(e)}"
        )
