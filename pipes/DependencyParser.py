from pipes.util.NLP_Parser.spacyParser import SpacyParser
from pipes.NamedEntityResognizer import SpacyNERParser
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
        def get_compound_component(comp):
            compound = [token for token in sent if token.dep_ in self.compound_tags and token.head == comp]
            if len(compound):
                sent_comp = SentenceComp(compound[0].text + ' ' + comp.text, comp)
            else:
                sent_comp = SentenceComp(comp.text, comp)
            return sent_comp

        def get_obj_conj_components(obj, sentence_comp: Sentence):
            for conj in obj.conjuncts:
                sent_obj = Sentence()
                sent_obj.obj = get_compound_component(conj)
                sent_obj.verb = sentence_comp.verb
                sent_obj.subj = sentence_comp.subj
                found_sent_objects.append(sent_obj)

        def get_subj_conj_components(conjunct, subject, found_items):
            items = [sent_item for sent_item in found_items if sent_item.subj.token == subject]
            for item in items:
                sent = Sentence()
                sent.subj = get_compound_component(conjunct)
                sent.obj = item.obj
                sent.verb = item.verb
                found_items.append(sent)

        def add_verb_conjucts(verb_conjucts, found_items):
            for verb_conj in verb_conjucts:
                items = [sent_item for sent_item in found_items if verb_conj in sent_item.verb.token.conjuncts]
                for item in items:
                    sent = Sentence()
                    sent.verb = SentenceComp(verb_conj.text, verb_conj)
                    sent.obj = item.obj
                    sent.subj = item.subj
                    found_items.append(sent)

        ner_parser = SpacyNERParser()
        subjects = [token for token in sent if token.dep_ in self.subject_tags and (token.ent_type_ in ner_parser.personLabels or token.ent_type_ in ner_parser.locationLabels)]
        objects = [token for token in sent if token.dep_ in self.object_tags and (token.ent_type_ in ner_parser.personLabels or token.ent_type_ in ner_parser.locationLabels)]
        found_sent_objects = []
        if len(subjects) == 0 or len(objects) == 0:
            return found_sent_objects

        verb_conj = []
        direct_objs = [obj for obj in objects if obj.dep_ == 'dobj']  # direct objects
        for obj in direct_objs:
            verb = obj.head
            verb_conj += verb.conjuncts
            subj_of_verb = [subj for subj in subjects if subj.head == verb]
            if len(subj_of_verb) > 0:
                sent_obj = Sentence()
                sent_obj.obj = get_compound_component(obj)
                sent_obj.verb = SentenceComp(verb.text, verb)
                sent_obj.subj = get_compound_component(subj_of_verb[0])
                found_sent_objects.append(sent_obj)
                get_obj_conj_components(obj, sent_obj)

        prep_objs = [obj for obj in objects if obj.dep_ == 'pobj']  # preposition objects

        for obj in prep_objs:
            prep = obj.head
            verb_comp = [prep]
            token = prep

            while token.dep_ != 'ROOT':
                if token.head not in token.conjuncts:
                    if token.head.pos_ == 'VERB':
                        verb_comp.append(token.head)
                else:
                    verb_conj += token.conjuncts
                    break
                token = token.head
            prep_verb = next(v for v in verb_comp if v.pos_ == 'VERB')
            prep_verb_text = " ".join([v.text for v in verb_comp[::-1]])
            subj_of_verb = [subj for subj in subjects if subj.head == verb_comp[-1] or subj.head in prep_verb.conjuncts]

            if len(subj_of_verb) > 0:
                sent_obj = Sentence()
                sent_obj.obj = get_compound_component(obj)
                sent_obj.verb = SentenceComp(prep_verb_text, prep_verb)
                sent_obj.subj = get_compound_component(subj_of_verb[0])
                found_sent_objects.append(sent_obj)
                get_obj_conj_components(obj, sent_obj)

        for subj in subjects:
            for conj in subj.conjuncts:
                get_subj_conj_components(conj, subj, found_sent_objects)

        add_verb_conjucts(verb_conj, found_sent_objects)

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
