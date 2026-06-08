from datetime import datetime
from logging import Logger
import selectors
import asyncio
from sentence_transformers import SentenceTransformer

from parsers.wikipedia_parser import WikipediaParser
from parsers.xml_parser import XmlParser
from external.wiki_data_repository import WikidataRepository
from utils.logging import setup_logging
from utils.text_utils import split_text

MAX_CHUNKS_BUFFER_COUNT = 20480
async def main():
    logger = setup_logging()
    logger.info("Starting Wikipedia dump processing pipeline...")

    xmlParser = XmlParser()
    wikipediaParser = WikipediaParser()

    logger.debug("START - download sentence transformer model")
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")
    logger.debug("END - download sentence transformer model")
    
    chunks_buffer = []
    initial_time: datetime = None

    async with WikidataRepository() as repo:
        for page in xmlParser.parse("C:\\Users\\User\\Desktop\\ptbr_wiki\\ptwiki-latest-pages-articles.xml"):
            try:
                if await repo.page_exists(page.page_id, page.revision_id):
                    logger.debug("Page '%s' (ID: %s) already exists. Skipping.", page.title, page.page_id)
                    continue

                if initial_time is None:
                    initial_time = datetime.now()

                logger.debug("Processing page title %s", page.title)

                text = wikipediaParser.parse_text(page.text)
                text_split = split_text(text)
                if not text_split:
                    logger.warning("Empty text split in page %s with text %s", page.title, text)
                    continue

                sha_bytes = page.text_sha.encode('utf-8')  
                chunks_buffer.extend([
                    {
                        "title": page.title,
                        "page_id": page.page_id,
                        "revision_id": page.revision_id,
                        "chunk_idx": chunk_idx,
                        "sha_bytes": sha_bytes,
                        "chunk_text": chunk_text,
                        "timestamp": page.timestamp
                    }

                    for chunk_idx, chunk_text in enumerate(text_split)
                ])

                buffer_size =len(chunks_buffer)
                if buffer_size >= MAX_CHUNKS_BUFFER_COUNT:
                    await send_to_db(logger, model, chunks_buffer, repo, initial_time)
                    chunks_buffer = []
                    initial_time = datetime.now()
            except Exception:
                logger.error("Pipeline failed while processing page '%s'", page.title, exc_info=True)
                logger.debug("Continuing to next page")

        if len(chunks_buffer) > 0:
            await send_to_db(logger, model, chunks_buffer, repo, initial_time)
            chunks_buffer = []
            initial_time = datetime.now()

        logger.info("Finished process")

async def send_to_db(logger: Logger, model: SentenceTransformer, chunks_buffer: list, repo: WikidataRepository, initial_time: datetime) -> None:
    logger.debug("Processing batch size %s", len(chunks_buffer))

    embedding_text = [item["chunk_text"] for item in chunks_buffer]
    
    logger.info("Start model encoding for %s chunks", len(chunks_buffer))
    embeddings = model.encode(embedding_text, batch_size=2048, show_progress_bar=False)
    logger.info("Finished model enconding")

    embeddings_list = embeddings.tolist()

    records = [
        (
            item["title"],
            item["page_id"],
            item["revision_id"],
            item["chunk_idx"],
            item["sha_bytes"],
            item["chunk_text"],
            item["timestamp"],
            embeddings_list[idx]
        )
        for idx, item in enumerate(chunks_buffer)
    ]

    logger.info("Start bulk insert for %s chunks", len(chunks_buffer))
    await repo.bulk_insert(records)
    logger.info("Finished bulk insert for %s chunks", len(chunks_buffer))

    show_elapsed_time(len(chunks_buffer), logger, initial_time)
    logger.debug("Successfully saved batch of %s chunks to database.", len(records))

def show_elapsed_time(tokens_written: int, logger: Logger, initial_time: datetime):    
    now = datetime.now()
    diff = now - initial_time

    logger.info("Tokens written %s in %s", tokens_written, diff)

if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    )