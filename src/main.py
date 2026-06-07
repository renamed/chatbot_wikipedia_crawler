import selectors

import asyncio
from sentence_transformers import SentenceTransformer

from parsers.wikipedia_parser import WikipediaParser
from parsers.xml_parser import XmlParser
from repository.wiki_data_repository import WikidataRepository
from utils.logging import setup_logging
from utils.text_utils import split_text


async def main():
    logger = setup_logging()
    logger.info("Starting Wikipedia dump processing pipeline...")

    xmlParser = XmlParser()
    wikipediaParser = WikipediaParser()

    logger.info("START - download sentence transformer model")
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")
    logger.info("END - download sentence transformer model")

    
    for page in xmlParser.parse("C:\\Users\\User\\Desktop\\ptbr_wiki\\ptwiki-latest-pages-articles.xml"):
        try:
            async with WikidataRepository() as repo:            
                if await repo.page_exists(page.page_id, page.revision_id):
                    logger.info("Page '%s' (ID: %s) already exists. Skipping.", page.title, page.page_id)
                    continue

                logger.info("Processing page title %s", page.title)

                text = wikipediaParser.parse_text(page.text)
                text_split = split_text(text)
                embeddings = model.encode(text_split, show_progress_bar=False)
                
                records = []
                for chunk_idx, (chunk_text, embedding) in enumerate(zip(text_split, embeddings)):                
                    sha_bytes = page.text_sha.encode('utf-8')

                    records.append((
                        page.title,
                        page.page_id,
                        page.revision_id,
                        chunk_idx,
                        sha_bytes,
                        chunk_text,
                        page.timestamp,
                        embedding.tolist()
                    ))
                
                await repo.bulk_insert(records)
                logger.info("Successfully save %s chunks for page %s", len(records), page.title)
        except:
            logger.error("Pipeline failed while processing page '%s'", page.title, exc_info=True)
            logger.info("Continuing to next page")
                

    
if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda:asyncio.SelectorEventLoop(selectors.SelectSelector())
    )