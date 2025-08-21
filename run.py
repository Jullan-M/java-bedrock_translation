from excel_tools import Ranked_Translations, methods
from comparative_translator import Locale_Translation
from utilities import dict2json

if __name__ == "__main__":
    loc_par = [["en_US.lang", "en_us.json"], ["fi_FI.lang", "fi_fi.json"], ["nb_NO.lang", "no_no.json"]]
    target_loc = "se_no.json"
    gen_trans = "se_no_ranked.json"

    lt = Locale_Translation(loc_par, target_loc)
    generated = lt.rank_and_generate()
    dict2json(generated, gen_trans)

    rt = Ranked_Translations(gen_trans)
    rt.to_excel()