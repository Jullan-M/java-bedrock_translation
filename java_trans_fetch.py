import json

def json2dict(filename: str):
    with open(filename, "r", encoding="utf-8") as js:
        dc = json.load(js)
    return dc

def lang_parser(lang_txt: str):
    lang_dic = {}
    for line in lang_txt:
        strip = line.strip()
        if (not strip) or strip[0] == "#" or strip[1] == "#":
            continue

        key, dirty_val = line.split("=", maxsplit=1)
        val = dirty_val.split("#", 1)[0].rstrip()
        lang_dic[key] = val
    return lang_dic

def lang2dict(filename: str):
    with open(filename, "r", encoding="utf-8") as lg:
        plain_txt = lg.readlines()
    dc = lang_parser(plain_txt)
    return dc

def lang2json(lang_file: str, out_file: str):
    dc = lang2dict(lang_file)
    with open(out_file, "w", encoding="utf-8") as js:
        js.write(json.dumps(dc, indent="\t"))

def dict2json(dictionary: dict, out_file: str):
    with open(out_file, "w", encoding="utf-8") as js:
        js.write(json.dumps(dictionary, indent="\t"))

def dict2lang(dictionary: str, out_file: str):
    with open(out_file, "w", encoding="utf-8") as lg:
        lg.write("\n".join(["=".join([k, dictionary[k]]) for k in dictionary]))

def generate_lang_template(base_file: str):
    base = lang2dict(base_file)
    for k in base:
        base[k] = ""
    dict2lang(base, f"{base_file.replace('.lang', '')}_template.lang")

def corresponding_keys(dict1: dict, dict2: dict):
    corr = {}
    for k1, v1 in dict1.items():
        dict2_vals = list(dict2.values())
        if v1 in dict2_vals:
            i = dict2_vals.index(v1)
            corr[k1] = list(dict2.keys())[i]
    return corr

def check_corresponding_integrity(dictionary: dict, corr: list):
    dup_num = 0
    for kc in corr:
        num = 0
        duplicates = []
        value = dictionary[kc]
        for k in dictionary:
            if dictionary[k] == value and kc != k:
                num += 1
                duplicates.append(k)
        
        if num > 0:
            print(f"Key: {kc}\t with {num} duplicates:")
            print(duplicates)
            print()
            dup_num +=1
    print("Total keys with same value:", dup_num)


def translate_corr_entries(src_json: str, corr_json: str, temp_file: str =""):
    src = json2dict(src_json)
    corr = json2dict(corr_json)
    translated = lang2dict(temp_file) if temp_file else {}

    for kc in corr:
        if corr[kc] in src:
            translated[kc] = src[corr[kc]]

    dict2lang(translated, f"{src_json.replace('.json', '')}_translated.lang")
check_corresponding_integrity(json2dict("en_us.json"), list(json2dict("en-bed-java_corresponding_keys.json").values()))

#translate_corr_entries("se_no.json", "en-bed-java_corresponding_keys.json", temp_file="en_US_template.lang")

"""
en_bed = json2dict("en_US_jsonized.json")
en_java = json2dict("en_us.json")
dict2json(corresponding_keys(en_bed, en_java), "bed-java_corresponding_keys.json")
"""
