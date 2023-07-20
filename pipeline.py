from stage1 import stage1
from stage2 import stage2
from pipes.preprocess_pipe import preprocess_input
import os


def pipeline(text_path, ontology_path, project_name):
    parser_type = input('NER with spaCy or flair?').lower()
    entities_dict = {'Locations': {}, 'Persons': {}}
    inputs = preprocess_input(text_path, ontology_path, project_name)
    if inputs.lang == 'fa':
        parser_type = 'flair'

    print('Starting pipeline for language: ' + inputs.lang)
    if not os.path.exists(project_name):
        os.mkdir(project_name)

    stage1(parser=parser_type,
           existing_entities=entities_dict,
           inputs=inputs)

    if inputs.lang == 'en':
        stage2(inputs=inputs,
               entities_json=os.path.join(inputs.project_name, inputs.project_name+'_entities.json'))


if __name__ == '__main__':
    working_dir = os.getcwd()
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'en_swiss.txt')
    ontology_path = os.path.join(working_dir, 'inputs', 'ner_onto.ttl')
    project_name = 'dh2023'

    pipeline(text_path=text_path,
             ontology_path=ontology_path,
             project_name='testing')
