from stage1 import stage1
from stage2 import stage2
from parse_ontology import parse_ontology
import os


def read_text(text_path):
    with open(text_path) as file:
        text = file.read()
    document_name, _ = os.path.basename(text_path).split('.')
    return text, document_name


def pipeline(text_path, text_lang, ontology_path, project_name):
    parser_type = input('NER with spaCy or flair?').lower()
    entities_dict = {'Locations': {}, 'Persons': {}}
    if text_lang == 'fa':
        parser_type = 'flair'

    text, document_name = read_text(text_path)
    # parse_ontology(ontology_path)

    if not os.path.exists(project_name):
        os.mkdir(project_name)

    stage1(parser=parser_type,
           existing_entities=entities_dict,
           text=text,
           doc_name=document_name,
           project_name=project_name,
           lang=text_lang)

    if text_lang == 'en':
        stage2(onto_file=ontology_path,
               text=text,
               doc_name=document_name,
               lang="en",
               project_name=project_name,
               entities_json=os.path.join(project_name, project_name+'_entities.json'))


if __name__ == '__main__':
    working_dir = os.getcwd()
    pipeline(text_path=os.path.join(working_dir, 'test_data', 'dh2023', 'en_swiss.txt'),
             text_lang='en',
             ontology_path=os.path.join(working_dir, 'ner_onto.ttl'),
             project_name='test')
