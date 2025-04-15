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
