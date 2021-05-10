import json
from utilities import dict2lang, dict2json
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, colors
from openpyxl.cell.cell import Cell

methods = {
    "_comment": "This json file sets ranking colors for translation methods in excel spread sheets.",
    "EQUAL": "00FF00",
    "EQUAL_LOWERCASE": "008000",
    "EQUAL_STRIPPED": "008080",
    "EQUAL_KEYS": "FF00FF",
    "SIMILAR_LCS": "080000"
}

class Ranked_Translations:
    def __init__(self, rt_filename : str):
        self.workbook = Workbook()
        self.ws = self.workbook.active
        self.filename = rt_filename.split(".")[0]
        with open(rt_filename, "r", encoding="utf-8") as js:
            dc = json.load(js)
        self.rts = dc
    
    def rank_cells(self, rank, quality):
        c = Cell(self.ws, column="A", row=1, value=rank)
        color = methods[rank]
        if quality == 0:
            # If only 1 locale consists of translation, make color "Reddish".
            color = "FF" + color[2:]
        elif rank != "EQUAL_LOWERCASE" and quality >= 1:
            # If translation is consistent across 2 or more locales, then GREEN.
            color = "00FF00"
        elif quality > 1:
            color = "00FF00"

        # Fill background of cell with color
        pf = PatternFill("solid", fgColor=colors.Color(color))
        c.fill = pf
        return c

    def to_excel(self):
        for row in self.rts:
            self.ws.append( [row, self.rts[row]["value"], self.rank_cells(self.rts[row]["rank"], self.rts[row]["quality"])] )
    
        self.workbook.save(filename=f"{self.filename}.xlsx")

def excel2dict(filename: str):
    # Convert   key.goes.here   value     formatted spreadsheets to dict
    wb = load_workbook(filename) # Workbook
    sh = wb.active # Sheet
    dc = {}
    for c1, c2 in zip(sh["A"], sh["B"]):
        k, v = c1.value, c2.value
        if k and not (v == None):
            dc[k] = v
    return dc

def excel2lang(filename: str, out_file: str, template: str = ""):
    dc = excel2dict(filename)
    dict2lang(dc, out_file, template)

def excel2json(filename: str, out_file: str):
    dc = excel2dict(filename)
    dict2json(dc, out_file)
    


