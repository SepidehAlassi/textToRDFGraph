from pipeline import pipeline, pipeline_multiple
import os

if __name__ == '__main__':
    working_dir = os.getcwd()
    data_folder = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'texts')
    ontology_path = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'example_onto.ttl')
    shacl_path = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'example_shacl.ttl')
    project_name = 'dh2023'

    pipeline_multiple(dir_path=data_folder,
                      ontology_path=ontology_path,
                      shacl_path=shacl_path,
                      project_name=project_name)
