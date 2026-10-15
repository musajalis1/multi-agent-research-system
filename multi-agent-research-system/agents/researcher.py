from tools.search import search_wikipedia


class Researcher:
    def __init__(self, search=search_wikipedia, max_sources=5):
        self.search = search
        self.max_sources = max_sources

    def run(self, question):
        return self.search(question, self.max_sources)
