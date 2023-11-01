from spacy import displacy
import os


def visualize_pos(doc, project_name, sentence_number):
    """
    Visualize dependencies in the sentences of the input text
    :param doc: spacy document object for the input text
    :param project_name:project name
    :param sentence_number: number of the sentence in the text
    """
    dep_svg = displacy.render(doc, style="dep")
    dir = os.path.join(os.path.dirname(__file__), '..', '..')
    filepath = os.path.join(dir, project_name, project_name + "_" + str(sentence_number) + "_dep_vis.svg")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(dep_svg)
