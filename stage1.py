import os
import json

from pipes.ResourceCreator import create_resources
from pipes.NamedEntityResognizer import parse_NE
from pipes.WikiInformationRetriever import retrieve_wiki_info
from pipes.PreProcessor import preprocess_input
from pyshacl import validate


def entities_toJson(entities_dict, wiki_props):  # get a class instance
    def convert_ent_to_dict(instance, wiki_props):
        entity_as_dict = instance.__dict__  # convert it to dictionary and return
        entity_dict = {}
        for key, value in entity_as_dict.items():
            if key in wiki_props.keys():
                qname = wiki_props[key]['prop_QName']
                entity_dict[qname] = value
            else:
                entity_dict[key] = value
        return entity_dict

    entities_dict_qname = {}
    for ent_type, ent_dict in entities_dict.items():
        entities_dict_qname[ent_type] = {}
        for identifier, entity_list in ent_dict.items():
            entities_dict_qname[ent_type][identifier] = []
            for ent in entity_list:
                entities_dict_qname[ent_type][identifier].append(convert_ent_to_dict(ent, wiki_props))
    return entities_dict_qname


def stage1(parser, existing_entities, inputs):
    found_locations, found_persons = parse_NE(parser, inputs)

    entities_dict, wiki_props = retrieve_wiki_info(found_locations, found_persons, existing_entities, inputs)
    jsonified_entities = entities_toJson(entities_dict, wiki_props)

    json_path = os.path.join(inputs.project_name, inputs.project_name + '_entities.json')
    with open(json_path, "w") as output_json:
        json.dump(jsonified_entities, output_json, indent=4, ensure_ascii=True)
    create_resources(entities_json=json_path,
                     inputs=inputs)

    data_graph_file = os.path.join(inputs.project_name, inputs.project_name + '_graph.ttl')
    conforms, results_graph, results_text = validate(data_graph=data_graph_file,
                                                     data_graph_format='turtle',
                                                     shacl_graph=inputs.shacl_graph.serialize(format='turtle'),
                                                     ont_graph=inputs.onto_graph.serialize(format='turtle'),
                                                     inference='rdfs',
                                                     abort_on_error=False,
                                                     meta_shacl=False,
                                                     debug=False)
    if not conforms:
        print(results_graph)


if __name__ == '__main__':
    working_dir = os.getcwd()
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'dh2023', 'en_swiss.txt')
    onto_path = os.path.join(working_dir, 'inputs', 'example_onto.ttl')
    shacl_path = os.path.join(working_dir, 'inputs', 'example_shacl.ttl')
    project_name = 'dh2023'
    inputs = preprocess_input(text_path=text_path,
                              onto_path=onto_path,
                              shacl_path=shacl_path,
                              project_name=project_name)

    if not os.path.exists(project_name):
        os.mkdir(project_name)
    entities_dict = {'Locations': {}, 'Persons': {}}
    stage1(parser='spacy',
           existing_entities=entities_dict,
           inputs=inputs)
    print('Stage1 done')
