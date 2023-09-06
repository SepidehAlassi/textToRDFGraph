from langdetect import detect

import os
from rdflib import Graph


def parse_ontology(file):
    graph = Graph()
    graph.parse(file, format='ttl')
    return graph


class Input:
    def __init__(self, text_path, onto_path, project_name):
        self.text, self.doc_name = read_text(text_path)
        self.lang = detect_lang(self.text)
        self.onto_graph = parse_ontology(onto_path)
        self.project_name = project_name


def detect_lang(text):
    lang = detect(text)
    supported_langs = ['en', 'de', 'fa']
    if lang not in supported_langs:
        raise ValueError('The Pipeline only supports ' +
                         ','.join(supported_langs) + ', not ' + lang)
    return lang


def read_text(text_path):
    with open(text_path) as file:
        text = file.read()
    document_name, _ = os.path.basename(text_path).split('.')
    return text, document_name


def preprocess_input(text_path, onto_path, project_name):
    inputs = Input(text_path, onto_path, project_name)
    return inputs


if __name__ == '__main__':
    working_dir = os.getcwd()
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'en_swiss.txt')
    ontology_path = os.path.join(working_dir, 'inputs', 'ner_onto.ttl')
    project_name = 'dh2023'
    inputs = preprocess_input(text_path, ontology_path, project_name)

