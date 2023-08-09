from pipes.NLP_Parsers.spacyParser import SpacyParser

gender_map = {'Masc': {'de': 'männlich', 'en': 'male'},
              'Fem': {'de': 'weiblich', 'en': 'female'}}


def pronoun_resolution_pipe(sentence_comp, pers_stack, lang):
    for sent_num, sent_instances in sentence_comp.items():
        for sent_inst in sent_instances:
            comps = [sent_inst.subj, sent_inst.obj]
            for comp in comps:
                if comp.token.pos_ == 'PRON':
                    morph_info = comp.token.morph.to_dict()
                    if is_resolvable(morph_info):
                        resolve_pronoun(morph_info, comp, sent_num, pers_stack, lang)


def resolve_pronoun(morphology, component, sent_num, persons_stack, lang):
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
