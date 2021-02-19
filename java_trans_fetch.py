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
    
    def to_json(self, filename: str):
        dict2json(self, filename)

    def to_lang(self, filename: str):
        dict2lang(self, filename)

class Locale_Pair:
    def __init__(self, loc_L: Union[dict, Locale], loc_R: Union[dict, Locale], existing_keys: list = []):
        self.loc_L = loc_L if type(loc_L) == Locale else Locale(loc_L)
        self.loc_R = loc_R if type(loc_R) == Locale else Locale(loc_R)
        self.corresponding, self.missing = self.corresponding_keys(existing_keys)
    
    def corresponding_keys(self, existing_keys: list = []) -> (dict, list):
        corr = {} # Corresponding keys between loc_L and loc_R
        missing = [] # Keys that exist in loc_R but are missing in existing_keys
        if existing_keys:
            for k1, v1 in self.loc_L.items():
                for k2, v2 in self.loc_R.items():
                    if v1 == v2 and not (k2 in missing):
                        if k2 in existing_keys:
                            corr[k1] = k2
                        else:
                            missing.append(k2)
                    elif v1.lower() == v2.lower():
                        if k2 in existing_keys:
                            corr[k1] = k2
                        else:
                            missing.append(k2)
                        
        else:
            for k1, v1 in self.loc_L.items():
                locR_vals = list(self.loc_R.values())
                if v1 in locR_vals:
                    i = locR_vals.index(v1)
                    corr[k1] = list(self.loc_R.keys())[i]
        return corr, missing

        
    def translate_corr_entries(self, localization: Union[dict, Locale], temp_file: str = "") -> dict:
        loc = localization if type(localization) == Locale else Locale(localization)
        translated = lang2dict(temp_file) if temp_file else {}
        for kc in self.corresponding:
            if self.corresponding[kc] in loc:
                translated[kc] = loc[self.corresponding[kc]]
        return translated



en_bed = lang2dict("en_US.lang")
en_java = json2dict("en_us.json")
se_java = json2dict("se_no.json")


bed_java_en = Locale_Pair(en_bed, en_java, se_java.keys())
translation = bed_java_en.translate_corr_entries(se_java, temp_file="en_US_template.lang")
dict2lang(translation, "se_no.lang")
"""

dups = loc_bed.keys_with_duplicate_values(list(json2dict("en-bed-java_corresponding_keys.json").keys()))
dict2json(dups, "duplicates.json")
#check_corresponding_integrity(json2dict("en_us.json"), list(json2dict("en-bed-java_corresponding_keys.json").values()))

#translate_corr_entries("se_no.json", "en-bed-java_corresponding_keys.json", temp_file="en_US_template.lang")

en_bed = json2dict("en_US_jsonized.json")
en_java = json2dict("en_us.json")
dict2json(corresponding_keys(en_bed, en_java), "bed-java_corresponding_keys.json")
"""