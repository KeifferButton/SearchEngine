# utils/nltk_helper.py

import nltk

def ensure_nltk_resources():
    resource_paths = {
        'wordnet': 'corpora/wordnet',
        'omw-1.4': 'corpora/omw-1.4',
        'punkt': 'tokenizers/punkt',
        'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
        'stopwords': 'corpora/stopwords'
    }

    for resource, path in resource_paths.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource)
