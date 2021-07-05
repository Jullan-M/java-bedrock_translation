import asyncio
import aiohttp
import re
from tqdm import tqdm
from pt_filter_langs import multifetch
from utilities import word_replace

async def to_basic_form(src_dict: dict, src_lang, dest_lang, max_at_once = 100, delay = 7):
    words = set()
    regex = r'\w+'

    src = src_dict.values()
    for s in src_dict.values():
        wlist = re.findall(regex, s)
        for w in wlist:
            if len(w) > 1:
                words.add(w.lower())
    
    reqs = await multifetch(words, src_lang, dest_lang, max_at_once=max_at_once, delay=delay)

    baseforms = {}
    for r in reqs:
        if r:
            word = r["result"][0]["input"]
            tags = r["tags"]
            if tags and all([word != t[0] for t in tags]):
                base = tags[0][0]
                baseforms[word] = base
    
    basic = {}
    print("Replacing src_dict with base forms.")
    for k, v in tqdm(src_dict.items()):
        value = v # Value (string) to be changed
        wlist = re.findall(regex, v)
        for w in wlist:
            w_l = w.lower() # lowercase of word w
            if w_l in baseforms:
                value = word_replace(w_l, baseforms[w_l], value)
        if value != v:
            basic[k] = value
    return basic

from utilities import lang2dict
import json
fi = lang2dict("Locales_1_7/fi_FI_1_7.lang")
#no = lang2dict("Locales_1_7/nb_NO_1_7.lang")
#no = {k: v for k,v in list(no.items())[:100]}
loop = asyncio.get_event_loop()
basic = loop.run_until_complete(to_basic_form(fi, "fin", "sme"))
with open("basic.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(basic, indent="\t", ensure_ascii=False))