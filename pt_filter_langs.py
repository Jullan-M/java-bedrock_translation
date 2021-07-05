import asyncio
import aiohttp

async def fetch(session, term, dictname, src_lang, dest_lang) -> dict:
    url = f"https://{dictname}.oahpa.no/lookup/{src_lang}/{dest_lang}/?lookup={term}"
    async with session.get(url) as resp:
        #### REMOVE ME '''
        if resp.status == 500:
            print(f"{term}")            
            return {}
        ####'''
        assert (resp.status == 200), f"response status code {resp.status} for '{term}'"
        return await resp.json()

async def multifetch(terms, src_lang, dest_lang, max_at_once = 100, delay = 6):
    wordslen = len(terms)
    tasks = []
    reqs = []
    async with aiohttp.ClientSession() as session:
        for n, w in enumerate(terms):
            task = asyncio.create_task(fetch(session, w, "sanit", src_lang, dest_lang))
            tasks.append(task)
            if n % max_at_once == 0:
                print(f"{n}/{wordslen}", end="\r")
                reqs.extend(await asyncio.gather(*tasks))
                await asyncio.sleep(delay)
                tasks = []
        print(f"{wordslen}/{wordslen}", end="\r")
        reqs.extend(await asyncio.gather(*tasks))
    return reqs

async def filter_lang_lemmas(l, d, src_lang, dest_lang):
    with open(f"Lemmas/{d}_{l}.txt", "r", encoding="utf-8") as f:
        words = f.read().split("\n")
    new_words = set()


    reqs = await multifetch(words, src_lang, dest_lang)
    
    for r in reqs:
        if r:
            word = r["result"][0]["input"]
            tags = r["tags"]
            if tags:
                new_words.add(word)
    new_words = list(new_words)
    new_words.sort()
    
    with open(f"Lemmas/new_{d}_{l}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(new_words))
    print(len(words), "->", len(new_words))

def filter_all(d: str, src_lang: str, dest_lang: str, abc: str):
    for l in abc:
        try:
            print(l)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(filter_lang_lemmas(l, d, src_lang, dest_lang))
        except FileNotFoundError:
            print(f"File for letter '{l}' not found, skipping.")
            continue

# FIN_ABC = "abcdefghijklmnopqrstuvwxyzåäö"
# filter_all("gtfinsme", "fin", "sme", FIN_ABC)