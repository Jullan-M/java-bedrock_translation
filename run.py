from comparative_translator import Locale_Translation
from excel_tools import Ranked_Translations, methods
from online_translator import neuro_translate
from utilities import dict2json, file2dict

if __name__ == "__main__":
    locale_path = "Locales_1_21"
    loc_par = [
        ["en_US_1_21.lang", "en_us_1_21.json"],
        ["nb_NO_1_21.lang", "no_NO_1_21.json"],
    ]
    target_loc = "se_NO_1_21.json"
    out_gen_trans = "se_no_ranked.json"

    en_dict = file2dict("Locales_1_21/en_us_1_21.json")
    sme_dict = file2dict("Locales_1_21/se_NO_1_21.json")

    lt = Locale_Translation(loc_par, target_loc, LOCALE_PATH=locale_path)
    lt.find_corresponding_keys()  # Use english dictionary keys as basis
    generated = lt.rank_and_generate()
    dict2json(generated, out_gen_trans)

    rt = Ranked_Translations(generated)
    rt.to_excel("ranked_sme.xlsx")
