from pipes.NamedEntityResognizer import FlairNERParser
import os
from flair.models import SequenceTagger
from flair.data import Sentence
from pipes.WikiInformationRetriever import add_wiki_info_person, add_wiki_info_location

# more models on hugging face https://huggingface.co/models?library=flair&sort=downloads



class FlairPosParser:
    def __init__(self):
        self.pos_models_dict = {'en': "flair/pos-english",
                                'de': "flair/de-pos-fine-grained"}

    def get_pos_tags(self, text, lang):
        # load tagger
        tagger = SequenceTagger.load(self.pos_models_dict[lang])

        # make example sentence
        sentence = Sentence(text)

        # predict pos tags
        tagger.predict(sentence)

        # iterate over entities and print
        for entity in sentence.annotation_layers['pos']:
            print(entity)


# Todo: check this for more info on customized model
# https://medium.com/thecyphy/training-custom-ner-model-using-flair-df1f9ea9c762

def flair_ner_test(text, lang, document):
    parser = FlairNERParser()
    _, locations, persons = parser.get_entities(text, lang)
    found_persons = add_wiki_info_person(persons, document)
    found_locations = add_wiki_info_location(locations, document)

    locs_dict = {}
    for loc in found_locations:
        print(loc.text, loc.geoname_id)
        locs_dict[loc.geoname_id] = loc.text

    pers_dict = {}
    for pers in found_persons:
        pers_dict[pers.gnd] = pers.text


def flair_pos_test(text, lang):
    tagger = FlairPosParser()
    tagger.get_pos_tags(text, lang)


if __name__ == '__main__':
    # test_data_path = "../../inputs/test_data/dh2023"
    #
    # test_file = "fa_swiss.txt"
    # test_data = os.path.join(test_data_path, test_file)
    # test_text = open(test_data, "r").read()
    # flair_ner_test(test_text, 'fa', 'fa_swiss')
    flair_pos_test("John wohnte in Basel. Jane ist in Basel geboren. Sie reisten nach Lyon.", 'de')
