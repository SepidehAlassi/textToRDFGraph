from langdetect import detect
import os
from rdflib import Graph


def parse_ontology(file):
    """
    Parse the input ontology to a graph
    :param file: ontology file
    :return: graph representing the ontology
    """
    graph = Graph()
    default_onto = os.path.join(os.path.dirname(__file__), '..', 'nlpGraph_onto.ttl')
    graph.parse(default_onto, format='ttl')
    if file != '':
        graph.parse(file, format='ttl')
    return graph


def parse_shacl(file):
    """
    Parse the input shacl to validate the generated graph
    :param file: shacl file with custom shape
    :return: shapes graph
    """
    graph = Graph()
    default_shacl = os.path.join(os.path.dirname(__file__), '..', 'nlpGraph_shacl.ttl')
    graph.parse(default_shacl, format='ttl')
    if file != '':
        graph.parse(file, format='ttl')
    return graph


class Input:
    def __init__(self, text, onto_path='', shacl_path='', project_name='test_output'):
        if os.path.isfile(text):
            self.text, self.doc_name = read_text(text)
        else:
            self.text = text
            self.doc_name = 'test_output'
        self.lang = detect_lang(self.text)
        self.onto_graph = parse_ontology(onto_path)
        self.shacl_graph = parse_shacl(shacl_path)
        self.project_name = project_name


def detect_lang(text):
    """
    Detect the language of the input text
    :param text: input text of the pipeline
    :return: language of the text
    """
    lang = detect(text)
    supported_langs = ['en', 'de', 'fa']
    if lang not in supported_langs:

        print('The Pipeline only supports ' +
                         ','.join(supported_langs) + 'the following text has language that is not supported, German language model is considered instead!\n', text)
        lang = 'de'
    return lang


def read_text(text_path):
    """
    Read text content
    :param text_path: Path to the text file
    :return: text string and name of the text document
    """
    with open(text_path) as file:
        text = file.read()
    document_name, _ = os.path.basename(text_path).split('.')
    return text, document_name


def preprocess_input(text_path, onto_path='', shacl_path='', project_name='test_project'):
    """
    Preprocess the inputs of the pipeline into an object
    :param text_path: path to the input text
    :param onto_path: path to the input ontology
    :param shacl_path: path to the input shacl file
    :param project_name: name of the project
    :return: Input object containing collection of pipeline's input data
    """
    inputs = Input(text_path, onto_path, shacl_path, project_name)
    return inputs


if __name__ == '__main__':
    working_dir = os.getcwd()
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'en_swiss.txt')
    project_name = 'dh2023'
    inputs = preprocess_input(text_path=text_path, project_name=project_name)

