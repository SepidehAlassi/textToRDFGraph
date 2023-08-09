from nltk.corpus import wordnet

import nltk
import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
#
# nltk.download('wordnet')
synonyms = []

for syn in wordnet.synsets("walked away"):
    for l in syn.lemmas():
        synonyms.append(l.name())

print(set(synonyms))
