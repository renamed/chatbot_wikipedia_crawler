from dataclasses import dataclass
from typing import Any, List, Tuple

from pgvector.psycopg import register_vector_async
import psycopg

@dataclass(frozen=True)
class ExistingPageResponse:
    page_id: int
    revision_id: int

class WikidataRepository:

    def __init__(self):
        self._conn = None
        self._existing_pages = None

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
        
        await self._conn.commit()
        
        if self._existing_pages is not None:
            self._existing_pages.update(
                ExistingPageResponse(page_id=row[1], revision_id=row[2]) for row in records
            )
            
    async def page_exists(self, page_id: int, revision_id: int) -> bool:
        if self._existing_pages is None:
            self._existing_pages = await self.list_existing_pages()
        
        expected_page = ExistingPageResponse(page_id, revision_id)
        return expected_page in self._existing_pages

    async def list_existing_pages(self) -> set[ExistingPageResponse]:
        if self._conn is None or self._conn.closed:
            raise RuntimeError("Connection not open")

        async with self._conn.cursor() as cur:
            await cur.execute("SELECT page_id, revision_id FROM wiki_page GROUP BY page_id, revision_id")
            rows = await cur.fetchall()
            return {ExistingPageResponse(page_id=row[0], revision_id=row[1]) for row in rows}