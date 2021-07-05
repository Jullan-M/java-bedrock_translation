from utilities import word_replace

def lenval_sort(dc: dict) -> list:
    # Sort dictionary by value string length, longest to shortest
    # Returns a list with pairs
    return sorted(dc.items(), key=lambda i: -len(i[1]) if i else 0)

def sorted_dict_from_pair(src_dict: dict, dest_lang: dict, max_len = 100) -> dict:
    # Make a dictionary between two languages based on the lenval_sort() above
    # Inputs are dictionaries of the form {key: value}
    src_sorted = dict(lenval_sort(src_dict))
    dc = {}
    for k in src_sorted:
        src_v = str(src_sorted[k])
        if k in dest_lang and len(src_v) < max_len:
            dest_v = str(dest_lang[k])
            dc[src_v] = dest_v
    return dc

def merge_dicts(dicts: list) -> list:
    merged_dict = {}
    for d in dicts:
        merged_dict = {**merged_dict, **d}
    return merged_dict

def partial_translate(src_dict: dict, dc: dict, src_lang: str = "en", min_len: int = 2):
    """
    src_dict: dict to be sorted
    dc: dict that is used for sorted. Either fetched from sorted_dict_from_pair() or other sources
    Returns partially translated src_dict
    """
    ignore_chars = dict.fromkeys(map(ord, " ,.!?-:;'"), None)
    pt_trans = {}
    src_sorted = lenval_sort(src_dict)
    for k, v in src_sorted:
        value = v
        for v_src in dc:
            if v_src in value and len(v_src) > min_len:
                value = word_replace(v_src, dc[v_src], value)
        
        
        if src_lang == "en":
            # Check every word in value whether they are plural
            # If no plural dictionary value exist, use singular (in case that exists) 
            for word in set(v.translate(ignore_chars).split(" ")):
                if word and len(word) > min_len and word.endswith('s') and not word.endswith("ss"):
                    v_sing = word[:-1]
                    if v_sing in dc:
                        value = word_replace(v_sing, dc[v_sing], value)
        if value != v:
            pt_trans[k] = value
    return pt_trans

from utilities import json2dict, lang2dict
NOB_ABC = "abcdefghijklmnoprstuvwyzæøå"
l_dicts = [json2dict(f"Articles/gtnobsme_{l}.json") for l in NOB_ABC]
nobsme = merge_dicts(l_dicts)
en_loc = json2dict("basic.json")

pt = partial_translate(en_loc, nobsme, src_lang="nob")
for k, v in list(pt.items())[:60]:
    print(f"{v}\n")