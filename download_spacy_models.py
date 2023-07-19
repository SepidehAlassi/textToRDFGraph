import os

# Download Spacy pretrained models
if __name__ == '__main__':
    # download pretrained model for English language
    os.system('python3 -m spacy download en_core_web_lg')

    # download pretrained model for German language
    os.system('python3 -m spacy download de_core_news_lg')

    # # download pretrained model for french language
    # os.system('python3 -m spacy download fr_core_news_sm')
    #
    # # download pretrained model for italian language
    # os.system('python3 -m spacy download it_core_news_sm')
    #
    # # download pretrained modelf for mult language
    # os.system('python3 -m spacy download xx_ent_wiki_sm')
