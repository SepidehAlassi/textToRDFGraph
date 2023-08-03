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
        self.object = obj
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
                    sent_obj.object = SentenceComp(obj.text, obj)

            found_sent_objects.append(sent_obj)
            conjs = [token for token in sent if token.dep_ == 'conj']
            for conj in conjs:
                new_obj = Sentence(sent_obj.subj, sent_obj.verb, sent_obj.object)
                compound = [token for token in sent if token.dep_ in self.compound_tags and token.head == conj]
                comp = ''
                if len(compound):
                    comp = compound[0].text + ' '

                if conj.head.dep_ in self.subject_tags:
                    new_obj.subj = SentenceComp(comp + conj.text, conj)
                else:  # objects
                    new_obj.object = SentenceComp(comp + conj.text, conj)
                found_sent_objects.append(new_obj)

        return found_sent_objects

    def write_to_excel(self, tags_dict, project_name):
        pos_info = pd.DataFrame(data={'Sentence Num': [], 'Subject': [], 'Verb': [], 'Object': []})
        for sent_num, sent_info in tags_dict.items():
            for info_item in sent_info:
                pos_info = pd.concat([pos_info, pd.DataFrame([{'Sentence Num': sent_num,
                                                               'Subject': info_item.subj.text,
                                                               'Verb': info_item.verb.text,
                                                               'Object': info_item.object.text
                                                               }])], ignore_index=True)
        excel_file = project_name + '_pos_info.xlsx'
        file_path = os.path.join(project_name, excel_file)
        with pd.ExcelWriter(file_path) as writer:
            pos_info.to_excel(writer, sheet_name='POS info')
        return pos_info

    def get_pos_tags(self):
        sentences = list(self.doc.sents)
        sent_components = {}
        for idx, sent in enumerate(sentences):
            sent_components[idx] = self.break_sentence(sent)
        return sent_components

    def visualize_pos(self, project_name):
        dep_svg = displacy.render(self.doc, style="dep")
        filepath = os.path.join(project_name, project_name + "_dep_vis.svg")
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(dep_svg)


def detect_entities(entity_rels, entities, lang):
    def get_entity(component):
        if component.token.pos_ == 'PROPN':
            ent_type = component.token.ent_type_
            if ent_type == 'PERSON' or ent_type == 'PER':
                for _, pers_items in entities['Persons'].items():
                    found_pers = [pers_item for pers_item in pers_items if
                                 pers_item.text == component.text and pers_item.language == lang]
                    if len(found_pers) > 0:
                        pers_stack.append(found_pers[0])
                        component.entity = found_pers[0]
                        break
            else:
                for _, loc_items in entities['Locations'].items():
                    found_loc = [loc_item for loc_item in loc_items if loc_item.text == component.text and loc_item.language == lang]
                    if len(found_loc)>0:
                        loc_stack.append(found_loc[0])
                        component.entity=found_loc[0]
                        break

    pers_stack = []
    loc_stack = []
    for sent_num, sent_rels in entity_rels.items():
        for sentence_instance in sent_rels:
            get_entity(sentence_instance.subj)
            get_entity(sentence_instance.object)
    return entity_rels, pers_stack, loc_stack


def parse_dependencies(text, project_name, lang, entities):
    pos_parser = SpacyPosParser(text, lang)
    pos_parser.visualize_pos(project_name=project_name)
    sent_components = pos_parser.get_pos_tags()
    pos_parser.write_to_excel(sent_components, project_name)
    sent_components, pers_stack, loc_stack = detect_entities(sent_components, entities, lang)
    return sent_components, pers_stack, loc_stack


if __name__ == '__main__':
    test_sent_en = 'Jacob Bernoulli however only lived in Basel. He traveled though to Geneva, Lyon, Bordeaux, Amsterdam, and London.'
    with open(os.path.join(os.getcwd(), 'dh2023', 'dh2023' + '_entities.json')) as input_file:
        entities = json.load(input_file)
    parse_dependencies(test_sent_en, 'testing', 'en', entities)
