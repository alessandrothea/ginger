'''
'''

import logging
import ROOT


# ______________________________________________________________________________
class StyleSetter(object):
    '''Utility class to apply settings to ROOT objects
    '''
    _log = logging.getLogger('StyleSetter')

    @classmethod
    def __lazy_init__(cls):
        '''Initialised the _setters attribut to
        avoid ROOT to be fully loaded when the module is imported
        '''

        if hasattr(cls, '_setters'):
            return
        cls._setters = {
            ROOT.TAttAxis: [
                ('labelfamily',   ROOT.TAxis.SetLabelFont),
                ('labelsize',     ROOT.TAxis.SetLabelSize),
                ('labeloffset',   ROOT.TAxis.SetLabelOffset),
                ('titlefamily',   ROOT.TAxis.SetTitleFont),
                ('titlesize',     ROOT.TAxis.SetTitleSize),
                ('titleoffset',   ROOT.TAxis.SetTitleOffset),
                ('ticklength',    ROOT.TAxis.SetTickLength),
                ('ndivisions',    ROOT.TAxis.SetNdivisions),
                ('moreloglabels', ROOT.TAxis.SetMoreLogLabels),
            ],

            ROOT.TAttText: [
                ('textfamily', ROOT.TAttText.SetTextFont),
                ('textsize',   ROOT.TAttText.SetTextSize),
                ('textcolor',  ROOT.TAttText.SetTextColor),
                ('textangle',  ROOT.TAttText.SetTextAngle),
                ('textalign',  ROOT.TAttText.SetTextAlign),
            ],

            ROOT.TAttLine: [
                ('linecolor', ROOT.TAttLine.SetLineColor),
                ('linestyle', ROOT.TAttLine.SetLineStyle),
                ('linewidth', ROOT.TAttLine.SetLineWidth),
            ],

            ROOT.TAttFill: [
                ('fillcolor', ROOT.TAttFill.SetFillColor),
                ('fillstyle', ROOT.TAttFill.SetFillStyle),
                ('fillstyle', ROOT.TAttFill.SetFillStyle),
            ],

            ROOT.TAttMarker: [
                ('markercolor', ROOT.TAttMarker.SetMarkerColor),
                ('markerstyle', ROOT.TAttMarker.SetMarkerStyle),
                ('markersize',  ROOT.TAttMarker.SetMarkerSize),
            ]
        }

    def __init__(self, **opts):
        self.__lazy_init__()
        self._opts = opts

    def apply(self, tobj, **opts):

        myopts = self._opts.copy()
        myopts.update(opts)

        for cls, methods in self._setters.iteritems():
            if not isinstance(tobj, cls):
                continue

            for l, m in methods:
                x = myopts.get(l, None)
                if x is not None:
                    m(tobj, x)
# ______________________________________________________________________________
