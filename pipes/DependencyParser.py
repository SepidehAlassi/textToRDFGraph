import pandas as pd
from spacy import displacy
from pipes.NLP_Parsers.spacyParser import SpacyParser
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


class SpacyPosParser:
    def __init__(self, text, lang):
        self.doc = SpacyParser().spacy_parse(text, lang)

        self.compound_tags = ['compound', 'pnc']
        self.subject_tags = ['nsubj', 'nsubjpass', 'sb']
        self.object_tags = ['pobj', 'dobj', 'iobj', 'nk']

    def break_sentence(self, sent):
        subjects = [token for token in sent if token.dep_ in self.subject_tags]
        objects = [token for token in sent if token.dep_ in self.object_tags]
        found_sent_objects = []

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
                found_sent_objects.append(new_obj)

        return found_sent_objects

    def get_pos_tags(self):
        sentences = list(self.doc.sents)
        sent_components = {}
        for idx, sent in enumerate(sentences):
            sent_components[idx] = self.break_sentence(sent)
        return sent_components


def visualize_pos(doc, project_name):
    dep_svg = displacy.render(doc, style="dep")
    filepath = os.path.join(project_name, project_name + "_dep_vis.svg")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(dep_svg)


def parse_entities(entity_rels, entities, lang):
    pers_labels = ['PERSON', 'PER']

    def get_entity(component, persons):
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

    pers_stack = {}
    for sent_num, sent_rels in entity_rels.items():
        persons = []
        for sentence_instance in sent_rels:
            get_entity(sentence_instance.subj, persons)
            get_entity(sentence_instance.obj, persons)
        pers_stack[sent_num] = persons
    return entity_rels, pers_stack


def parse_dependencies(text, project_name, lang, entities):
    pos_parser = SpacyPosParser(text, lang)
    visualize_pos(pos_parser.doc, project_name=project_name)
    sent_components = pos_parser.get_pos_tags()
    sent_components, pers_stack = parse_entities(sent_components, entities, lang)
    return sent_components, pers_stack


if __name__ == '__main__':
    test_sent_en = 'Jacob Bernoulli however only lived in Basel. He traveled though to Geneva, Lyon, Bordeaux, Amsterdam, and London.'
    with open(os.path.join(os.getcwd(), 'dh2023', 'dh2023' + '_entities.json')) as input_file:
        entities = json.load(input_file)
    parse_dependencies(test_sent_en, 'testing', 'en', entities)
