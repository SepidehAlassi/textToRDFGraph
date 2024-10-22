from pipeline import pipeline, pipeline_multiple
import os

if __name__ == '__main__':
    working_dir = os.getcwd()
    data_folder = os.path.join(working_dir, 'inputs', 'test_data', 'reisebuechlein')

    project_name = 'reisebuechlein'

    pipeline_multiple(dir_path=data_folder,
                      project_name=project_name)
