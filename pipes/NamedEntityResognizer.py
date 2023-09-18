from pipes.util.NLP_Parser.spacyParser import SpacyParser
from spacy import displacy
from flair.models import SequenceTagger
from flair.data import Sentence
import os
from Entitiy import GeoEntity, PersonEntity
from pipes.PreProcessor import Input, preprocess_input

articles_to_strip = ('der ', 'die ', 'das ', 'the ')


def sanitize_entity(text, start_char, end_char, lang):
    if lang == 'fa':
        text = text.strip('،')
        end_char = end_char - 1
    else:
        text = text[4:]
        start_char = start_char + 4
    return text, start_char, end_char


class SpacyNERParser:
    def __init__(self):
        self.locationLabels = ['GPE', 'LOC']
        self.personLabels = ['PER', 'PERSON']

    def extract_person_entities(self, entities, lang):
        """
        Extract person named entities with Spacy
        :param entities: already extracted named entities of the project
        :param lang: language of the input text
        :return: person entities
        """
        found_persons = []
        person_entities = list(filter(lambda ent: ent.label_ in self.personLabels, entities))

        for ent in person_entities:
            text = ent.text
            end_char = ent.end_char
            start_char = ent.start_char
            if text.startswith(articles_to_strip) or lang == 'fa':
                text, start_char, end_char = sanitize_entity(text=text, end_char=end_char, start_char=start_char, lang=lang)
            entity = PersonEntity(text=text, label=ent.label_, start_char=start_char, end_char=end_char,
                                  lang=lang)
            found_persons.append(entity)

        return found_persons

    def extract_location_entities(self, entities, lang):
        """
        Extract location named entities with Spacy
        :param entities: already extracted named entities of the project
        :param lang: language of the input text
        :return: location entities
        """
        found_locations = []
        geo_entities = list(filter(lambda ent: ent.label_ in self.locationLabels, entities))

        for ent in geo_entities:
            text = ent.text
            end_char = ent.end_char
            start_char = ent.start_char
            if text.startswith(articles_to_strip) or lang == 'fa':
                text, start_char, end_char = sanitize_entity(text=text, end_char=end_char, start_char=start_char,
                                                             lang=lang)

            entity = GeoEntity(text=text, label=ent.label_, start_char=start_char, end_char=end_char,
                               lang=lang)
            found_locations.append(entity)

        return found_locations

    def extract_ne(self, inputs: Input):
        """
        Extract named entities from the input text with Spacy
        :param inputs: preprocessed inputs of the pipeline
        :return: found location and person entities.
        """

        def store_ner_vis(doc, inputs: Input):
            html = displacy.render(doc, style="ent")
            filepath = os.path.join(inputs.project_name, inputs.doc_name + '_text.html')
            with open(filepath, "w", encoding="utf-8") as output_file:
                output_file.write(html)

        doc = SpacyParser().spacy_parse(inputs.text, inputs.lang)
        store_ner_vis(doc, inputs)
        locations = self.extract_location_entities(doc.ents, inputs.lang)
        persons = self.extract_person_entities(doc.ents, inputs.lang)
        return locations, persons


class FlairNERParser:
    def __init__(self):
        self.location_label = 'LOC'
        self.person_label = 'PER'
        self.ner_models_dict = {'en': "flair/ner-english-large",
                                'de': "flair/ner-german-large",
                                'fa': 'hamedkhaledi/persain-flair-ner'}

    def extract_ne(self, inputs: Input):
        """
        Extract named entities with flair
        :param inputs: collection of input data
        :return: location and person entities
        """
        tagger = SequenceTagger.load(self.ner_models_dict[inputs.lang])

        # make example sentences
        sentence = Sentence(inputs.text)

        # predict NER tags
        tagger.predict(sentence)

        found_entities = sentence.get_spans('ner')
        locations = self.extract_location_entities(found_entities, inputs.lang)
        persons = self.extract_person_entities(found_entities, inputs.lang)
        return locations, persons

    def extract_location_entities(self, entities, lang):
        """
        Extract location entities with flair
        :param entities: already extracted entities of the project
        :param lang: language of the text
        :return: location entities
        """
        extracted_locations = []

        for entity in entities:
            tag = entity.get_label('ner')

            if tag.value == self.location_label:
                text = entity.text
                end_char = entity.end_position
                start_char = entity.start_position
                if text.startswith(articles_to_strip) or lang == 'fa':
                    text, start_char, end_char = sanitize_entity(text=text, end_char=end_char, start_char=start_char,
                                                                 lang=lang)

                loc_entity = GeoEntity(text=text, label=tag.value, start_char=start_char,
                                       end_char=end_char, lang=lang)
                extracted_locations.append(loc_entity)

        return extracted_locations

    def extract_person_entities(self, entities, lang):
        """
        Extract person entities with flair
        :param entities: already extracted entities of the project
        :param lang: language of the text
        :return: person entities
        """
        extracted_persons = []
        for entity in entities:
            tag = entity.get_label('ner')

            if tag.value == self.person_label:
                text = entity.text
                end_char = entity.end_position
                start_char = entity.start_position
                if text.startswith(articles_to_strip) or lang == 'fa':
                    text, start_char, end_char = sanitize_entity(text=text, end_char=end_char, start_char=start_char,
                                                                 lang=lang)
                pers_entity = PersonEntity(text=text, label=tag.value,
                                           start_char=start_char,
                                           end_char=end_char,
                                           lang=lang)
                extracted_persons.append(pers_entity)
        return extracted_persons


def parse_NE(parser_type, inputs: Input):
    """
    Parse named entities from input text
    :param parser_type: type of parser to use, spacy or flair
    :param inputs: collection of input data
    :return: location and person entities
    """
    if parser_type == 'flair':
        print('NER with flair')
        parser = FlairNERParser()
    else:
        print('NER with spaCy')
        parser = SpacyNERParser()
    return parser.extract_ne(inputs)


def ner_test(parser, inputs: Input):
    def pretty_print(locations):
        return '\n'.join([str(d.text) + ' ' + str(d.label) for d in locations])

    found_locations, found_persons = parse_NE(parser, inputs)
    str_loc = pretty_print(found_locations)
    str_pers = pretty_print(found_persons)
    print("---English---\nLocations found:", len(found_locations))
    print(str_loc)
    print("---English---\nPersons found:", len(found_persons))
    print(str_pers)
    return found_persons, found_locations


if __name__ == '__main__':
    text_path = os.path.join(os.path.dirname(__file__), '..',  'inputs', 'test_data', 'magellan_voyage', 'en_magellan_voyage.txt')
    project_name = 'magellan'
    inputs = preprocess_input(text_path=text_path, project_name=project_name)
    persons, locations = ner_test('spacy', inputs)
    unique_pers = set([pers.text for pers in persons])
    unique_locs = set([loc.text for loc in locations])
    print(len(unique_locs), len(unique_pers))
