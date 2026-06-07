
from typing import Any, List, Tuple

from pgvector.psycopg import register_vector_async
import psycopg


class WikidataRepository:

    def __init__(self):
        self._conn = None

    async def open_connection(self) -> None:
        if self._conn is None or self._conn.closed:
            self._conn = await psycopg.AsyncConnection.connect("postgresql://postgres:123@localhost:5431/chatbot_wikipedia")
            await register_vector_async(self._conn)

    async def close_connection(self) -> None:
        if self._conn and not self._conn.closed:
            await self._conn.close()

    async def __aenter__(self):
        await self.open_connection()
        return self
    
    async def __aexit__(self, exc_type, exc_eval, exc_tb):
        
        if self._conn and not self._conn.closed:
            if exc_type:    
                await self._conn.rollback()
            else:
                await self._conn.commit()
        
        await self.close_connection()

    async def bulk_insert(self, records: List[Tuple[Any, ...]]) -> None:
        if self._conn is None or self._conn.closed:
            raise RuntimeError("Connection not open")
        
        async with self._conn.cursor() as cur:
            await cur.executemany("""
                                  INSERT INTO wiki_page (
                                    title, page_id, revision_id, chunk_index, text_sha, body, timestamp, embedding
                                  ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s
                                  )                                  
                                  """, records)
            
    async def page_exists(self, page_id: int, revision_id: int) -> bool:
        if self._conn is None or self._conn.closed:
            raise RuntimeError("Connection not open")
        
        async with self._conn.cursor() as cur:
            await cur.execute(
                "SELECT 1 FROM wiki_page WHERE page_id = %s AND revision_id = %s LIMIT 1",
                (page_id, revision_id)
            )
            result = await cur.fetchone()
            return result is not None


