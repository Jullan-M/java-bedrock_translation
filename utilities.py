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
    key.name=here is value  # Another comment goes here

    to a Python dictionary of the form
    {
        "key.name" = "here is value"
    }
    Note: all comments in the .lang file will be stripped out in the result dict.
    """
    # NOTE: Comments cannot be preserved in a dictionary file. 
    #       Pass the dictionary file along with the template to dict2lang to get back the comments.
    lang_dic = {}
    count = 0
    for line in lang_txt:
        count += 1

        try:
            strip = line.strip()
            if (not strip) or strip[0] == "#" or strip[1] == "#":
                continue
            key, dirty_val = line.split("=", maxsplit=1)
            val = dirty_val.split("#", 1)[0].rstrip()
            lang_dic[key] = val
        except (ValueError,IndexError) as er:
            print(er)
            print(f"Format error in lang file, Line {count}:\n{line}")
        
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
        js.write(json.dumps(dictionary, indent="\t", sort_keys=True))

def dict2lang(dictionary: dict, out_file: str, template: str = ""):
    # Converts a local Python dictionary to a .lang with the filename out_file
    with open(out_file, "w", encoding="utf-8") as lg:
        if template:
            # If there's a template: preserve order, comments and empty lines in template
            with open(template, "r", encoding="utf-8") as tp:
                for line in tp.readlines():
                    if line[0] == "#" or not ("=" in line):
                        # Write line as is if it is not an actual entry
                        lg.write(line)
                    else:
                        k = line.split("=", maxsplit=1)[0] # key

                        # Find corresponding value in dictionary. If it doesn't exist then it is an empty string
                        v = dictionary[k] if k in dictionary else ""
                        if "#" in line:
                            # Preserve comments after value with one (1) tabulation
                            comment = line.split("#", maxsplit=1)[1]
                            lg.write(f"{k}={v}\t#{comment}") # NOTE: Comments include \n
                        else:
                            lg.write(f"{k}={v}\n")
        else:
            # If no template, dump all pairs in dictionary into simple key=value format with no specific ordering
            lg.write("\n".join(["=".join([k, dictionary[k]]) for k in dictionary]))

def lang2json(lang_file: str):
    # Converts a .lang to a .json of the same name
    dc = lang2dict(lang_file)
    dict2json(dc, lang_file.replace('.lang', 'json"'))

def json2lang(json_file: str):
    # Converts a .json file to a .lang of the same name
    dc = json2dict(json_file)
    dict2lang(dc, json_file.replace('.json', '.lang'))

def file2dict(filename: str):
    # Converts a file to dictionary based on extension
    # The file must either be .lang or .json
    assert ('.' in filename), f"Missing extension in filename: {filename}"
    ext = filename.split(".")[-1].lower()
    if ext == "json":
        return json2dict(filename)
    elif ext == "lang":
        return lang2dict(filename)
    else:
        raise ValueError(f"Unknown file extension in filename: {filename}")

def dict2file(dictionary: dict, out_file: str):
    # Converts a .lang to a .json of the same name
    assert ('.' in out_file), f"Missing extension in filename: {out_file}"
    ext = out_file.split(".")[-1].lower()
    if ext == "json":
        dict2json(dictionary, out_file)
    elif ext == "lang":
        dict2lang(dictionary, out_file)
    else:
        raise ValueError(f"Unknown file extension in filename: {out_file}")



def lcs(x: str, y: str, print_out: bool = False):
    # LONGEST COMMON SUBSTRING
    # Find the length of the strings 
    m = len(x) 
    n = len(y) 
  
    # Declaring the array for storing the dp values 
    ls = [[None]*(n + 1) for i in range(m + 1)] 
  
    # Following steps build L[m + 1][n + 1] in bottom up fashion 
    # Note: L[i][j] contains length of LCS of x[0..i-1] and y[0..j-1]
    for i in range(m + 1): 
        for j in range(n + 1):
            if i == 0 or j == 0:
                ls[i][j] = 0
            elif x[i-1] == y[j-1]: 
                ls[i][j] = ls[i-1][j-1]+1
            else:
                ls[i][j] = max(ls[i-1][j], ls[i][j-1])
    
    if print_out:
        index = ls[m][n]
        lcs_str = [""] * (index+1) 
        i = m
        j = n
        while i > 0 and j > 0:
            # If current character in x and y are same then current character is part of LCS 
            if x[i-1] == y[j-1]: 
                lcs_str[index-1] = x[i-1] 
                i-=1
                j-=1
                index-=1
            # If not same, then find the larger of two and go in the direction of larger value 
            elif ls[i-1][j] > ls[i][j-1]: 
                i-=1
            else: 
                j-=1
        print("str1:\t" + x + "\nstr2:\t" + y + "\nlcs:\t" + "".join(lcs_str))
    
    # ls[m][n] contains the length of LCS of x[0..n-1] & y[0..m-1]
    return ls[m][n]