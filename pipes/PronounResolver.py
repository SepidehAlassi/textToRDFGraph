from pipes.util.NLP_Parser.spacyParser import SpacyParser

gender_map = {'Masc': {'de': 'männlich', 'en': 'male'},
              'Fem': {'de': 'weiblich', 'en': 'female'}}


def resolve_pronouns(sentence_comp, pers_stack, lang):
    """
    Resolve pronouns found in the text. It updates the sentence components by adding the entity that represents a pronoun.
    TODO: currently only resolves personal pronouns, extend this.
    :param sentence_comp: components of a sentence
    :param pers_stack: Stack of persons found in the text
    :param lang: language of the text
    """
    for sent_num, sent_instances in sentence_comp.items():
        for sent_inst in sent_instances:
            comps = [sent_inst.subj, sent_inst.obj]
            for comp in comps:
                if comp.token.pos_ == 'PRON':
                    morph_info = comp.token.morph.to_dict()
                    if is_resolvable(morph_info):
                        resolve_pers_pronoun(morph_info, comp, sent_num, pers_stack, lang)


def resolve_pers_pronoun(morphology, component, sent_num, persons_stack, lang):
    """
    Resolve the personal pronoun found in the text with respect to its morphology, and gender using the
    stack of person entities created from the text.
    :param morphology: morphology of the pronoun token
    :param component: the component representing the pronoun
    :param sent_num: index number of the sentence containing the pronoun within the text
    :param persons_stack: stack of persons found in text through dependency parsing pipe
    :param lang: language of the text
    :return: the person entity corresponding to the pronoun
    """
    sent_ids = [num for num in list(persons_stack.keys()) if num < sent_num]

    gender = morphology.get('Gender')
    for sent in sent_ids[::-1]:
        persons = persons_stack[sent].copy()
        while len(persons) > 0:
            pers = persons.pop()
            if pers.gender == gender_map[gender][lang]:
                component.entity = pers
                return pers


def is_resolvable(morphology):
    """
    Is a pronoun with given morphology resolvable?
    :param morphology: morphology of the pronoun token
    :return:
    - True, if it is a nominative or accusative 3rd person pronoun.
    - False, otherwise
    """
    gender = morphology.get('Gender')
    number = morphology.get('Number')
    person = morphology.get('Person')
    case = morphology.get('Case')
    pron_type = morphology.get('PronType')
    if pron_type != 'Prs':
        return False
    if gender == 'Neut':
        return False
    if (number == 'Sing' and person == '3') and (case == 'Nom' or case == 'Acc'):
        return True
    else:
        return False


if __name__ == '__main__':
    text = "She is a teacher. He is a musician. It is a dog"
    doc = SpacyParser().spacy_parse(text, 'en')
    for token in doc:
        print(token)
