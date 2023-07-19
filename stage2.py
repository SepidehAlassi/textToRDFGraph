from parse_ontology import *
from dep_parsing_pipe import parse_dependencies
from update_graph_stage2 import add_entity_relations
import os
import json
from Entitiy import from_json


def read_entities(entities_json):
    with open(entities_json, 'r') as file:
        data = json.load(file)
    entities = from_json(data)
    return entities


def stage2(onto_file, text, doc_name, lang, project_name, entities_json):
    entities = read_entities(entities_json)

    # parse ontology
    relations = parse_ontology(onto_file)

    # dependency parsing pipe
    excel_file_path = parse_dependencies(text=text, project_name=project_name, lang=lang)

    # Pronoun resolution pipe
    # TODO: separate this pipe

    # update graph
    add_entity_relations(excel_file=excel_file_path,
                         entities_dict=entities,
                         relations=relations,
                         project_name=project_name,
                         document_label=doc_name)
    print('stage 2')


if __name__ == '__main__':
    folder_path = os.path.join('test_data', 'dh2023')
    document_name = 'en_swiss'
    file_path = os.path.join(folder_path, document_name + '.txt')
    with open(file_path, 'r') as file:
        text = file.read()
    stage2(onto_file=os.path.join(os.getcwd(), 'ner_onto.ttl'),
           text=text,
           doc_name=document_name,
           lang='en',
           project_name='test',
           entities_json=os.path.join('test', 'test_entities.json'))
