'''
'''
import logging
import ROOT

from .toolbox import StyleSetter


# ______________________________________________________________________________
#     __          __
#    / /   ____ _/ /____  _  __
#   / /   / __ `/ __/ _ \| |/_/
#  / /___/ /_/ / /_/  __/>  <
# /_____/\__,_/\__/\___/_/|_|
#
class Latex:

    _log = logging.getLogger('Latex')

    # --------------------------------------------------------------------------
    @staticmethod
    def __lazy_init__(cls):
        '''Initialised the _legendstyle attribute to
        avoid ROOT to be fully loaded when the module is imported
        '''
        cls._latexstyle = {
            'textfamily': 4,
            'textsize'  : 20,
            'textcolor' : ROOT.kBlack,
        }

        cls._hcodes = {
            'l': 10,
            'c': 20,
            'r': 30,
        }

        cls._vcodes = {
            'b': 1,
            'm': 2,
            't': 3,
        }
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __init__(self, text, **opts):

        self.__lazy_init__(self.__class__)

        self._text   = text

        self._anchor = (0, 0)
        self._align = ('c', 'm')
        self._style = self._latexstyle.copy()

        for n, o in opts.iteritems():
            attr = '_' + n
            if not hasattr(self, attr): continue
            if n == 'style':
                getattr(self, attr).update(o)
            else:
                setattr(self, attr, o)

        self._latex = ROOT.TLatex()
        self._latex.SetNDC()
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def _rootstyle(self):
        '''Convert the pixel-based style into ROOT parameters'''

        # extract the pad height
        pad = ROOT.gPad.func()
        ph = pad.GetWh() * pad.GetHNDC()

        style = self._style.copy()
        style['textfamily'] = style['textfamily'] * 10 + 2
        style['textsize']  /= ph
        return style
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def draw(self):

        pad = ROOT.gPad.func()
        fw = float(pad.GetWw() * pad.GetWNDC())
        fh = float(pad.GetWh() * pad.GetHNDC())

        ha, va = self._align
        self._latex.SetTextAlign(self._hcodes[ha] + self._vcodes[va])

        setter = StyleSetter(**(self._rootstyle()))
        setter.apply(self._latex)

        x0, y0 = self._anchor
        self._latex.SetText( x0 / fw, 1 - (y0 / fh), self._text )

        self._latex.Draw()
