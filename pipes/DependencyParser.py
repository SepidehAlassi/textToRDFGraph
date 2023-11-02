from pipes.util.NLP_Parser.spacyParser import SpacyParser
from pipes.NamedEntityResognizer import SpacyNERParser
import os
import json
from constants import *

from pipes.util.json_handler import entities_fromJson


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
        self.ner_parser = SpacyNERParser()

    def get_sent_components(self):
        """
        Get the components of sentences in the text
        :return: a dictionary with sentence index and components found in that sentence describing relation.
        """

        def get_sentences(text):
            """
            This function breaks the text into sentences.
            :param text: input text
            :return: list of sentences
            """
            checkString = lambda s: any(c.isalpha() for c in s) or any(c.isdigit() for c in s)
            sents = [elem + '.' for elem in text.split('.\n') if checkString(elem)]
            return sents

        sentences = get_sentences(self.text)
        sent_components = {}
        for idx, sentence in enumerate(sentences):
            sent = SpacyParser().spacy_parse(text=sentence, lang=self.lang)
            sent_comp = self.parse_sentence(sent)
            if len(sent_comp):
                sent_components[idx] = sent_comp
        return sent_components

    def parse_sentence(self, sent):
        pass


class DependencyParserEN(DependencyParser):
    def __init__(self, text, lang):
        super().__init__(text, lang)
        self.compound_tags = ['compound', 'pnc']
        self.subject_tags = ['nsubj', 'nsubjpass']
        self.object_tags = ['pobj', 'dobj', 'iobj']

    def get_compound_component(self, sent, comp, compound_tags):
        compound = [token for token in sent if token.dep_ in compound_tags and token.head == comp]
        if len(compound):
            compound_part = compound.pop()
            if compound_part.text not in FEMALE_ADDRESS_WORDS + MALE_ADDRESS_WORDS:
                sent_comp = SentenceComp(compound_part.text + ' ' + comp.text, comp)
            else:
                sent_comp = SentenceComp(comp.text, comp)
        else:
            sent_comp = SentenceComp(comp.text, comp)
        return sent_comp

    def get_obj_conj_components(self, obj, sentence_comp: Sentence, found_objects, sent, compound_tags):
        for conj in obj.conjuncts:
            sent_obj = Sentence()
            sent_obj.obj = self.get_compound_component(sent, conj, compound_tags)
            sent_obj.verb = sentence_comp.verb
            sent_obj.subj = sentence_comp.subj
            found_objects.append(sent_obj)

    def get_subj_conj_components(self, conjunct, subject, found_items, text_sent, compound_tags):
        items = [sent_item for sent_item in found_items if sent_item.subj.token == subject]
        for item in items:
            sent = Sentence()
            sent.subj = self.get_compound_component(text_sent, conjunct, compound_tags)
            sent.obj = item.obj
            sent.verb = item.verb
            found_items.append(sent)

    def add_verb_conjucts(self, verb_conjucts, found_items):
        for verb_conj in verb_conjucts:
            items = [sent_item for sent_item in found_items if verb_conj in sent_item.verb.token.conjuncts]
            for item in items:
                sent = Sentence()
                sent.verb = SentenceComp(verb_conj.text, verb_conj)
                sent.obj = item.obj
                sent.subj = item.subj
                found_items.append(sent)

    def parse_sentence(self, sent):
        """
        Parse subject, verb, and object out of the sentence
        :param sent: input sentence
        :return: sentence components
        """
        subjects = [token for token in sent if token.dep_ in self.subject_tags and (
                token.ent_type_ in self.ner_parser.personLabels or token.ent_type_ in self.ner_parser.locationLabels)]
        objects = [sent_comp for sent_comp in sent if sent_comp.dep_ in self.object_tags and (
                sent_comp.ent_type_ in self.ner_parser.personLabels or sent_comp.ent_type_ in self.ner_parser.locationLabels)]

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
                sent_obj.obj = self.get_compound_component(sent, obj, self.compound_tags)
                sent_obj.verb = SentenceComp(verb.text, verb)
                sent_obj.subj = self.get_compound_component(sent, subj_of_verb[0], self.compound_tags)
                found_sent_objects.append(sent_obj)
                self.get_obj_conj_components(obj, sent_obj, found_sent_objects, sent, self.compound_tags)

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
            else:
                if token.pos_ == 'AUX':
                    verb_comp.append(token)
            prep_verb = next(v for v in verb_comp if v.pos_ == 'VERB' or v.pos_ == 'AUX')
            prep_verb_text = " ".join([v.text for v in verb_comp[::-1]])
            subj_of_verb = [subj for subj in subjects if subj.head == verb_comp[-1] or subj.head in prep_verb.conjuncts]

            if len(subj_of_verb) > 0:
                sent_obj = Sentence()
                sent_obj.obj = self.get_compound_component(sent, obj, self.compound_tags)
                sent_obj.verb = SentenceComp(prep_verb_text, prep_verb)
                sent_obj.subj = self.get_compound_component(sent, subj_of_verb[0], self.compound_tags)
                found_sent_objects.append(sent_obj)
                self.get_obj_conj_components(obj, sent_obj, found_sent_objects, sent, self.compound_tags)

        for subj in subjects:
            for conj in subj.conjuncts:
                self.get_subj_conj_components(conj, subj, found_sent_objects, sent, self.compound_tags)

        self.add_verb_conjucts(verb_conj, found_sent_objects)

        return found_sent_objects


class DependencyParserDE(DependencyParser):
    def __init__(self, text, lang):
        super().__init__(text, lang)
        self.subject_tags = ['sb']
        self.object_tags = ['oa']
        self.compound_tags = ['pnc']

    def get_sent_subjects(self, sent):
        found_subjects = []
        nominatives = [token for token in sent if 'Case' in token.morph.to_dict().keys() and token.morph.to_dict()['Case'] == 'Nom']
        pnc_tokens = [token for token in nominatives if token.dep_ in self.compound_tags]
        for pnc in pnc_tokens:
            head = pnc.head
            found_subjects.append(SentenceComp(pnc.text + ' ' + head.text, head))
            nominatives.remove(pnc)
            if head in nominatives:
                nominatives.remove(head)

        if len(nominatives) > 1:
            nominatives = sorted(nominatives, key=lambda x: x.idx)
            for index, token in enumerate(nominatives):
                if token.dep_ == 'ROOT':
                    found_subjects.append(SentenceComp(token.text + ' ' + nominatives[index+1].text, nominatives[index+1]))
                    nominatives.remove(token)
                    del nominatives[index+1]

            for nom in nominatives:
                found_subjects.append(SentenceComp(nom.text, nom))
        elif len(nominatives) == 1:
            found_subjects.append(SentenceComp(nominatives[0].text, nominatives[0]))
        else:
            pass
        return found_subjects

    def get_sent_verb(self, sent):
        verbs = [token for token in sent if token.pos_ == 'VERB']
        found_verbs=[]
        for verb in verbs:
            head = verb.head
            if head.pos_ == 'AUX':
                text = head.text + ' ' + verb.text
            else:
                text = verb.text
            adp_props = [token for token in sent if token.head == verb and token.pos_ == 'ADP']
            for adp_prop in adp_props:
                text = text + ' ' + adp_prop.text
            found_verbs.append(SentenceComp(text, verb))
        return found_verbs

    def get_sent_objects(self, sent):
        def get_conjuncts(object_list):
            for acc in object_list:
                accusative_conj = [token for token in sent if token.dep_ == 'cj' and
                                   token.right_edge == acc.right_edge and
                                   (
                                               token.ent_type_ in self.ner_parser.personLabels or token.ent_type_ in self.ner_parser.locationLabels) and
                                   token not in object_list]
                object_list.extend(accusative_conj)

        found_objects = []
        accusatives = [token for token in sent if
                       'Case' in token.morph.to_dict().keys() and token.morph.to_dict()['Case'] == 'Acc' and
                       (token.ent_type_ in self.ner_parser.personLabels or token.ent_type_ in self.ner_parser.locationLabels)]
        get_conjuncts(accusatives)

        compound_accusatives = [token for token in accusatives if token.left_edge.dep_ in self.compound_tags]
        for acc in compound_accusatives:
            left_edge = acc.left_edge
            found_objects.append(SentenceComp(left_edge.text + ' ' + acc.text, acc))
            accusatives.remove(acc)
            if left_edge in accusatives:
                accusatives.remove(left_edge)
        for obj in accusatives:
            found_objects.append(SentenceComp(obj.text, obj))

        if len(found_objects) == 0:  # not found accusatives check Datives
            adp_props = [token for token in sent if token.head.pos_ == 'VERB' and token.pos_ == 'ADP']
            for adp_prop in adp_props:
                dative_objs = [token for token in sent if token.head == adp_prop and
                             (token.ent_type_ in self.ner_parser.personLabels or token.ent_type_ in self.ner_parser.locationLabels)]
                get_conjuncts(dative_objs)
                compound_datives = [token for token in dative_objs if token.left_edge.dep_ in self.compound_tags]
                for obj in compound_datives:
                    left_edge = obj.left_edge
                    found_objects.append(SentenceComp(left_edge.text + ' ' + obj.text, obj))
                    dative_objs.remove(obj)
                    if left_edge in dative_objs:
                        dative_objs.remove(left_edge)
                for prop_obj in dative_objs:
                    found_objects.append(SentenceComp(prop_obj.text, prop_obj))

        return found_objects

    def parse_sentence(self, sent):
        """
        Parse subject, verb, and object out of the sentence
        :param sent: input sentence
        :return: sentence components
        """

        found_sent_objects = []

        subjects = self.get_sent_subjects(sent)  # get nominatives from the sentence
        verbs = self.get_sent_verb(sent)
        objects = self.get_sent_objects(sent)
        if len(subjects) == 0 or len(objects) == 0:
            return found_sent_objects
        # All permutations of sentence components
        for subj in subjects:
            for verb in verbs:
                for obj in objects:
                    sentence = Sentence(subj=subj, verb=verb, obj=obj)
                    found_sent_objects.append(sentence)

        return found_sent_objects


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
                    found_loc = [loc_item for loc_item in loc_items if
                                 loc_item.text == component.text and loc_item.language == lang]
                    if len(found_loc) > 0:
                        component.entity = found_loc[0]
                        break

    # collect person entities for pronoun resolution later
    pers_stack = {}
    for sent_num, sent_rels in sentence_components.items():
        persons = []
        for sentence_instance in sent_rels:
            get_ne_record_of_token(sentence_instance.subj, persons)
            get_ne_record_of_token(sentence_instance.obj, persons)
        pers_stack[sent_num] = persons
    return sentence_components, pers_stack


def parse_dependencies(text, lang, entities):
    """
    Parse dependencies of tokens in the text.
    :param text: input text
    :param lang: language of the text
    :param entities: extracted named entities
    :return: sentence components and persons stack extracted form the text
    """
    if lang == 'en':
        pos_parser = DependencyParserEN(text, lang)
    else:
        pos_parser = DependencyParserDE(text, lang)

    sent_components = pos_parser.get_sent_components()
    sent_components, pers_stack = get_entity_of_sentence_component(sent_components, entities, lang)
    return sent_components, pers_stack


if __name__ == '__main__':
    test_sent_en = 'Jacob Bernoulli however only lived in Basel. He traveled though to Geneva, Lyon, Bordeaux, Amsterdam, and London.'
    path = os.path.join(os.getcwd(), '..', 'jacob_bernoulli', 'jacob_bernoulli' + '_entities.json')
    entities = entities_fromJson(path)

    found_comps, _ = parse_dependencies(test_sent_en, 'en', entities)
    print(len(found_comps))
