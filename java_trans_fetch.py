from utilities import *
from typing import Union

class Locale(dict):
    def __init__(self, dictionary: dict = {}, **kwarg) -> dict:
        super().__init__(dictionary, **kwarg)
    
    def values_with_duplicate_keys(self, corr: list = []) -> dict:
        duplicates = {}
        keys = corr if corr else self
        for kc in keys:
            value = self[kc]
            if value in duplicates.keys():
                continue
            duplicates[value] = [kc]
            for k, v in self.items():
                if v == value and k != kc:
                    duplicates[value].append(k)  
        return duplicates

    def generate_lang_template(self, out_file: str):
        base = self.copy()
        for k in base:
            base[k] = ""
        dict2lang(base, out_file)
    
    def merge(self, other):
        for k in other:
            if not (k in self):
                self[k] = other[k]
    
    def to_json(self, filename: str):
        dict2json(self, filename)

    def to_lang(self, filename: str):
        dict2lang(self, filename)

class Locale_Pair:
    
    def __init__(self, loc_L: Union[dict, Locale], loc_R: Union[dict, Locale], existing_keys: list = []):
        self.loc_L = loc_L if type(loc_L) == Locale else Locale(loc_L)
        self.loc_R = loc_R if type(loc_R) == Locale else Locale(loc_R)
        #self.count = 0
        self.corresponding = self.corresponding_keys(existing_keys)
    
    def corresponding_keys(self, existing_keys: list) -> (dict, list):
        corr = {} # Corresponding keys between loc_L and loc_R
        ignore_chars = dict.fromkeys(map(ord, " ,.!?-:;'"), None)
        
        for k1, v1 in self.loc_L.items():
            for k2 in existing_keys:
                v2 = self.loc_R[k2]
                if v1 == v2:
                    corr[k1] = k2
                elif v1.lower() == v2.lower():
                    corr[k1] = k2
                elif k1==k2:
                    corr[k1] = k2
                
                elif len(v1) > 5 and len(v2) > 5:
                    strip1 = v1.translate(ignore_chars)
                    strip2 = v2.translate(ignore_chars)
                    if strip1.lower() == strip2.lower():
                        print(v1)
                        print(v2)
                        corr[k1] = k2
                """
                elif len(v1) > 25 and len(v2) > 25 and lcs(v1, v2, False) >= 0.5*(len(v1)+len(v2))/2:
                    print(v1)
                    print(v2)
                    dict_append(k1, k2)
                """
        
        return corr

        
    def translate_corr_entries(self, localization: Union[dict, Locale], temp_file: str = "") -> dict:
        loc = localization if type(localization) == Locale else Locale(localization)
        translated = lang2dict(temp_file) if temp_file else {}
        for kc in self.corresponding:
            if self.corresponding[kc] in loc:
                translated[kc] = loc[self.corresponding[kc]]
        return translated

def generate_tranlation(locale_pair_files: list, dest_locale_file: str):
    ext1 = locale_pair_files[0][0].split(".")[-1].lower()
    ext2 = locale_pair_files[0][1].split(".")[-1].lower()
    dest_locale = file2dict(dest_locale_file)
    unused_keys = set(dest_locale.keys())
    translation = {}
    for loc_L, loc_R in locale_pair_files:
        loc_pair = Locale_Pair(file2dict(loc_L), file2dict(loc_R), dest_locale.keys())
        loc_trans = loc_pair.translate_corr_entries(dest_locale)
        count = 0
        for k in loc_pair.corresponding:
            if not (k in translation):
                translation[k] = loc_trans[k]
                unused_keys.discard(loc_pair.corresponding[k])
                count+=1
        print(count, "entries translated from pair:", loc_L, loc_R)
        print("Current unused_keys:", len(unused_keys))
    dict2file(translation, dest_locale_file.replace(ext2, ext1))
    return translation


loc_par = [["en_US.lang", "en_us.json"], ["fi_FI.lang", "fi_fi.json"], ["nb_NO.lang", "no_no.json"]]
dest_loc = "se_no.json"
generated = generate_tranlation(loc_par, dest_loc)
working = Locale(lang2dict("se_NO_manual.lang"))
working.merge(generated)
working.to_lang("se_no_generated.lang")
"""
en_bed = lang2dict("en_US.lang")
en = Locale(en_bed)
en.generate_lang_template("en_US_template.lang")
en_java = json2dict("en_us.json")
se_java = json2dict("se_no.json")


bed_java_en = Locale_Pair(en_bed, en_java, se_java.keys())
translation = bed_java_en.translate_corr_entries(se_java)
dict2lang(translation, "se_no.lang")


dups = loc_bed.keys_with_duplicate_values(list(json2dict("en-bed-java_corresponding_keys.json").keys()))
dict2json(dups, "duplicates.json")
#check_corresponding_integrity(json2dict("en_us.json"), list(json2dict("en-bed-java_corresponding_keys.json").values()))

#translate_corr_entries("se_no.json", "en-bed-java_corresponding_keys.json", temp_file="en_US_template.lang")

en_bed = json2dict("en_US_jsonized.json")
en_java = json2dict("en_us.json")
dict2json(corresponding_keys(en_bed, en_java), "bed-java_corresponding_keys.json")
"""