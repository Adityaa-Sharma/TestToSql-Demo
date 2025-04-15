import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.connection import get_db_cursor
from app.schemas.sql_schema import Column, Table, DatabaseSchema

def get_database_schema() -> DatabaseSchema:
    """
    Fetches the database schema from PostgreSQL including tables and their columns.
    """
    schema = DatabaseSchema(tables=[])
    
    try:
        with get_db_cursor() as cursor:
            # Get all tables in the database
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE';
            """)
            
            tables = cursor.fetchall()
            
            for table_row in tables:
                table_name = table_row[0]
                
                # Get columns for this table
                cursor.execute("""
                    SELECT 
                        column_name, 
                        data_type, 
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s;
                """, (table_name,))
                
                columns_data = cursor.fetchall()
                columns = []
                
                # Get primary keys
                cursor.execute("""
                    SELECT 
                        kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY' 
                    AND kcu.table_name = %s;
                """, (table_name,))
                
                primary_keys = [row[0] for row in cursor.fetchall()]
                
                # Get foreign keys
                cursor.execute("""
                    SELECT 
                        kcu.column_name,
                        ccu.table_name as foreign_table_name,
                        ccu.column_name as foreign_column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage ccu 
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND kcu.table_name = %s;
                """, (table_name,))
                
                foreign_keys = {row[0]: f"{row[1]}.{row[2]}" for row in cursor.fetchall()}
                
                for column_data in columns_data:
                    column_name = column_data[0]
                    data_type = column_data[1]
                    is_nullable = column_data[2] == 'YES'
                    
                    columns.append(Column(
                        name=column_name,
                        data_type=data_type,
                        is_nullable=is_nullable,
                        is_primary_key=column_name in primary_keys,
                        foreign_key=foreign_keys.get(column_name)
                    ))
                
                schema.tables.append(Table(name=table_name, columns=columns))
                
        return schema
    
    except Exception as e:
        print(f"Error fetching database schema: {e}")
        return DatabaseSchema(tables=[])
