class Entity:
    def __init__(self, text, label, start_char=0, end_char=0, wiki_id="", lang="en", iri='', document=''):
        self.label = label  # named entity label: GPE, LOC, PERSON
        self.text = text  # named entity text
        self.start_char = start_char  # start character of the named entity in the text
        self.end_char = end_char  # end character of the named entity in the text
        self.language = lang  # text language
        self.wiki_id = wiki_id  # URL of the wikidata record
        self.iri = iri
        self.document = document


class GeoEntity(Entity):
    def __init__(self, text, label, start_char=0, end_char=0, wiki_id="", lang="en", iri='', document='',
                 geoname_id=""):
        super().__init__(text, label, start_char, end_char, wiki_id, lang, iri, document)
        self.geoNameID = geoname_id  # GeoName ID of the location extracted from wikidata


class PersonEntity(Entity):
    def __init__(self, text, label, start_char=0, end_char=0, wiki_id="", lang="en", iri='', document='', gnd="",
                 given_name="", family_name="", gender=""):
        super().__init__(text, label, start_char, end_char, wiki_id, lang, iri, document)
        self.gnd = gnd  # GND number of the person extracted from wikidata
        self.givenName = given_name  # Given name of the person extracted from wikidata
        self.familyName = family_name  # Family name of the person extracted from wikidata
        self.gender = gender


if __name__ == '__main__':
    pass
