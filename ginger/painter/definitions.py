'''
ROOT to ginger mappings

Note: when imported ROOT is fully loaded
'''

import ROOT

textfamily = {
    'Times New Roman'            : 13,
    'Times New Roman Italic'     : 1,
    'Times New Roman Bold'       : 2,
    'Times New Roman Bold Italic': 3,
    'Arial'                      : 4,
    'Arial Italic'               : 5,
    'Arial Bold'                 : 6,
    'Arial Bold Italic'          : 7,
    'Courier New'                : 8,
    'Courier New Italic'         : 9,
    'Courier New Bold'           : 10,
    'Courier New Bold Italic'    : 11,
    'Symbol'                     : 12,
    'Symbol Italic'              : 15,
    'Wingdings'                  : 14,
}

textalignment = {
    't': ROOT.kVAlignTop,
    'm': ROOT.kVAlignCenter,
    'b': ROOT.kVAlignBottom,
    'l': ROOT.kHAlignLeft ,
    'c': ROOT.kHAlignCenter,
    'r': ROOT.kHAlignRight,
}
