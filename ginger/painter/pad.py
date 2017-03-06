import logging
import ROOT

from .toolbox import StyleSetter


# ______________________________________________________________________________
#     ____            __
#    / __ \____ _____/ /
#   / /_/ / __ `/ __  /
#  / ____/ /_/ / /_/ /
# /_/    \__,_/\__,_/
#
class Pad(object):
    '''Wrapper of the ROOT.Pad class.

    Parameters
    ----------

    name : str
        Pad name.

    width : int, optional
        Pad width.

    height : int, optional
        Pad height.

    **opts :
        Arbitrary style parameters
    '''
    _log = logging.getLogger('Pad')

    # __________________________________________________________________________
    @classmethod
    def __lazy_init__(cls):
        '''Initialised the _axisstyle attribute to
        avoid ROOT to be fully loaded when the module is imported

        OK, no ROOT enums are used here (yet), but just in case.
        '''

        if hasattr(cls, '_axisstyle'):
            return

        cls._axisstyle = {
            'labelfamily': 4,
            'labelsize':   20,
            'labeloffset': 2,
            'titlefamily': 4,
            'titlesize':   25,
            'titleoffset': 30.,
            'ticklength':  10,
            'ndivisions':  505,
        }
    # __________________________________________________________________________

    # __________________________________________________________________________
    def __init__(self, name, width=500, height=500, **opts):

        self.__lazy_init__()

        self._name = name
        self._w = width
        self._h = height
        self._align = ('c', 'm')  # lcr
        self._showtitle = False
        self._showstats = False

        self._obj = None
        self._drawables = []

        self._margins = (60, 60, 60, 60)
        self._xaxis = self._axisstyle.copy()
        self._yaxis = self._axisstyle.copy()

        # temp solution

        for n, o in opts.iteritems():
            attr = '_' + n
            if not hasattr(self, attr):
                continue
            if n == 'xaxis' or n == 'yaxis':
                getattr(self, attr).update(o)
            else:
                setattr(self, attr, o)
        self._build()
    # __________________________________________________________________________

    # __________________________________________________________________________
    def _build(self):
        m = self._margins
        if isinstance(m, tuple):
            if len(m) == 1:
                m = (m[0], m[0], m[0], m[0])
            elif len(m) == 2:
                m = (m[0], m[0], m[1], m[1])
            elif len(m) == 4:
                pass
            else:
                raise ValueError('margins must be a 1,2,4 length tuple')
        self._margins = m
    # __________________________________________________________________________

    # __________________________________________________________________________
    @property
    def xaxis(self): return self._xaxis
    # __________________________________________________________________________

    # __________________________________________________________________________
    @property
    def yaxis(self): return self._yaxis
    # __________________________________________________________________________

    # __________________________________________________________________________
    @property
    def w(self): return self._w
    # __________________________________________________________________________

    # __________________________________________________________________________
    @property
    def h(self):
        return self._h
    # __________________________________________________________________________

    # __________________________________________________________________________
    def __str__(self):
        return '%s(\'%s\',w=%d,h=%d,obj=%s)' % (
            self.__class__.__name__, self._name, self._w, self._h, self._obj
        )
    # __________________________________________________________________________

    # __________________________________________________________________________
    def __getattr__(self, name):
        if not self._obj:
            raise AttributeError('%s not found' % name)
        return getattr(self._obj, name)
    # __________________________________________________________________________

    # __________________________________________________________________________
    def add(self, drawable, opts=''):
        '''
        Parameters:
            drawable: Hist1D
            opts: str, optional

        '''

        # if not isinstance(drawable, ROOT.TH1):
        #     raise TypeError('Expeted ROOT.TH1, found %s' % drawable.__class__.__name__)

        self._drawables.append( (drawable, opts) )
    # __________________________________________________________________________

    # __________________________________________________________________________
    def _applyobjstyle(self):
        for o in self._drawables:
            o._applystyle()
    # __________________________________________________________________________

    # __________________________________________________________________________
    def _applypadstyle(self):

        left, right, top, bottom = self._margins
        fh, fw = float(self._h), float(self._w)

        if top    is not None: self._obj.SetTopMargin    ( top / fh )
        if bottom is not None: self._obj.SetBottomMargin ( bottom / fh )
        if left   is not None: self._obj.SetLeftMargin   ( left / fw )
        if right  is not None: self._obj.SetRightMargin  ( right / fw )
    # _________________________________________________________________________

    # __________________________________________________________________________
    def _applyframestyle(self):
        '''Apply the style to the Pad's frame
        '''

        # Loop over the list of primitives. Stop at the first TH1, THStack or TMultiGraph
        # TODO: What about simple TGraphs?
        h = None
        for o in self._obj.GetListOfPrimitives():
            if not (
                isinstance(o, ROOT.TH1) or
                isinstance(o, ROOT.THStack) or
                isinstance(o, ROOT.TMultiGraph)
            ):
                continue
            h = o
            break

        # TODO fix the frame line width
        # for o in self._obj.GetListOfPrimitives():
        #     if isinstance(o,ROOT.TFrame):
        #         print 'TFrame linewidth', o.GetLineWidth()
        #         o.SetLineWidth(1)
        #         print 'TFrame linewidth', o.GetLineWidth()

        if not h: return

        # Apply settings to the frame
        frame = h.GetHistogram() if isinstance(h, ROOT.THStack) or isinstance(h, ROOT.TMultiGraph) else h
        if not self._showtitle:
            frame.SetBit(ROOT.TH1.kNoTitle)

            # Delete the histogram's title if already drawn
            for o in self._obj.GetListOfPrimitives():
                if isinstance(o, ROOT.TPaveText) and o.GetName() == 'title':
                    ROOT.SetOwnership(o, True)
                    del o

        if not self._showstats:
            frame.SetBit(ROOT.TH1.kNoStats)
            # Delete the histogram's stats if already drawn
            o = h.FindObject('stats')
            if o.__nonzero__():
                ROOT.SetOwnership(o, True)
                del o

        left, right, top, bottom = self._margins
        lax = self._w - left - right
        lay = self._h - top - bottom

        setter = StyleSetter()

        # Calculate the style parameters for the X axis
        # TODO massive cleanup needed
        xax = h.GetXaxis()
        style = self._xaxis.copy()
        style['ticklength'] *= self._w / float(lax * self._h)
        style['labeloffset'] /= float(self._h - top - bottom)

        # Force variable size fonts
        style['titlefamily']  = style['titlefamily'] * 10 + 2
        # TODO careful the order here is important, as titleoffset is using titlesize in pixels
        style['titleoffset'] *= 1. / (1.6 * style['titlesize']) if style['titlesize'] else 0
        style['titlesize']   /= float(self._h)
        style['labelfamily']  = style['labelfamily'] * 10 + 2
        style['labelsize']   /= float(self._h)

        # Apply the calculated style to the Y axis
        setter.apply(xax, **style)
        self._log.debug('tick xaxis: %s => %s', self._xaxis['ticklength'], style['ticklength'])

        # Calculate the style parameters for the Y axis
        yax = h.GetYaxis()
        style = self._yaxis.copy()
        style['ticklength']   *= self._h / float( lay * self._w)
        style['labeloffset']  /= float(self._w - left - right)
        # style['titleoffset'] *= self._obj.GetWh()/(1.6*self._w*style['titlesize']) if style['titlesize'] else 0

        style['titlefamily']  = style['titlefamily'] * 10 + 2
        # print 'bu',style['titleoffset'], style['titlesize']
        # style['titleoffset'] *= 1./(1.6*style['titlesize']) if style['titlesize'] else 0
        style['titleoffset'] *= self._h / (1.6 * style['titlesize'] * self._w) if style['titlesize'] else 0
        style['titlesize']   /= float(self._h)
        style['labelfamily']  = style['labelfamily'] * 10 + 2
        style['labelsize']   /= float(self._h)
        # print '->>> Y',style['titlefamily'],style['titlesize'],style['titleoffset']

        # Apply the calculated style to the Y axis
        setter.apply(yax, **style)

        self.Modified()
        self._log.debug('tick yaxis: %s =>  %s', self._yaxis['ticklength'])
    # __________________________________________________________________________
# ______________________________________________________________________________


# ______________________________________________________________________________
#     ______          __             ______            __
#    / ____/___ ___  / /_  ___  ____/ / __ \____ _____/ /
#   / __/ / __ `__ \/ __ \/ _ \/ __  / /_/ / __ `/ __  /
#  / /___/ / / / / / /_/ /  __/ /_/ / ____/ /_/ / /_/ /
# /_____/_/ /_/ /_/_.___/\___/\__,_/_/    \__,_/\__,_/
#
class EmbedPad(object):
    '''
    Wrapper to easily embed a tcanvas in as Pad
    '''

    def __init__(self, tcanvas, align=('c', 'm')):
        self._tcanvas = tcanvas
        self._align   = align
        self._obj     = None

    @property
    def w(self): return self._tcanvas.GetWw()

    @property
    def h(self): return self._tcanvas.GetWh()

    def _applypadstyle(self):
        pass

    def _applyframestyle(self):
        # here draw the
        self._obj.cd()
        ROOT.gROOT.SetSelectedPad(self._obj)
        self._tcanvas.DrawClonePad()
# ______________________________________________________________________________
