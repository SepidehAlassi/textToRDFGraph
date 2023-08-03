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

    def toJson(instance):  # get a class instance
        return instance.__dict__  # convert it to dictionary and return


class GeoEntity(Entity):
    def __init__(self, text, label, start_char=0, end_char=0, wiki_id="", lang="en", iri='', document='', geoname_id="",
                 lon=None, lat=None):
        super().__init__(text, label, start_char, end_char, wiki_id, lang, iri, document)
        self.geoname_id = geoname_id  # GeoName ID of the location extracted from wikidata
        self.longitude = lon  # Longitude of the location extracted from wikidata
        self.latitude = lat  # Latitude of the location extracted from wikidata


class PersonEntity(Entity):
    def __init__(self, text, label, start_char=0, end_char=0, wiki_id="", lang="en", iri='', document='', gnd="",
                 given_name="", family_name="", gender=""):
        super().__init__(text, label, start_char, end_char, wiki_id, lang, iri, document)
        self.gnd = gnd  # GND number of the person extracted from wikidata
        self.given_name = given_name  # Given name of the person extracted from wikidata
        self.family_name = family_name  # Family name of the person extracted from wikidata
        self.gender = gender


def from_json(dct):
    output = {'Locations': {}, 'Persons': {}}
    for key, locs in dct['Locations'].items():
        output['Locations'][key] = []
        for loc in locs:
            output['Locations'][key].append(GeoEntity(text=loc['text'],
                                                      label=loc['label'],
                                                      start_char=loc['start_char'],
                                                      end_char=loc['end_char'],
                                                      wiki_id=loc['wiki_id'],
                                                      lang=loc['language'],
                                                      iri=loc['iri'],
                                                      document=loc['document'],
                                                      geoname_id=loc['geoname_id'],
                                                      lon=loc['longitude'],
                                                      lat=loc['latitude']
                                                      ))

    for pers_key, values in dct['Persons'].items():
        output['Persons'][pers_key] = []
        for pers in values:
            output['Persons'][pers_key].append(PersonEntity(text=pers['text'],
                                                            label=pers['label'],
                                                            start_char=pers['start_char'],
                                                            end_char=pers['end_char'],
                                                            wiki_id=pers['wiki_id'],
                                                            lang=pers['language'],
                                                            iri=pers['iri'],
                                                            document=pers['document'],
                                                            gnd=pers['gnd'],
                                                            given_name=pers['given_name'],
                                                            family_name=pers['family_name'],
                                                            gender=pers['gender']))
    return output


if __name__ == '__main__':
    pers1 = PersonEntity("firstPers", "pers1", 0, 3)
    pers2 = PersonEntity("2ndPers", "pers2", 4, 10)
    pers3 = PersonEntity("3rdPers", "pers3", 12, 18)
    persons = [pers3, pers1, pers2]
    sorted_list = sorted(persons, key=lambda x: x.start_char)
    print(sorted_list)
