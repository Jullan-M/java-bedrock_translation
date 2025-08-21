import os
from utilities import *
from typing import Union
from tqdm import tqdm

CORR_KEYS_PATH = "Corr"


class Locale(dict):
    # Class that inherits dict data structure and adds some extra methods to it
    def __init__(self, dictionary: dict = {}, **kwarg) -> dict:
        super().__init__(dictionary, **kwarg)

    def values_with_duplicate_keys(self, corr: list = []) -> dict:
        """
        Makes a dict of values with multiple duplicate keys. 
        If corr is a nonempty list of keys, it will only iterate through those keys instead.
        dict format:
        "value": ["key1", "key2", "key3"]
        """
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
        # Makes a template lang file, including only left-hand side keys of =
        base = self.copy()
        for k in base:
            base[k] = ""
        dict2lang(base, out_file)

    def merge(self, other):
        # Merge another dictionary with self without overwriting existing key-value pairs.
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

    def corresponding_keys(self, existing_keys: list) -> dict:
        """
        Makes a dictionary of corresponding keys between LEFT and RIGHT locale.
        These keys have the same value in their respective dicts.
        Dict format:
        "left.key" = {
                    "key" = "right.key",
                    "rank" = "RANK_NAME"
                }
        """
        corr = {}  # Corresponding keys between loc_L and loc_R
        ignore_chars = dict.fromkeys(map(ord, " ,.!?-:;'"), None)

        for k1, v1 in tqdm(self.loc_L.items()):
            for k2 in existing_keys:
                v2 = self.loc_R[k2]

                # Equal values
                if v1 == v2:
                    corr[k1] = {"key": k2, "rank": "EQUAL"}
                    break

                # Equal lowercase values
                elif v1.lower() == v2.lower():
                    corr[k1] = {"key": k2, "rank": "EQUAL_LOWERCASE"}
                    break

                # The two preceding methods are pretty reliable, so break out of those

                # Equal values when stripped out of ignore_chars
                elif len(v1) > 5 and len(v2) > 5:
                    strip1 = v1.translate(ignore_chars)
                    strip2 = v2.translate(ignore_chars)
                    if strip1.lower() == strip2.lower():
                        corr[k1] = {"key": k2, "rank": "EQUAL_STRIPPED"}

                # Equal keys
                elif k1 == k2:
                    corr[k1] = {"key": k2, "rank": "EQUAL_KEYS"}

                # Similar values based on longest common subsequences
                elif len(v1) > 15 and len(v2) > 15 and lcs(v1, v2, False) >= 0.6*(len(v1)+len(v2))/2:
                    print(v1)
                    print(v2)
                    corr[k1] = {"key": k2, "rank": "SIMILAR_LCS"}

        return corr

    def translate_corr_entries(self, localization: Union[dict, Locale], temp_file: str = "") -> dict:
        # Translate existing locale an existing localization on the LEFT format to RIGHT format based on corresponding keys
        loc = localization if type(
            localization) == Locale else Locale(localization)
        translated = lang2dict(temp_file) if temp_file else {}
        for kc in self.corresponding:
            if self.corresponding[kc]["key"] in loc:
                translated[kc] = loc[self.corresponding[kc]["key"]]
        return translated


class Locale_Translation:
    def __init__(self, locale_pair_files: list, target_locale_file: str, LOCALE_PATH: str = "Locales"):
        self.LOCALE_PATH = LOCALE_PATH
        # Convert locale files to dicts
        self.locale_pairs = [[file2dict(os.path.join(self.LOCALE_PATH, loc_L)), file2dict(
            os.path.join(self.LOCALE_PATH, loc_R))] for loc_L, loc_R in locale_pair_files]

        # Extensions
        self.ext1 = locale_pair_files[0][0].split(".")[-1].lower()
        self.ext2 = locale_pair_files[0][1].split(".")[-1].lower()

        # Target file to be used to find translations
        self.target = file2dict(os.path.join(LOCALE_PATH, target_locale_file))
        self.unused_keys = set(self.target)

    def find_corresponding_keys(self, existing_keys: list = []):
        # Use keys in target as existing keys if not defined already
        existing_keys = self.target.keys() if not existing_keys else existing_keys
        self.pairs = [Locale_Pair(loc_L, loc_R, existing_keys)
                      for loc_L, loc_R in self.locale_pairs]

    def rank_and_generate(self) -> dict:
        translation = {}

        # Make pool of translated keys
        key_pool = set()
        for pair in self.pairs:
            key_pool = key_pool.union(pair.corresponding.keys())

        # Rank keys based on their method of translation and how the values match across locales
        for key in key_pool:
            key_quality = 0
            for pair in self.pairs:
                if key in pair.corresponding.keys():
                    corr_key = pair.corresponding[key]["key"]
                    # Compare to other pairs (if they contain the key)
                    for other in self.pairs:
                        if pair != other and key in other.corresponding.keys():
                            if other.loc_L[key].lower() == other.loc_R[corr_key].lower():
                                key_quality += 1
                                # print(key_quality, pair.loc_L[key])

                    rank = pair.corresponding[key]["rank"]
                    translation[key] = {"value": self.target[corr_key],
                                        "rank": rank,
                                        "quality": key_quality}
                    # Break out of pair-loop; we've already determined the translation and its quality
                    break
        return translation


def generate_tranlation(locale_pair_files: list, dest_locale_file: str, LOCALE_PATH: str = "Locales"):
    ext1 = locale_pair_files[0][0].split(".")[-1].lower()
    ext2 = locale_pair_files[0][1].split(".")[-1].lower()

    dest_locale = file2dict(os.path.join(LOCALE_PATH, dest_locale_file))
    unused_keys = set(dest_locale.keys())
    translation = {}
    for loc_L, loc_R in locale_pair_files:
        loc_pair = Locale_Pair(
            file2dict(os.path.join(LOCALE_PATH, loc_L)),
            file2dict(os.path.join(LOCALE_PATH, loc_R)),
            dest_locale.keys())
        loc_trans = loc_pair.translate_corr_entries(dest_locale)
        count = 0
        for k in loc_pair.corresponding:
            if not (k in translation):
                translation[k] = loc_trans[k]
                unused_keys.discard(loc_pair.corresponding[k]["key"])
                count += 1
        print(count, "entries translated from pair:", loc_L, loc_R)
        print("Current unused_keys:", len(unused_keys))
    dict2file(translation, dest_locale_file.replace(ext2, ext1))
    return Locale(translation)


'''
loc_par = [["en_US.lang", "en_us.json"], ["fi_FI.lang", "fi_fi.json"], ["nb_NO.lang", "no_no.json"]]
target_loc = "se_no.json"

lt = Locale_Translation(loc_par, target_loc)
generated = lt.rank_and_generate()
dict2json(generated, "test.json")
'''
