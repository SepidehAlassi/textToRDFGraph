import os
import json

from pipes.ResourceCreator import create_resources
from Entitiy import Entity
from pipes.NamedEntityResognizer import parse_NE
from pipes.WikiInformationRetriever import retrieve_wiki_infromation
from pipes.PreProcessor import preprocess_input


def stage1(parser, existing_entities, inputs):

    found_locations, found_persons = parse_NE(parser, inputs)

    entities_dict = retrieve_wiki_infromation(found_locations, found_persons, existing_entities, inputs.doc_name)

    json_path = os.path.join(inputs.project_name, inputs.project_name + '_entities.json')
    with open(json_path, "w") as output_json:
        output_json.write(json.dumps(entities_dict, default=Entity.toJson, indent=4, ensure_ascii=True))
    create_resources(entities_json=json_path,
                     inputs=inputs)


if __name__ == '__main__':
    working_dir = os.getcwd()
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'magellan_voyage', 'en_magellan_voyage.txt')
    ontology_path = os.path.join(working_dir, 'inputs', 'ner_onto.ttl')
    project_name = 'magellan'
    inputs = preprocess_input(text_path, ontology_path, project_name)

    if not os.path.exists(project_name):
        os.mkdir(project_name)
    entities_dict = {'Locations': {}, 'Persons': {}}
    stage1(parser='spacy',
           existing_entities=entities_dict,
           inputs=inputs)
