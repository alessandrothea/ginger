import ROOT
import logging

from ..utils import TH1AddDirSentry
from .toolbox import StyleSetter


# ______________________________________________________________________________
class Hist1D(object):
    '''docstring for .'''

    _log = logging.getLogger('Hist1D')

    # _hist1dstyle = {
    #     'linewidth'   : 2,
    #     'linecolor'   : 1,  # ROOT.kBlack
    #     'markersize'  : 1,
    #     'markercolor' : 1,  # ROOT.kBlack
    #     'markerstyle' : 20,  # ROOT.kFullCircle
    #     'textsize'    : 15,
    #     'fillstyle'   : 0,
    # }

    # __________________________________________________________________________
    @classmethod
    def __lazy_init__(cls):
        '''Initialised the _hist1dstyle attribute to
        avoid ROOT to be fully loaded when the module is imported
        '''
        if hasattr(cls, '_hist1dstyle'):
            return
        cls._hist1dstyle = {
            'linewidth'   : 2,
            'linecolor'   : ROOT.kBlack,
            'markersize'  : 1,
            'markercolor' : ROOT.kBlack,
            'markerstyle' : ROOT.kFullCircle,
            'textsize'    : 15,
            'fillstyle'   : 0,
        }
    # __________________________________________________________________________

    # __________________________________________________________________________
    def __init__(self, h1, **opts):
        if not isinstance(h1, ROOT.TH1):
            raise TypeError("h1 is does not inherit from ROOT.TH1")

        self.__lazy_init__()

        self._style = self._hist1dstyle.copy()
        for n, o in opts.iteritems():
            attr = '_' + n
            if not hasattr(self, attr): continue
            if n == 'style':
                getattr(self, attr).update(o)
            else:
                setattr(self, attr, o)

        sentry = TH1AddDirSentry()
        h1clone = h1.Clone()
        ROOT.SetOwnership(h1clone, False)
        self._obj = h1clone
    # __________________________________________________________________________

    # __________________________________________________________________________
    def _applystyle(self):
        styler = StyleSetter(**self._style)
        styler.apply(self._obj)
    # __________________________________________________________________________

    # __________________________________________________________________________
    def draw(self, opts):
        '''Applies the style and draw the object'''

        self._applystyle()
        self._obj.Draw(opts)
    # __________________________________________________________________________
