

from parsers.wikipedia_parser import WikipediaParser
from parsers.xml_parser import XmlParser
from utils.logging import setup_logging
from utils.text_utils import split_text


async def init():
    logger = setup_logging()
    logger.info("Starting Wikipedia dump processing pipeline...")

    xmlParser = XmlParser()
    wikipediaParser = WikipediaParser()

    
    for page in xmlParser.parse("C:\\Users\\User\\Desktop\\ptbr_wiki\\ptwiki-latest-pages-articles.xml"):
        logger.debug("Processing page title %s", page.title)

        text = wikipediaParser.parse_text(page.text)
        text_split = split_text(text)
        
        if not text_split:
            logger.warning("Empty text split in page %s with text %s", page.title, text)
            continue

        sha_bytes = page.text_sha.encode('utf-8')  
        page_chunks = [
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
        ]