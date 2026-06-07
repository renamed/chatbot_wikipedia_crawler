from semantic_text_splitter import TextSplitter

def split_text(text: str, max_characters: int = 1000, neighbor_overlap :int = 250) -> list[str]:
    splitter = TextSplitter(capacity=max_characters, overlap=neighbor_overlap, trim=True)
    return splitter.chunks(text)