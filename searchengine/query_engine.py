import argparse
import sys
import re
import sqlite3
import nltk
from nltk import pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
from collections import defaultdict
from config import DB_PATH

def ensure_nltk_resources():
    for resource in [
        'wordnet',
        'omw-1.4',
        'punkt',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng',
        'stopwords'
    ]:
        try:
            nltk.data.find(f'corpora/{resource}')  # corpus lookup
        except LookupError:
            try:
                nltk.data.find(f'taggers/{resource}')  # tagger lookup
            except LookupError:
                nltk.download(resource)

ensure_nltk_resources()

def search(query, use_raw_query=False, limit=20):

    # Return if query is None
    if not query:
        return [], "", ""

    # Map NLTK tags to WordNet tags for POS-aware lemmatization
    def get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN  # default fallback

    lemmatizer = WordNetLemmatizer()

    # Process query:
    # Make lowercase
    query = query.lower()
    # Remove special characters and punctuation
    query = re.sub(r'[^a-zA-Z0-9 ]', '', query)

    # Additional spellchecking step
    if not use_raw_query:
        corrected_query = str(TextBlob(query).correct())
    else:
        corrected_query = query

    # Tokenize query
    tokenized_query = corrected_query.split()
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_query = [w for w in tokenized_query if w not in stop_words]

    # Lemmatize text
    tagged = pos_tag(filtered_query)
    lemmatized_query = [lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in tagged]


    # Search database for terms
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    scores = defaultdict(float)
    
    for term in lemmatized_query:
        cursor.execute('SELECT page_id, tfidf FROM index_terms WHERE term = ?', (term,))
        for page_id, tfidf in cursor.fetchall():
            scores[page_id] += tfidf
            
    top_pages = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    results = []
    for page_id, score in top_pages[:limit]:
        cursor.execute('SELECT url, text, title FROM pages WHERE id = ?', (page_id,))
        url, text, title = cursor.fetchone()
        snippet = extract_snippet(text, lemmatized_query)
        results.append({
            "url": url,
            "score": score,
            "snippet": snippet,
            "title": title,
        })
        
    connection.close()
    
    return results, query, corrected_query

# Extracts a text snippet containing one of the search terms to display below the link
def extract_snippet(text, terms):
    # Split text into sentences
    sentences = sent_tokenize(text)
    
    # Try to find a sentence containing one of the terms
    for sentence in sentences:
        if any(term.lower() in sentence.lower() for term in terms):
            # Bold matched terms
            for term in terms:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                sentence = pattern.sub(r'<b>\g<0></b>', sentence)
            return sentence
        
    # Fallback: return first sentence
    return sentences[0] if sentences else ""