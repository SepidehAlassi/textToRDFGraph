from pipes.util.NLP_Parser.spacyParser import SpacyParser
import os
import json


class SentenceComp:
    def __init__(self, text, token, ent={}):
        self.text = text
        self.token = token
        self.entity = ent


class Sentence:
    def __init__(self, subj='', verb='', obj=''):
        self.subj = subj
        self.obj = obj
        self.verb = verb


class DependencyParser:
    def __init__(self, text, lang):
        self.text = text
        self.lang = lang
        self.compound_tags = ['compound', 'pnc']
        self.subject_tags = ['nsubj', 'nsubjpass', 'sb']
        self.object_tags = ['pobj', 'dobj', 'iobj', 'nk']

    def parse_sentence(self, sent):
        """
        Parse subject, verb, and object out of the sentence
        :param sent: input sentence
        :return: sentence components
        """

        subjects = [token for token in sent if token.dep_ in self.subject_tags]
        objects = [token for token in sent if token.dep_ in self.object_tags]
        found_sent_objects = []
        if len(subjects) == 0 or len(objects) == 0:
            return found_sent_objects
        for subject in subjects:
            sent_obj = Sentence()
            compound = [token for token in sent if token.dep_ in self.compound_tags and token.head == subject]

            if len(compound):
                sent_obj.subj = SentenceComp(compound[0].text + ' ' + subject.text, subject)
            else:
                sent_obj.subj = SentenceComp(subject.text, subject)

            if subject.head.dep_ == 'ROOT':
                if subject.head.pos_ == 'VERB':
                    verb = subject.head
                else:
                    if subject.head.pos_ == 'AUX':
                        main_verb = [token for token in sent if token.head == subject.head and token.pos_ == 'VERB']
                        if len(main_verb):
                            verb = main_verb[0]
                        else:
                            verb = subject.head
                sent_obj.verb = SentenceComp(verb.text, verb)
                prep_found = [token for token in sent if token.pos_ == 'ADP' and token.head == verb]
                if len(prep_found) > 0:
                    prep = prep_found[0]
                    sent_obj.verb.text += ' ' + prep.text

                for obj in objects:
                    sent_obj.obj = SentenceComp(obj.text, obj)
            if sent_obj.obj != '' and sent_obj.subj != '' and sent_obj.verb != '':
                found_sent_objects.append(sent_obj)
            conjs = [token for token in sent if token.dep_ == 'conj']
            for conj in conjs:
                new_obj = Sentence(sent_obj.subj, sent_obj.verb, sent_obj.obj)
                compound = [token for token in sent if token.dep_ in self.compound_tags and token.head == conj]
                comp = ''
                if len(compound):
                    comp = compound[0].text + ' '

                if conj.head.dep_ in self.subject_tags:
                    new_obj.subj = SentenceComp(comp + conj.text, conj)
                else:  # objects
                    new_obj.obj = SentenceComp(comp + conj.text, conj)
                if new_obj.obj != '' and new_obj.subj != '' and new_obj.verb != '':
                    found_sent_objects.append(new_obj)

        return found_sent_objects

    def get_sent_components(self):
        """
        Get the components of sentences in the text
        :return: a dictionary with sentence index and components found in that sentence describing relation.
        """
        def get_sentences():
            """
            This function breaks the text into sentences.
            :param text: input text
            :return: list of sentences
            """
            checkString = lambda s: any(c.isalpha() for c in s) or any(c.isdigit() for c in s)
            sents = [elem+'.' for elem in self.text.split('.\n') if checkString(elem)]
            return sents

        sentences = get_sentences()
        sent_components = {}
        for idx, sentence in enumerate(sentences):
            sent = SpacyParser().spacy_parse(text=sentence, lang=self.lang)
            sent_comp = self.parse_sentence(sent)
            if len(sent_comp):
                sent_components[idx] = sent_comp
        return sent_components


def get_entity_of_sentence_component(sentence_components, entities, lang):
    """
    1. Get the entity record corresponding to a parsed sentence component
    2. Make a stack of person entities of the text for pronoun resolution later
    :param sentence_components: the extracted entity relations through dependency parsing
    :param entities: previously extracted named entities
    :param lang:language of the text
    :return: updated sentence components and persons stack
    """
    pers_labels = ['PERSON', 'PER']

    def get_ne_record_of_token(component, persons):
        if component.token.pos_ == 'PROPN':
            ent_type = component.token.ent_type_
            if ent_type in pers_labels:
                for _, pers_items in entities['Persons'].items():
                    found_pers = [pers_item for pers_item in pers_items if
                                 pers_item.text == component.text and pers_item.language == lang]
                    if len(found_pers) > 0:
                        persons.append(found_pers[0])
                        component.entity = found_pers[0]
                        break
            else:
                for _, loc_items in entities['Locations'].items():
                    found_loc = [loc_item for loc_item in loc_items if loc_item.text == component.text and loc_item.language == lang]
                    if len(found_loc) > 0:
                        component.entity = found_loc[0]
                        break
    #collect person entities for pronoun resolution later
    pers_stack = {}
    for sent_num, sent_rels in sentence_components.items():
        persons = []
        for sentence_instance in sent_rels:
            get_ne_record_of_token(sentence_instance.subj, persons)
            get_ne_record_of_token(sentence_instance.obj, persons)
        pers_stack[sent_num] = persons
    return sentence_components, pers_stack


def parse_dependencies(text, project_name, lang, entities):
    """
    Parse dependencies of tokens in the text.
    :param text: input text
    :param project_name: input project name
    :param lang: language of the text
    :param entities: extracted named entities
    :return: sentence components and persons stack extracted form the text
    """
    pos_parser = DependencyParser(text, lang)
    sent_components = pos_parser.get_sent_components()
    sent_components, pers_stack = get_entity_of_sentence_component(sent_components, entities, lang)
    return sent_components, pers_stack


if __name__ == '__main__':
    test_sent_en = 'Jacob Bernoulli however only lived in Basel. He traveled though to Geneva, Lyon, Bordeaux, Amsterdam, and London.'
    with open(os.path.join(os.getcwd(), 'dh2023', 'dh2023' + '_entities.json')) as input_file:
        entities = json.load(input_file)
    parse_dependencies(test_sent_en, 'testing', 'en', entities)
