import requests
import json

dicts = {"fin": "gtfinsme", "nob": "gtnobsme"}

backend = "https://satni.uit.no/newsatni/"

headers = {
    'Content-Type': 'application/json',
}

query = """
query AllArticles($lemma: String!, $wantedLangs: [String]!, $wantedDicts: [String]!) {
    dictEntryList(exact: $lemma, wanted: $wantedLangs, wantedDicts: $wantedDicts) {
        dictName
        targetLang
        lookupLemmas {
            edges {
                node {
                    lemma
                    language
                    pos
                }
            }
        }
        translationGroups {
            translationLemmas {
                edges {
                    node {
                        lemma
                        language
                        pos
                    }
                }
            }
            exampleGroups {
                example
                translation
            }
            restriction {
                restriction
            }
        }
    }
    conceptList(exact: $lemma, wanted: $wantedLangs) {
        name
        collections
        definition
        explanation
        terms {
            note
            source
            status
            expression {
                lemma
                language
                pos
            }
        }
    }
}
"""

word_query = {
    "operationName": "AllArticles",
    "variables": {
        "wantedLangs": ["sme", "fin"],
    },
    "query": query
}



def translate(words, src_lang):
    word_query["variables"]["wantedDicts"] = dicts[src_lang]

    trans_words = []
    for w in words:
        word_query["variables"]["lemma"] = w.lower()
        response = requests.post(backend, headers=headers, data=json.dumps(word_query))
        w_article = response.json()
        if w_article['data']['dictEntryList']:
            tw = w_article['data']['dictEntryList'][0]['translationGroups'][0]['translationLemmas']['edges'][0]['node']['lemma']
            trans_words.append(tw)
    return trans_words
    
words = ["Hanki", "Ilma", "Kaunis", "Korkeus", "Ilmainen", "Nimi", "Siemen", "Kesto", "Poista", "Vihreä", "Pilkku"]

print(translate(words, "fin"))

"""
word_query["variables"]["wantedDicts"] = dicts["fin"]
word_query["variables"]["lemma"] = "tyyli"
response = requests.post('https://satni.uit.no/newsatni/', headers=headers, data=json.dumps(word_query))
w_article = response.json()
print(w_article['data']['dictEntryList'])
"""