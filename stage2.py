from pipes.dep_parsing_pipe import parse_dependencies
from pipes.postprocess_pipe import add_entity_relations
from rdflib import Graph
import os
import json
from Entitiy import from_json


def read_entities(entities_json):
    with open(entities_json, 'r') as file:
        data = json.load(file)
    entities = from_json(data)
    return entities


def stage2(inputs, entities_json):
    entities = read_entities(entities_json)

    # dependency parsing pipe
    excel_file_path = parse_dependencies(text=inputs.text, project_name=inputs.project_name, lang=inputs.lang)

    # Pronoun resolution pipe
    # TODO: separate this pipe

    # update graph
    add_entity_relations(excel_file=excel_file_path,
                         entities_dict=entities,
                         inputs=inputs)
    print('End of stage 2!')


if __name__ == '__main__':
    folder_path = os.path.join('inputs/test_data', 'dh2023')
    document_name = 'en_swiss'
    file_path = os.path.join(folder_path, document_name + '.txt')
    with open(file_path, 'r') as file:
        text = file.read()
    stage2(onto_file=os.path.join(os.getcwd(), 'inputs/ner_onto.ttl'),
           text=text,
           doc_name=document_name,
           lang='en',
           project_name='test',
           entities_json=os.path.join('test', 'test_entities.json'))
