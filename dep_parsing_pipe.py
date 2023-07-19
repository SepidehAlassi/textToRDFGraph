import pandas as pd
from spacy import displacy
from spacyParser import SpacyParser
import os


class Sentence:
    def __init__(self, subj='', verb='', object=''):
        self.subj = subj
        self.object = object
        self.verb = verb


class SpacyPosParser:
    def __init__(self, text, lang):
        self.doc = SpacyParser().spacy_parse(text, lang)

    def get_deps(self, tokens, sentence_num, tags_dict):
        compound_tags = ['compound', 'pnc']
        subject_tags = ['nsubj', 'nsubjpass', 'sb']
        object_tags = ['pobj', 'dobj', 'iobj', 'nk']

        subjects = [token for token in tokens if token.dep_ in subject_tags]
        objects = [token for token in tokens if token.dep_ in object_tags]
        found_sent_objects = []

        for subject in subjects:
            sent_obj = Sentence()
            compound = [token for token in tokens if token.dep_ in compound_tags and token.head == subject]

            if len(compound):
                sent_obj.subj = compound[0].text + ' ' + subject.text
            elif subject.pos_ == 'PRON' and sentence_num - 1 in tags_dict.keys():
                morph_info = subject.morph.to_dict()
                prev_sentence = tags_dict[sentence_num - 1][0]
                sent_obj.subj = prev_sentence.subj
            else:
                sent_obj.subj = subject.text

            if subject.head.dep_ == 'ROOT':
                if subject.head.pos_ == 'VERB':
                    verb = subject.head
                else:
                    if subject.head.pos_ == 'AUX':
                        main_verb = [token for token in tokens if token.head == subject.head and token.pos_ == 'VERB']
                        if len(main_verb):
                            verb = main_verb[0]
                        else:
                            verb = subject.head
                sent_obj.verb = verb.text
                prep_found = [token for token in tokens if token.pos_ == 'ADP' and token.head == verb]
                if len(prep_found) > 0:
                    prep = prep_found[0]
                    sent_obj.verb += ' ' + prep.text

                for obj in objects:
                    sent_obj.object = obj.text

            found_sent_objects.append(sent_obj)
            conjs = [token for token in tokens if token.dep_ == 'conj']
            for conj in conjs:
                new_obj = Sentence(sent_obj.subj, sent_obj.verb, sent_obj.object)
                compound = [token for token in tokens if token.dep_ in compound_tags and token.head == conj]
                comp = ''
                if len(compound):
                    comp = compound[0].text + ' '

                if conj.head.dep_ in subject_tags:
                    new_obj.subj = comp + conj.text
                else:  # objects
                    new_obj.object = comp + conj.text
                found_sent_objects.append(new_obj)

        return found_sent_objects

    def write_to_excel(self, tags_dict, project_name):
        pos_info = pd.DataFrame(data={'Sentence Num': [], 'Subject': [], 'Verb': [], 'Object': []})
        for sent_num, sent_info in tags_dict.items():
            for info_item in sent_info:
                pos_info = pd.concat([pos_info, pd.DataFrame([{'Sentence Num': sent_num,
                                            'Subject': info_item.subj,
                                            'Verb': info_item.verb,
                                            'Object': info_item.object
                                            }])], ignore_index=True)
        excel_file = project_name + '_pos_info.xlsx'
        file_path = os.path.join(project_name, excel_file)
        with pd.ExcelWriter(file_path) as writer:
            pos_info.to_excel(writer, sheet_name='POS info')
        return file_path

    def get_pos_tags(self, project_name):
        sentences = list(self.doc.sents)
        tags_dict = {}
        for idx, sent in enumerate(sentences):
            tags_dict[idx] = self.get_deps([token for token in sent], idx, tags_dict)

        excel_file_path = self.write_to_excel(tags_dict, project_name)
        self.visualize_pos(project_name=project_name)
        return excel_file_path

    def visualize_pos(self, project_name):
        dep_svg = displacy.render(self.doc, style="dep")
        filepath = os.path.join(project_name, project_name + "_dep_vis.svg")
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(dep_svg)


def parse_dependencies(text, project_name, lang):
    pos_parser = SpacyPosParser(text, lang)
    excel_output_file = pos_parser.get_pos_tags(project_name)
    return excel_output_file


def pos_test(text, lang, filename):
    pos_parser = SpacyPosParser(text, lang)
    pos_parser.get_pos_tags(filename)
    print("pos_tagged")


if __name__ == '__main__':
    test_sent_en = 'Jacob Bernoulli however only lived in Basel. He traveled though to Geneva, Lyon, Bordeaux, Amsterdam, and London.'
    pos_test(test_sent_en, 'en', 'jacob_bio')
