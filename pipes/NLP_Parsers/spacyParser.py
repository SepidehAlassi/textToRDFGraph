import spacy

models_dict = {'en': "en_core_web_lg",
               'de': "de_core_news_lg",
               'fr': "fr_core_news_lg",
               'it': "it_core_news_lg"}


class SpacyParser:
    def __init__(self):
        pass

    def spacy_parse(self, text, lang='en'):
        model = spacy.load(models_dict[lang])
        doc = model(text)
        return doc








