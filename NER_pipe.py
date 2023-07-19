from spacyParser import SpacyParser
from spacy import displacy
from flair.models import SequenceTagger
from flair.data import Sentence
import os
from Entitiy import GeoEntity, PersonEntity


class SpacyNERParser:
    def __init__(self):
        self.locationLabels = ['GPE', 'LOC']
        self.personLabels = ['PER', 'PERSON']

    def extract_person_entities(self, entities, lang):
        found_persons = []
        person_entities = list(filter(lambda ent: ent.label_ in self.personLabels, entities))

        for ent in person_entities:
            entity = PersonEntity(text=ent.text, label=ent.label_, start_char=ent.start_char, end_char=ent.end_char,
                                  lang=lang)
            found_persons.append(entity)

        return found_persons

    def extract_location_entities(self, entities, lang):
        found_locations = []
        geo_entities = list(filter(lambda ent: ent.label_ in self.locationLabels, entities))

        for ent in geo_entities:
            entity = GeoEntity(text=ent.text, label=ent.label_, start_char=ent.start_char, end_char=ent.end_char,
                               lang=lang)
            found_locations.append(entity)

        return found_locations

    def get_entities(self, text, lang='en'):
        """
        :param text: the text
        :param lang: language of the text
        :return: parsed doc, found location and person entities.
        """

        def store_ner_vis(doc, lang):
            html = displacy.render(doc, style="ent")
            filepath = os.path.join('output', lang + '_text.html')
            with open(filepath, "w", encoding="utf-8") as output_file:
                output_file.write(html)

        doc = SpacyParser().spacy_parse(text, lang)
        store_ner_vis(doc, lang)
        locations = self.extract_location_entities(doc.ents, lang)
        persons = self.extract_person_entities(doc.ents, lang)
        return locations, persons


class FlairNERParser:
    def __init__(self):
        self.location_label = 'LOC'
        self.person_label = 'PER'
        self.ner_models_dict = {'en': "flair/ner-english-large",
                                'de': "flair/ner-german-large",
                                'fa': 'hamedkhaledi/persain-flair-ner'}

    def get_entities(self, text, lang='en'):
        tagger = SequenceTagger.load(self.ner_models_dict[lang])

        # make example sentences
        sentence = Sentence(text)

        # predict NER tags
        tagger.predict(sentence)

        found_entities = sentence.get_spans('ner')
        locations = self.extract_location_entities(found_entities, lang)
        persons = self.extract_person_entities(found_entities, lang)
        return locations, persons

    def extract_location_entities(self, entities, lang):
        extracted_locations = []
        for entity in entities:
            tag = entity.get_label('ner')

            if tag.value == self.location_label:
                if lang == 'fa':
                    text = entity.text.strip('،')
                else:
                    text = entity.text

                loc_entity = GeoEntity(text=text, label=tag.value, start_char=entity.start_position,
                                       end_char=entity.end_position, lang=lang)
                extracted_locations.append(loc_entity)

        return extracted_locations

    def extract_person_entities(self, entities, lang):
        extracted_persons = []
        for entity in entities:
            tag = entity.get_label('ner')

            if tag.value == self.person_label:
                pers_entity = PersonEntity(text=entity.text, label=tag.value,
                                           start_char=entity.start_position,
                                           end_char=entity.end_position,
                                           lang=lang)
                extracted_persons.append(pers_entity)
        return extracted_persons


def ner_pipe(parser_type, text, lang):
    if parser_type == 'flair':
        print('NER with flair')
        parser = FlairNERParser()
    else:
        print('NER with spaCy')
        parser = SpacyNERParser()
    return parser.get_entities(text, lang)


def ner_test(parser, text, lang):
    def pretty_print(locations):
        return '\n'.join([str(d.text) + ' ' + str(d.label) for d in locations])

    found_locations, found_persons = ner_pipe(parser, text, lang)
    str_loc = pretty_print(found_locations)
    str_pers = pretty_print(found_persons)
    print("---English---\nLocations found:", len(found_locations))
    print(str_loc)
    print("---English---\nPersons found:", len(found_persons))
    print(str_pers)
    return found_persons, found_locations


if __name__ == '__main__':
    with open('/Users/sepidehalassi/dev/ner_lod/test_data/magellan_voyage/en_magellan_voyage.txt') as file:
        test_sent_en = file.read()
    persons, locations = ner_test('flair', test_sent_en, 'en')
    unique_pers = set([pers.text for pers in persons])
    unique_locs = set([loc.text for loc in locations])
    print(len(unique_locs), len(unique_pers))
