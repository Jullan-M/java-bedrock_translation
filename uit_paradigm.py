import requests
from tabulate import tabulate

DICTNAMES = {"sme": "sanit",
             "sma": "baakoeh",
             "sms": "saan",
             "smn": "saanih"}

PREF_DEST = {"sme": "nob",
             "sma": "nob",
             "sms": "nob",
             "smn": "sme"}

def get_p_article(term, dictname, src_lang, dest_lang, pos=""):
    postxt = "" if pos else f"?pos={pos}"
    data = requests.get(f"https://{dictname}.oahpa.no/paradigm/{src_lang}/{dest_lang}/{term}/{postxt}", verify=False)
    return data.json()

class Paradigm:
    def __init__(self, word, lang):
        p_article = get_p_article(word, DICTNAMES[lang], lang, PREF_DEST[lang])
        self.word = word
        self.lang = lang
        self.paradigms = [self.parse_paradigm(
            p) for p in p_article["paradigms"]]

    def parse_paradigm(self, p):
        paradigm = {}
        for e in p:
            paradigm[e[3]] = e[0]
        return paradigm

para1 = Paradigm("vázzit", "sme")
for p in para1.paradigms:
    if not p:
        continue
    wc = next(iter(p)).split("+")[0]  # Wordclass of paradigm element
    # Numbering (Sg, Du, Pl), only used for pronouns
    num = next(iter(p)).split("+")[2] if wc == "Pron" else ""
    table = [[k.replace("+", " "), i] for k, i in p.items()]
    print(tabulate(table, headers=['Word class.', 'Inflexion']))
    print()

print(get_p_article("vázzit", "sanit", "sme", "nob"))