'''
'''

import logging
import ROOT

from .toolbox import StyleSetter


# ______________________________________________________________________________
#     __                              __
#    / /   ___  ____ ____  ____  ____/ /
#   / /   / _ \/ __ `/ _ \/ __ \/ __  /
#  / /___/  __/ /_/ /  __/ / / / /_/ /
# /_____/\___/\__, /\___/_/ /_/\__,_/
#            /____/
class Legend(object):

    _log = logging.getLogger('Legend')

    # --------------------------------------------------------------------------
    @classmethod
    def __lazy_init__(cls):
        '''Initialised the _legendstyle attribute to
        avoid ROOT to be fully loaded when the module is imported
        '''
        cls._legendstyle = {
            'textfamily' : 4,
            'textsize'   : 20,
            'textcolor'  : ROOT.kBlack,
        }
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __init__(self, nx, ny, boxsize, **opts):

        if not hasattr(self, '_legendstyle'):
            self.__lazy_init__()

        self._boxsize = boxsize
        self._nx = nx
        self._ny = ny

        self._labelwidth = None
        self._anchor = (0, 0)
        self._align = ('c', 'm')
        self._style = self._legendstyle.copy()

        for n, o in opts.iteritems():
            attr = '_' + n
            if not hasattr(self, attr): continue
            if n == 'style':
                getattr(self, attr).update(o)
            else:
                setattr(self, attr, o)

        self._grid = [[None] * ny for i in xrange(nx)]
        self._legends = []
        self._sequence = [ (i, j) for i in xrange(self._nx) for j in xrange(self._ny) ]
        self._cursor = 0
        self._maxlabelwidth = 0
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
    @property
    def sequence(self):
        return self._sequence[:]
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    @sequence.setter
    def sequence(self, value):

        if len(set(value)) != len(value):
            raise RuntimeError('There are duplicates in the new sequence!')

        if len(value) > self._nx * self._ny:
            raise ValueError('New sequence longer than label')

        self._sequence = value
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def _updatebox(self):
        '''Recalculate the legend box parameters'''
        # apply the style to all the elements first
        for leg in self._legends:
            self._applystyle(leg)

        # extract the pad size
        pad = ROOT.gPad.func()
        pw = pad.GetWw() * pad.GetWNDC()
        # ph = pad.GetWh() * pad.GetHNDC()

        #
        dummy = ROOT.TLatex(0, 0, '')
        setter = StyleSetter(**(self._rootstyle()))
        setter.apply(dummy)

        uxmin = pad.GetUxmin()
        uxmax = pad.GetUxmax()
        # uymin = pad.GetUymin()
        # uymax = pad.GetUymax()

        dx = (uxmax - uxmin) / (1 - pad.GetLeftMargin() - pad.GetRightMargin())
        # dy = (uymax - uymin) / (1 - pad.GetTopMargin() - pad.GetBottomMargin())

        # for each row and col check whether there is at lest an entry
        hrows = [False] * self._ny
        wcols = [False] * self._nx
        widths = []

        for i, col in enumerate(self._grid):
            for j, entry in enumerate(col):
                if not entry: continue
                wcols[i] = True
                hrows[j] = True
                (title, leg) = entry

                dummy.SetTitle(title)

#                 print pad.GetName(),dummy.GetTitle(),dummy.GetXsize()*pw/(ph*dx),dummy.GetYsize()/dy
                # widths.append( dummy.GetXsize()*pw/(ph*dx) )
                widths.append( dummy.GetXsize() * pw / (dx) )

        # add 10%
        self._maxlabelwidth = int(max(widths) * 1.1)

        self._colcount = wcols.count(True)
        self._rowcount = hrows.count(True)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def _getanchor(self, i, j):
        labelwidth = self._labelwidth if self._labelwidth is not None else self._maxlabelwidth
        x0, y0 = self._anchor[0] + i * (labelwidth + self._boxsize), self._anchor[1] + j * self._boxsize

        ha, va = self._align
        if va == 't':
            pass
        elif va == 'm':
            y0 -= self._rowcount * self._boxsize / 2.
        elif va == 'b':
            y0 -= self._rowcount * self._boxsize
        else:
            raise KeyError('Unknown vertical alignement %s', va)

        if ha == 'l':
            pass
        elif ha == 'c':
            x0 -= self._colcount * (self._boxsize + labelwidth) / 2.
        elif ha == 'r':
            x0 -= self._colcount * (self._boxsize + labelwidth)
        else:
            raise KeyError('Unknown horizontal alignement %s', ha)

        return x0, y0
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def _applystyle(self, leg):
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetMargin( 1 )

        methods = [
            ('textfamily'      , leg.SetTextFont),
            ('textsize'        , leg.SetTextSize),
        ]

        rstyle = self._rootstyle()
        for l, m in methods:
            x = rstyle.get(l, None)
            if x is not None: m(x)  # ; print x,m.__name__

    # --------------------------------------------------------------------------
    def addentry(self, obj, opt='', title=None, pos=None ):
        # override the appendion sequence
        if pos:
            i, j = pos
            if ( i < 0 and i > self._nx ) or ( j < 0 and j > self._ny ):
                raise IndexError('Index out of bounds (%d,%d) not in [0,%d],[0,%d]' % (i, j, self._nx, self._ny))
        else:
            if self._cursor >= len(self._sequence):
                raise IndexError('The legend is full!')

            i, j = self._sequence[self._cursor]

            self._cursor += 1

        if not self._grid[i][j] is None:
            raise RuntimeError('Entry (%d,%d) is already assigned' % (i, j))

        self._grid[i][j] = (obj, opt, title)

        leg = ROOT.TLegend( 0, 0, 1, 1 )
        title = obj.GetTitle() if title is None else title
        leg.AddEntry(obj, title, opt)

        # self._applystyle(leg)
        self._legends.append( leg )

        self._grid[i][j] = (title, leg)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def _point(self, x, y):

        pad = ROOT.gPad.func()
        fw = pad.GetWw() * pad.GetWNDC()
        fh = pad.GetWh() * pad.GetHNDC()

        mxsize = 16
        mosize = 8

        u = x / fw
        v = (fh - y) / fh

        ul = (x + mxsize / 2) / fw
        vl = (fh - (y - mxsize / 2)) / fh

        l = ROOT.TLatex(ul, vl, '(%d,%d)' % (x, y) )
        l.SetTextFont(44)
        l.SetTextSize(10)
        l.SetNDC()
        ROOT.SetOwnership(l, False)

        mx = ROOT.TMarker(u, v, ROOT.kPlus)
        mx.SetNDC()
        mx.SetMarkerSize(mxsize / 8.)
        mx.SetBit(ROOT.TMarker.kCanDelete)
        ROOT.SetOwnership(mx, False)

        mo = ROOT.TMarker(u, v, ROOT.kCircle)
        mo.SetNDC()
        mo.SetMarkerSize(mosize / 8.)
        mo.SetBit(ROOT.TMarker.kCanDelete)
        ROOT.SetOwnership(mo, False)

        ms = ROOT.TList()
        ms.Add(mx)
        ms.Add(mo)
        ms.Add(l)

        ROOT.SetOwnership(ms, False)

        return ms
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def draw(self):

        self._updatebox()

        pad = ROOT.gPad.func()
        fw = pad.GetWw() * pad.GetWNDC()
        fh = pad.GetWh() * pad.GetHNDC()

        # self._point(*(self._anchor)).Draw()
        # m = ROOT.TMarker(0,0,ROOT.kPlus)
        # l = ROOT.TLatex()
        for i, col in enumerate(self._grid):
            for j, entry in enumerate(col):
                if not entry: continue
                title, leg = entry

                x0, y0 = self._getanchor(i, j)
                x1, y1 = x0 + self._boxsize, y0 + self._boxsize

                # self._point(x0,y0).Draw()
                # self._point(x1,y1).Draw()

                u0 = x0 / fw
                v0 = (fh - y1) / fh
                u1 = x1 / fw
                v1 = (fh - y0) / fh

                leg.SetX1( u0 )
                leg.SetY1( v0 )
                leg.SetX2( u1 )
                leg.SetY2( v1 )
                leg.Draw()
