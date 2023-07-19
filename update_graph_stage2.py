
import pandas as pd
import os
import json
from Entitiy import from_json
from create_resources_pipe import update_graph


def add_entity_relations(excel_file, entities_dict, relations, document_label, project_name):
    pos_info = pd.read_excel(excel_file, sheet_name='POS info')  # returns a DataFrame
    persons = [pers_occur[0] for pers_occur in entities_dict["Persons"].values()]
    locations = [loc_occur[0] for loc_occur in entities_dict["Locations"].values()]
    links_to_add = []
    for index, row in pos_info.iterrows():

        subj = row['Subject']
        found_person = [pers for pers in persons if pers.text == subj]
        if len(found_person) == 0:
            continue
        else:
            subject_iri = found_person[0].iri

        predicate = relations[row['Verb']]['prop']
        obj = row['Object']
        found_location = [loc for loc in locations if loc.text == obj]
        if len(found_location) == 0:
            continue
        else:
            object_iri = found_location[0].iri
        links_to_add.append({'subj_iri': subject_iri, 'prop_iri': predicate, 'obj_iri': object_iri})
    update_graph(links_to_add, document_label, project_name)


if __name__ == '__main__':
    file_path = os.path.join('output', 'flair_named_entities.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    entities = from_json(data)
    add_entity_relations('en_swiss', entities)
