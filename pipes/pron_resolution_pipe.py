from pipes.NLP_Parsers.spacyParser import SpacyParser
gender = {'Masc': ['männlich', 'male'],
          'Fem': ['weiblich', 'female']}


def resolve_pronoun(sentence_comp, pers_stack, loc_stack):
    for sent_num, sent_instances in sentence_comp.items():
        for sent_inst in sent_instances:
            subj = sent_inst.subj

            if subj.token.pos_ == 'PRON':
                morph_info = subj.token.morph.to_dict()



if __name__ == '__main__':
    text = "She is a teacher. He is a musician. It is a dog"
    doc = SpacyParser().spacy_parse(text, 'en')
    for token in doc:
        print(token)


