from dataclasses import dataclass
from lxml import etree


@dataclass
class WikipediaPage:
    title: str
    page_id: int
    revision_id: int
    text_sha: str
    text: str
    timestamp: str


class XmlParser:
    NS = "{http://www.mediawiki.org/xml/export-0.11/}"

    def parse(self, file_path: str):
        tag = f"{self.NS}page"
        for event, elem in etree.iterparse(file_path, tag=tag, huge_tree=True):
            ns_elem = elem.find(f"{self.NS}ns")
            if ns_elem is None or ns_elem.text != "0":
                self.__clear_parents(elem)
                continue

            title = elem.find(f"{self.NS}title").text
            page_id = int(elem.find(f"{self.NS}id").text)

            revision = elem.find(f"{self.NS}revision")
            revision_id = int(revision.find(f"{self.NS}id").text)
            timestamp = revision.find(f"{self.NS}timestamp").text

            sha_elem = revision.find(f"{self.NS}sha1")
            text_sha = sha_elem.text if sha_elem is not None else ""

            text_elem = revision.find(f"{self.NS}text")
            text = text_elem.text if text_elem is not None else ""

            page = WikipediaPage(
                title=title,
                page_id=page_id,
                revision_id=revision_id,
                text_sha=text_sha,
                text=text,
                timestamp=timestamp,
            )
            yield page

            self.__clear_parents(elem)

    def __clear_parents(self, elem):
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]