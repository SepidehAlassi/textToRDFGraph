import os
import json

from pipes.create_resources_pipe import create_resources_pipe
from Entitiy import Entity
from pipes.NER_pipe import ner_pipe
from pipes.wiki_IR_pipe import wiki_IR_pipe


def stage1(parser, existing_entities, text, doc_name, project_name, lang="en"):

    found_locations, found_persons = ner_pipe(parser, text, lang)

    entities_dict = wiki_IR_pipe(found_locations, found_persons, existing_entities, doc_name)

    json_file = os.path.join(project_name, project_name+'_entities.json')
    with open(json_file, "w") as output:
        output.write(json.dumps(entities_dict, default=Entity.toJson, indent=4, ensure_ascii=True))
    create_resources_pipe(entities_json=json_file,
                          project_name=project_name,
                          text=text,
                          doc_name=doc_name)


if __name__ == '__main__':
    folder_path = os.path.join('inputs/test_data', 'dh2023')
    document_name = 'fa_swiss'
    file_path = os.path.join(folder_path, document_name + '.txt')
    with open(file_path, 'r') as file:
        text = file.read()
    lang = 'fa'
    parser_type = input('NER with spaCy or flair?').lower()
    file_path = os.path.join('test', 'test_entities.json')
    with open(file_path) as json_file:
        existing_entities = json.load(json_file)
    stage1(parser=parser_type,
           existing_entities=existing_entities,
           text=text,
           doc_name=document_name,
           project_name='test',
           lang=lang)
    # dump entities to JSON
    with open(file_path, "w") as output:
        output.write(json.dumps(existing_entities, default=Entity.toJson, indent=4, ensure_ascii=True))
    # serialize results as turtle
    create_resource_pipe.create_entity_resources(entities_path=file_path)
    create_resource_pipe.serialize_documents(data_folder=folder_path, entities_json=file_path)
