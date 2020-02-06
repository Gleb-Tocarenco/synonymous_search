import requests
import spacy
from urllib.parse import urlparse

from bs4 import BeautifulSoup

nlp = spacy.load('en_core_web_sm')
MESH_DESCRIPTOR = 'https://id.nlm.nih.gov/mesh/lookup/descriptor'
MESH_API_DETAILS = 'https://id.nlm.nih.gov/mesh/lookup/details'

urls = [
 'https://patient.info/forums/discuss/asthma-or-anxiety-need-a-bit-of-advice-please-724249',
 'https://patient.info/forums/discuss/asthma-after-anaphylactic-reaction-719379',
 'https://patient.info/forums/discuss/blood-pressure-meds-for-ears--723608',
 'https://patient.info/forums/discuss/liver-inflammation-from-methotrexate-704988',
 'https://patient.info/forums/discuss/after-ankle-surgery-724182',
 'https://patient.info/forums/discuss/ankle-injury-724323',
 'https://patient.info/forums/discuss/ankylosing-spondylitis-finger-stiffness-and-pain-707576',
 'https://patient.info/forums/discuss/should-iincrease-dose-been-on-10mg-for-4-weeks-no-improvement--726975'
]


data = []

for url in urls:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.find(class_='post__title').getText()
    content = soup.find(id='post_content').findChildren('p', recursive=False)[0].getText()
    data.append({'title': title, 'content': content})

def extract_nouns(text):
    words = set()
    text_doc = nlp(text)
    for token in text_doc:
        if not (token.is_punct or token.is_stop) and token.pos_ == 'NOUN':
            words.add(token.lemma_.strip().lower())
    return words

def find_medical_terms(term):
    r = requests.get(MESH_DESCRIPTOR, params={'label': term})
    if not(r.ok and r.json()):
        return ''
    return r.json()[0]['resource']

def exctract_synonyms(url):
    path = urlparse(url).path
    descriptor = path.split('/')[-1]
    r = requests.get(MESH_API_DETAILS, params={'descriptor': descriptor})
    if not(r.ok and r.json()):
        return ''
    return ', '.join([x['label'].lower() for x in r.json()['terms']])

def update_data_with_synonyms(data):
    for d in data:
        nouns = extract_nouns(d['title'])
        nouns.update(extract_nouns(d['content']))
        medical_terms = []
        for noun in nouns:
            medical_term = find_medical_terms(noun)
            if medical_term: 
                medical_terms.append(medical_term)
        synonyms = []
        for medical_term in medical_terms:
            synonyms_list = exctract_synonyms(medical_term)
            print(synonyms_list)
            synonyms.append(synonyms_list)
        synonyms = ', '.join(synonyms)
        data['synonyms'] = synonyms

def search_by_synonyms(data, term):
    matches = []
    for d in data:
        if term in d['synonyms']:
            matches.append(d)
    return d

update_data_with_synonyms(data)
search_by_synonyms(data, 'headache')
