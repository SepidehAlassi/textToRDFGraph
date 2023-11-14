from stage1 import stage1
from stage2 import stage2
from pipes.PreProcessor import preprocess_input
from pipes.util.json_handler import entities_fromJson
import os
import time


def pipeline(data_path, ontology_path='', shacl_path='', project_name='test_project', run_stage2=False):
    if os.path.isdir(data_path):
        pipeline_multiple(dir_path=data_path,
                          ontology_path=ontology_path,
                          shacl_path=shacl_path,
                          project_name=project_name,
                          run_stage2=run_stage2)
    else:
        pipeline_single(text_path=data_path,
                        ontology_path=ontology_path,
                        shacl_path=shacl_path,
                        project_name=project_name,
                        run_stage2=run_stage2)


def pipeline_single(text_path, ontology_path='', shacl_path='', project_name='test_project', run_stage2=False):
    # parser_type = input('NER with spaCy or flair?').lower()
    entities_dict = {'Locations': {}, 'Persons': {}}

    inputs = preprocess_input(text_path=text_path,
                              onto_path=ontology_path,
                              shacl_path=shacl_path,
                              project_name=project_name)

    parser_type = 'flair'

    print('Starting pipeline for language: ' + inputs.lang)
    if not os.path.exists(project_name):
        os.mkdir(project_name)

    stage1(parser=parser_type,
           existing_entities=entities_dict,
           inputs=inputs)
    print('End of stage 1!')
    if inputs.lang != 'fa' and run_stage2:
        stage2(inputs=inputs,
               entities_json=os.path.join(inputs.project_name, inputs.project_name + '_entities.json'))
    print('End of stage 2!')


def pipeline_multiple(dir_path, ontology_path='', shacl_path='', project_name='test_project', run_stage2=False):
    parser_type = input('NER with spaCy or flair?').lower()

    entities_dict = {'Locations': {}, 'Persons': {}}

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
        entities_dict = entities_fromJson(json_path)

        if text_path != text_paths[-1]:
            time.sleep(60)
        print('End of stage 1!')
        if run_stage2 and input_params.lang != 'fa':
            stage2(inputs=input_params,
                   entities_json=json_path)
            print('End of stage 2!')


if __name__ == '__main__':
    working_dir = os.getcwd()
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'jacob_bernoulli', 'texts', 'jb_basel_genf_en.txt')
    ontology_path = os.path.join(working_dir, 'inputs', 'test_data', 'jacob_bernoulli', 'input_onto.ttl')
    shacl_path = os.path.join(working_dir, 'inputs', 'test_data', 'jacob_bernoulli', 'input_shacl.ttl')
    project_name = 'jacob_bernoulli'
    data_folder = os.path.join(working_dir, 'inputs', 'test_data', 'jacob_bernoulli')

    pipeline(data_path=text_path,
             ontology_path=ontology_path,
             shacl_path=shacl_path,
             project_name=project_name,
             run_stage2=True)
