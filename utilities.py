import os
import json

def json2dict(json_file: str):
    # Converts a .json to a local Python dictionary
    with open(json_file, "r", encoding="utf-8") as js:
        dc = json.load(js)
    return dc

def lang_parser(lang_txt: str):
    """
    Parses the plain text of a Minecraft .lang file of the form

    ## Comment
    key.name=here is value # Another comment goes here

    to a Python dictionary of the form
    {
        "key.name" = "here is value"
    }
    Note: all comments in the .lang file will be stripped out in the result dict.
    """
    # 
    # This excludes any comments
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
    # Converts a .lang to a local Python dictionary
    # See function lang_parser for how the parsing is done
    with open(filename, "r", encoding="utf-8") as lg:
        plain_txt = lg.readlines()
    dc = lang_parser(plain_txt)
    return dc

def dict2json(dictionary: dict, out_file: str):
    # Converts a local Python dictionary to a .json with the filename out_file
    with open(out_file, "w", encoding="utf-8") as js:
        js.write(json.dumps(dictionary, indent="\t"))

def dict2lang(dictionary: str, out_file: str):
    # Converts a local Python dictionary to a .lang with the filename out_file
    with open(out_file, "w", encoding="utf-8") as lg:
        lg.write("\n".join(["=".join([k, dictionary[k]]) for k in dictionary]))

def lang2json(lang_file: str):
    # Converts a .lang to a .json of the same name
    dc = lang2dict(lang_file)
    dict2json(dc, f"{lang_file.replace('.lang', '')}.json")

def json2lang(json_file: str):
    # Converts a .json file to a .lang of the same name
    dc = json2dict(json_file)
    dict2json(dc, f"{json_file.replace('.json', '')}.lang")
