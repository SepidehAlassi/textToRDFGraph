from stage1 import stage1
from stage2 import stage2
from pipes.PreProcessor import preprocess_input
import os
import json
import time


def pipeline(text_path, ontology_path='', shacl_path='', project_name='test'):
    parser_type = input('NER with spaCy or flair?').lower()
    entities_dict = {'Locations': {}, 'Persons': {}}
    inputs = preprocess_input(text_path=text_path,
                              onto_path=ontology_path,
                              shacl_path=shacl_path,
                              project_name=project_name)
    if inputs.lang == 'fa':
        parser_type = 'flair'

    print('Starting pipeline for language: ' + inputs.lang)
    if not os.path.exists(project_name):
        os.mkdir(project_name)

    stage1(parser=parser_type,
           existing_entities=entities_dict,
           inputs=inputs)
    print('End of stage 1!')
    if inputs.lang == 'en':
        stage2(inputs=inputs,
               entities_json=os.path.join(inputs.project_name, inputs.project_name+'_entities.json'))
    print('End of stage 2!')


def pipeline_multiple(dir_path, ontology_path, shacl_path, project_name):
    parser_type = input('NER with spaCy or flair?').lower()
    entities_dict = {'Locations': {}, 'Persons': {}}
    english_texts = []
    if not os.path.exists(project_name):
        os.mkdir(project_name)
    text_paths = [os.path.join(dir_path, file) for file in os.listdir(dir_path) if file.endswith('.txt')]
    for text_path in text_paths:
        input_params = preprocess_input(text_path, ontology_path, shacl_path, project_name)
        if input_params.lang == 'fa':
            parser_type = 'flair'

        print('Starting pipeline for language: ' + input_params.lang)

        stage1(parser=parser_type,
               existing_entities=entities_dict,
               inputs=input_params)

        json_path = os.path.join(input_params.project_name, input_params.project_name + '_entities.json')
        with open(json_path) as input_file:
            entities_dict = json.load(input_file)
        if input_params.lang == 'en':
            english_texts.append(input_params)
        if text_path != text_paths[-1]:
            time.sleep(60)
    print('End of stage 1!')
    for en_text in english_texts:
        stage2(inputs=en_text,
               entities_json=os.path.join(en_text.project_name, en_text.project_name + '_entities.json'))
    print('End of stage 2!')


if __name__ == '__main__':
    working_dir = os.getcwd()
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'de_swiss.txt')
    ontology_path = os.path.join(working_dir, 'inputs', 'nlpGraph_onto.ttl')
    project_name = 'dh2023'

    pipeline(text_path=text_path,
             project_name='testing')
    # data_folder = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023')
    #
    # pipeline_multiple(dir_path=data_folder,
    #                   ontology_path=ontology_path,
    #                   project_name=project_name)
