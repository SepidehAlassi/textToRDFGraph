from pipes.DependencyParser import parse_dependencies
from pipes.PostProcessor import post_process_graph
from pipes.PronounResolver import resolve_pronouns
from pipes.PreProcessor import preprocess_input

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
    sentence_comps, pers_stack = parse_dependencies(text=inputs.text, project_name=inputs.project_name,
                                                    lang=inputs.lang, entities=entities)

    # Pronoun resolution pipe
    resolve_pronouns(sentence_comps, pers_stack, lang=inputs.lang)

    # Postprocessing the graph
    post_process_graph(sentence_comps, inputs=inputs)
    print('End of stage2')


if __name__ == '__main__':
    working_dir = os.getcwd()
    entities_json = os.path.join(working_dir, 'dh2023', 'dh2023_entities.json')
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'en_swiss.txt')
    onto_path = os.path.join(working_dir, 'inputs', 'example_onto.ttl')
    shacl_path = os.path.join(working_dir, 'inputs', 'example_shacl.ttl')
    project_name = 'dh2023'
    inputs = preprocess_input(text_path=text_path,
                              onto_path=onto_path,
                              shacl_path=shacl_path,
                              project_name=project_name)

    stage2(inputs=inputs,
           entities_json=entities_json)
