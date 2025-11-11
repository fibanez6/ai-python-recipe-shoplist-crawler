import sqlite3
from pathlib import Path
from typing import Any, Optional

import sqlite_utils
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "shoplist.db"

class DatabaseQuery(BaseModel):
    query: str
    params: Optional[list[Any]] = None

class SearchRequest(BaseModel):
    table: str
    search_term: str
    limit: int = 10

class DBManager:
    def __init__(self, db_path=DB_PATH):
        self.db = sqlite_utils.Database(db_path)

    # def create_table(self, table_name, columns):
    #     """
    #     Create a table if it doesn't exist.
    #     columns: dict of column_name: type (e.g. {"name": str, "quantity": int})
    #     """
    #     self.db[table_name].create(columns, pk=None, not_null=None, defaults=None, if_not_exists=True)

    # def insert(self, table_name, record):
    #     """
    #     Insert a record (dict) into the table.
    #     """
    #     self.db[table_name].insert(record)

    # def query(self, table_name, where=None):
    #     """
    #     Query records from a table. Optionally filter with a where dict.
    #     """
    #     if where:
    #         return list(self.db[table_name].rows_where(where))
    #     return list(self.db[table_name].rows)

    # def update(self, table_name, pk, updates):
    #     """
    #     Update a record by primary key.
    #     """
    #     self.db[table_name].update(pk, updates)

    # def delete(self, table_name, pk):
    #     """
    #     Delete a record by primary key.
    #     """
    #     self.db[table_name].delete(pk)

    async def execute_query(request: DatabaseQuery):
        """Execute a custom SQL query."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if request.params:
                cursor.execute(request.query, request.params)
            else:
                cursor.execute(request.query)
            
            if request.query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                data = [dict(zip(columns, row)) for row in results]
            else:
                conn.commit()
                data = {"affected_rows": cursor.rowcount}
            
            conn.close()
            return {"success": True, "data": data}
            
        except sqlite3.Error as e:
            raise e

    async def search_data(request: SearchRequest):
        """Search for data in the database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if request.table == "fetched_data":
                query = """
                    SELECT id, url, substr(content, 1, 200) as content_preview, metadata, timestamp
                    FROM fetched_data 
                    WHERE url LIKE ? OR content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                search_pattern = f"%{request.search_term}%"
                cursor.execute(query, (search_pattern, search_pattern, request.limit))
                
            elif request.table == "scraped_data":
                query = """
                    SELECT id, url, title, substr(content, 1, 200) as content_preview, extracted_data, timestamp
                    FROM scraped_data 
                    WHERE url LIKE ? OR title LIKE ? OR content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                search_pattern = f"%{request.search_term}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, request.limit))
            else:
                raise Exception("Invalid table name")
            
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            data = [dict(zip(columns, row)) for row in results]
            
            conn.close()
            return {"success": True, "results": data, "count": len(data)}
            
        except sqlite3.Error as e:
            raise e
        
    async def get_database_stats():
        """Get database statistics."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Count records in each table
            cursor.execute("SELECT COUNT(*) FROM fetched_data")
            fetched_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM scraped_data")
            scraped_count = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute("""
                SELECT url, timestamp FROM fetched_data 
                ORDER BY timestamp DESC LIMIT 5
            """)
            recent_fetches = cursor.fetchall()
            
            cursor.execute("""
                SELECT url, title, timestamp FROM scraped_data 
                ORDER BY timestamp DESC LIMIT 5
            """)
            recent_scrapes = cursor.fetchall()
            
            conn.close()
            
            return {
                "fetched_data_count": fetched_count,
                "scraped_data_count": scraped_count,
                "recent_fetches": [{"url": r[0], "timestamp": r[1]} for r in recent_fetches],
                "recent_scrapes": [{"url": r[0], "title": r[1], "timestamp": r[2]} for r in recent_scrapes]
            }
            
        except sqlite3.Error as e:
            raise e