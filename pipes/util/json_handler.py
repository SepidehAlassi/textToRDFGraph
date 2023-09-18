from Entitiy import *
import json


def from_json(dct):
    def convert_to_ent(ent, obj):
        for key, val in ent.items():
            if ':' in key:
                attr_name = key.split(':')[1]
            else:
                attr_name=key
            setattr(obj, attr_name, val)

    output = {'Locations': {}, 'Persons': {}}
    for key, locs in dct['Locations'].items():
        output['Locations'][key] = []
        for loc in locs:
            location_obj = GeoEntity(text=loc['text'], label=loc['label'])
            convert_to_ent(loc, location_obj)
            output['Locations'][key].append(location_obj)

    for pers_key, values in dct['Persons'].items():
        output['Persons'][pers_key] = []
        for pers in values:
            pers_obj = PersonEntity(text=loc['text'], label=loc['label'])
            convert_to_ent(pers, pers_obj)
            output['Persons'][pers_key].append(pers_obj)
    return output


def entities_fromJson(entities_json):
    with open(entities_json, 'r') as file:
        data = json.load(file)
    entities = from_json(data)
    return entities


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
