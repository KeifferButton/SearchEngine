import sqlite3
import re
import math
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from collections import Counter
from config import DB_PATH

def ensure_nltk_resources():
    for resource in [
        'wordnet',
        'omw-1.4',
        'punkt',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng',  # ← this is the missing one
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

print("Starting indexer")

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON")

# Create inverted index table
cursor.execute('DROP TABLE IF EXISTS index_terms')
cursor.execute('''
               CREATE TABLE index_terms (
                   term TEXT,
                   page_id INTEGER,
                   frequency INTEGER,
                   tfidf REAL,
                   PRIMARY KEY (term, page_id),
                   FOREIGN KEY (page_id) REFERENCES pages(id)
               )
''')

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

# For each page in database, get text
cursor.execute('SELECT MAX(id) FROM pages')
max_id = cursor.fetchone()[0]
if max_id:
    for id in range(1, max_id + 1):
        cursor.execute('SELECT url, text FROM pages WHERE id = ?', (id,))
        row = cursor.fetchone()
        # If page not found, skip
        if not row:
            continue
        url, text = row
        
        print("Normalizing text with id:", id)
        
        # Process text:
        # Make lowercase
        text = text.lower()
        # Remove special characters and punctuation
        text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
        # Tokenize text
        tokenized_text = text.split()
        # Remove stop words
        stop_words = set(stopwords.words('english'))
        filtered_text = [w for w in tokenized_text if w not in stop_words]
                
        # Lemmatize text
        tagged = pos_tag(filtered_text)
        lemmatized_text = [lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in tagged]
                
        # Create dictionary of word counts
        word_counts = Counter(lemmatized_text)
            
        # Input into database    
        for term, freq in word_counts.items():
            cursor.execute('''
                INSERT OR IGNORE INTO index_terms (term, page_id, frequency)
                VALUES (?, ?, ?)
            ''', (
                term, id, freq
            ))
            
    
    # Compute TF-IDF values (Term Frequency-Inverse Document Frequency):
    print("Calculating TF-IDF values")
    
    # Get total number of documents
    cursor.execute('SELECT COUNT(*) FROM pages')
    N = cursor.fetchone()[0]
    
    # Get all unique terms
    cursor.execute('SELECT DISTINCT term FROM index_terms')
    all_terms = [row[0] for row in cursor.fetchall()]
    
    for term in all_terms:
        # Document frequency
        cursor.execute('SELECT COUNT(*) FROM index_terms WHERE term = ?', (term,))
        df = cursor.fetchone()[0]
        
        idf = math.log(N / (1 + df))
        
        # Update tf-idf for each occurence of this term
        cursor.execute('SELECT page_id, frequency FROM index_terms WHERE term = ?', (term,))
        for page_id, freq, in cursor.fetchall():
            # Log-Normalized TF
            tf = 1 + math.log(freq)
            tfidf = tf * idf
            cursor.execute('''
                UPDATE index_terms
                SET tfidf = ?
                WHERE term = ? AND page_id = ?
            ''', (tfidf, term, page_id))
            
print("Indexer finished successfully")

connection.commit()
connection.close()