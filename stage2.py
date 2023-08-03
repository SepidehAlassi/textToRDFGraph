from pipes.dep_parsing_pipe import parse_dependencies
from pipes.postprocess_pipe import add_entity_relations
from pipes.pron_resolution_pipe import resolve_pronoun

import os
import json
from Entitiy import from_json
from pipes.preprocess_pipe import Input


def read_entities(entities_json):
    with open(entities_json, 'r') as file:
        data = json.load(file)
    entities = from_json(data)
    return entities


def stage2(inputs, entities_json):
    entities = read_entities(entities_json)

    # dependency parsing pipe
    sentence_comps, pers_stack, loc_stack = dependencies(text=inputs.text, project_name=inputs.project_name, lang=inputs.lang, entities=entities)

    # Pronoun resolution pipe
    resolve_pronoun(sentence_comps, pers_stack, loc_stack)

    # update graph
    add_entity_relations(sentence_comps,
                         inputs=inputs)
    print('End of stage2')


if __name__ == '__main__':
    entities_json = os.path.join(os.getcwd(), 'dh2023', 'dh2023_entities.json')
    test_input = Input(text_path=os.path.join(os.getcwd(), 'inputs', 'test_data', 'dh2023', 'en_swiss.txt'),
                       onto_path=os.path.join(os.getcwd(), 'inputs', 'ner_onto.ttl'),
                       project_name='dh2023')
    stage2(inputs=test_input,
           entities_json=entities_json)
