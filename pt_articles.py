import json
import asyncio
import aiohttp

WC_PRIO = ("V", "Pron", "N", "A", "Adv", "CC")

URL = "https://satni.uit.no/newsatni/"

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

query = """
query AllArticles($lemma: String!, $wantedLangs: [String]!, $wantedDicts: [String]!) {
    dictEntryList(exact: $lemma, wanted: $wantedLangs, wantedDicts: $wantedDicts) {
        lookupLemmas {
            edges {
                node {
                    lemma
                    pos
                }
            }
        }
        translationGroups {
            translationLemmas {
                edges {
                    node {
                        lemma
                        pos
                    }
                }
            }
        }
    }
}
"""


WORD_QUERY = {
    "operationName": "AllArticles",
    "variables": {
        "wantedLangs": [],
    },
    "query": query
}

WANTED_LANGS = {
    "gtsmenob": ["sme", "nob"],
    "gtnobsme": ["nob", "sme"],
    "gtnobsma": ["nob", "sma"],
    "gtsmanob": ["sma", "nob"],
    "gtsmefin": ["sme", "fin"],
    "gtfinsme": ["fin", "sme"],
    "gtsmesmn": ["sme", "smn"],
    "gtsmnsme": ["smn", "sme"],
    "sammallahtismefin": ["sme", "fin"],
    "gtfinsmn": ["fin", "smn"],
    "gtsmnfin": ["smn", "fin"]
}

def choose_entry(dictEntryList: list) -> dict:
    # Chooses a dictEntry based on a wordclass prioritization list
    global WC_PRIO
    pos_list = [e["lookupLemmas"]["edges"][0]["node"]["pos"] for e in dictEntryList]
    index = -1
    
    # Iterate over WCs in prio list
    for pos in WC_PRIO:
        if pos in pos_list:
            index = pos_list.index(pos)
            break
    
    # If there isn't a WC in WC_PRIO choose the first entry.
    if index == -1:
        index = 0 

    return dictEntryList[index]



async def fetch(session, term, dictname):
    global URL, HEADERS, WORD_QUERY, WANTED_LANGS
    word_query = WORD_QUERY
    word_query["variables"]["lemma"] = term
    word_query["variables"]["wantedDicts"] = dictname
    word_query["variables"]["wantedLangs"] = WANTED_LANGS[dictname]
    async with session.get(URL, headers=HEADERS, data=json.dumps(word_query)) as resp:
        assert resp.status == 200, f"response status code {resp.status}"
        return await resp.json()

async def find_articles(l, d, max_at_once = 100, delay = 7):
    global WANTED_LANGS
    src_lang, dest_lang = WANTED_LANGS[d]

    with open(f"Lemmas/new_{d}_{l}.txt", "r", encoding="utf-8") as f:
        words = f.read().split("\n")
    wordslen = len(words)
    articles = {}
    
    tasks = []
    reqs = []
    async with aiohttp.ClientSession() as session:
        for n, w in enumerate(words):
            task = asyncio.create_task(fetch(session, w, d))
            tasks.append(task)
            if n % max_at_once == 0:
                print(f"{n}/{wordslen}", end="\r")
                reqs.extend(await asyncio.gather(*tasks))
                await asyncio.sleep(delay)
                tasks = []
        print(f"{wordslen}/{wordslen}")
        reqs.extend(await asyncio.gather(*tasks))
    
    for r in reqs:
        try:
            dictEntry = choose_entry(r["data"]["dictEntryList"])
            word = dictEntry["lookupLemmas"]["edges"][0]["node"]["lemma"]
            trans = dictEntry["translationGroups"][0]["translationLemmas"]["edges"][0]["node"]["lemma"]
            articles[word] = trans
        except (IndexError, KeyError) as error:
            print(error)
            print(r)
        
    with open(f"Articles/{d}_{l}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(articles, indent="\t", ensure_ascii=False))

def all_articles(d: str, abc: str):
    for l in abc:
        try:
            print(l)
            loop = asyncio.get_event_loop()
            loop.run_until_complete( find_articles(l, d) )
        except FileNotFoundError:
            print(f"File for letter '{l}' not found, skipping.")
            continue

FIN_ABC = "abcdefghijklmnopqrstuvwxyzåäö"
NOB_ABC = "abcdefghijklmnopqrstuvwxyzæøå"
all_articles("gtfinsme", FIN_ABC)