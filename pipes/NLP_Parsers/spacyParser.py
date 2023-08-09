import spacy

models_dict = {'en': "en_core_web_lg",
               'de': "de_core_news_lg",
               'fr': "fr_core_news_lg",
               'it': "it_core_news_lg"}


class SpacyParser:
    def __init__(self):
        pass

    def spacy_parse(self, text, lang='en', disable=[]):
        model = spacy.load(models_dict[lang], disable=disable)
        doc = model(text)
        return doc








