import requests
import json

SME_ABC = "aábcčdđefghijklmnŋoprsštŧuvzž"
NOB_ABC = "abcdefghijklmnopqrstuvwxyzæøå"
FIN_ABC = "abcdefghijklmnopqrstuvwxyzåäö"

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

query = """
query AllLemmas($inputValue: String!, $wantedLangs: [String]!, $wantedDicts: [String]!, $after: String ) {
      stemList(first:10000,
               search: $inputValue,
               wanted: $wantedLangs,
               wantedDicts: $wantedDicts
               after: $after
             ) {
      totalCount
      edges {
        node {
          stem
        }
      }
    }
  }
"""

word_query = {
    "operationName": "AllLemmas",
    "variables": {
        "inputValue": "",
        "wantedLangs": [],
        "wantedDicts": []
    },
    "query": query
}

DICT_LANGS = {
    "gtsmenob": "sme",
    "gtnobsme": "nob",
    "gtnobsma": "nob",
    "gtsmanob": "sma",
    "gtsmefin": "sme",
    "gtfinsme": "fin",
    "gtsmesmn": "sme",
    "gtsmnsme": "smn",
    "sammallahtismefin": "sme",
    "gtfinsmn": "fin",
    "gtsmnfin": "smn"
}

def search(l: str, wantedDicts: list = [], wantedLangs: list = []):
    global header, query, word_query
    # Searches for words that start with the string l
    # Can be of any length
    word_query["variables"]["inputValue"] = l
    if wantedDicts:
        word_query["variables"]["wantedDicts"] = wantedDicts
    if wantedLangs:
        word_query["variables"]["wantedLangs"] = wantedLangs
        
    response = requests.get('https://satni.uit.no/newsatni/', headers=headers, data=json.dumps(word_query))
    return response.json()['data']['stemList']

def search_dict_words(d: str, l: str):
    # Iterates through a letter and finds every word in a given dictionary d.
    global DICT_LANGS
    word_query["variables"]["wantedDicts"] = [d]
    word_query["variables"]["wantedLangs"] = [DICT_LANGS[d]]

    words = set()
    res = search(l)
    
    for w in res['edges']:
        word = w['node']['stem']
        if word[0].islower():
            words.add(w['node']['stem'])
    return words

def save_wordlist(words, filename: str):
    # The words are saved to a txt file e.g. "gtsmenob_á.txt", separated by \n.
    with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(words))

def save_all(d: str, abc: str):
    global DICT_LANGS
    word_query["variables"]["wantedDicts"] = [d]
    word_query["variables"]["wantedLangs"] = [DICT_LANGS[d]]

    for l in abc:
        words = search_dict_words(d, l)
        if words:
            save_wordlist(words, f"Lemmas/{d}_{l}.txt")
        print(l, len(words))

# save_all("gtfinsme", FIN_ABC)