import os
import json
from pyshacl import validate
from pipes.util.json_handler import entities_toJson
from pipes.ResourceCreator import create_resources
from pipes.NamedEntityResognizer import parse_NE
from pipes.WikiInformationRetriever import retrieve_wiki_info
from pipes.PreProcessor import preprocess_input


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
    text_path = os.path.join(working_dir, 'inputs', 'test_data', 'jacob_bernoulli', 'texts', 'jb_basel_genf_en.txt')
    # onto_path = os.path.join(working_dir, 'inputs', 'example_onto.ttl')
    # shacl_path = os.path.join(working_dir, 'inputs', 'example_shacl.ttl')
    project_name = 'jacob_bernoulli'
    inputs = preprocess_input(text_path=text_path,
                              project_name=project_name)

    if not os.path.exists(project_name):
        os.mkdir(project_name)
    entities_dict = {'Locations': {}, 'Persons': {}}
    stage1(parser='flair',
           existing_entities=entities_dict,
           inputs=inputs)
    print('Stage1 done')
