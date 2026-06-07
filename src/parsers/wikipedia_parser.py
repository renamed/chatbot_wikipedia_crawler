import mwparserfromhell


class WikipediaParser:

    def parse_text(self, text:str) -> str:
        wikicode = mwparserfromhell.parse(text)
        return wikicode.strip_code()