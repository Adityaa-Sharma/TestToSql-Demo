from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class Column(BaseModel):
    name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    foreign_key: Optional[str] = None
    
class Table(BaseModel):
    name: str
    columns: List[Column]
    
class DatabaseSchema(BaseModel):
    tables: List[Table]
    
class SQLQueryRequest(BaseModel):
    natural_language_query: str
    schema: Optional[DatabaseSchema] = None
    
class SQLQueryResponse(BaseModel):
    sql_query: str
    explanation: Optional[str] = None
    error: Optional[str] = None

class SQLGenerationModel(BaseModel):
    """Pydantic model for LLM structured output with both input and output fields."""
    # Input fields
    natural_language_query: str = Field(..., description="The natural language query from the user")
    schema_description: str = Field(..., description="Database schema in string format")
    
    # Output fields
    sql_query: str = Field(..., description="The SQL query that answers the natural language query")
    explanation: str = Field(default="", description="Explanation of what the SQL query does")
    
    class Config:
        jaon_schema_extra = {
            "example": {
                "natural_language_query": "Show me all customers from New York",
                "schema_description": "Table: customers\nColumns:\n- id (int) PRIMARY KEY\n- name (varchar)\n- city (varchar)",
                "sql_query": "SELECT * FROM customers WHERE city = 'New York';",
                "explanation": "This query selects all customers whose city is New York."
            }
        }
