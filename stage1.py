import os
import json

from pipes.create_resources_pipe import create_resources_pipe
from Entitiy import Entity
from pipes.NER_pipe import ner_pipe
from pipes.wiki_IR_pipe import wiki_IR_pipe
from pipes.preprocess_pipe import preprocess_input

def stage1(parser, existing_entities, inputs):

    found_locations, found_persons = ner_pipe(parser, inputs)

    entities_dict = wiki_IR_pipe(found_locations, found_persons, existing_entities, inputs.doc_name)

    json_path = os.path.join(inputs.project_name, inputs.project_name + '_entities.json')
    with open(json_path, "w") as output_json:
        output_json.write(json.dumps(entities_dict, default=Entity.toJson, indent=4, ensure_ascii=True))
    create_resources_pipe(entities_json=json_path,
                          inputs=inputs)
    print('End of stage 1!')


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
