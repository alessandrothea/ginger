'''
'''

import logging
import ROOT
import uuid

from .pad import Pad

_tcanvas_winframe_width = 4
_tcanvas_winframe_height = 28


# ______________________________________________________________________________
def _makecanvas(name, title, w, h):
    '''Helper method to account for Canvas borders

    What about usign TCanvas.SetCanvasSize to ensure the correct geometry?

    Parameters
    ----------

    title : str
        Cavas name.

    w : int
        Canvas width.

    h : int
        Canvas height.
    '''
    return ROOT.TCanvas(name, title, w + _tcanvas_winframe_width, h + _tcanvas_winframe_height)
# ______________________________________________________________________________


# ______________________________________________________________________________
#    ______
#   / ____/___ _____ _   ______ ______
#  / /   / __ `/ __ \ | / / __ `/ ___/
# / /___/ /_/ / / / / |/ / /_/ (__  )
# \____/\__,_/_/ /_/|___/\__,_/____/
#
class Canvas(object):
    '''Wrapper of the ROO Canvas class

    Parameters
    ----------

    minsize: tuple(int,int), optional
        Minimum pad size.
    '''
    _log = logging.getLogger('Canvas')

    # --------------------------------------------------------------------------
    def __init__(self, minsize=(0, 0)):
        self._minsize = minsize
        self._pads = []
        self._grid = {}  # new
        self._hrows = []
        self._wcols = []
        self._obj = None
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __del__(self):
        del self._obj

    # --------------------------------------------------------------------------
    def __getattr__(self, name):
        if not self._obj:
            raise AttributeError
        return getattr(self._obj, name)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # the alignement should be decided here
    def attach(self, pad, i, j ):
        # if ( i < 0 and i > self._nx ) or ( j < 0 and j > self._ny ):
            # raise IndexError('Index out of bounds (%d,%d) not in [0,%d],[0,%d]' % (i,j,self._nx,self._ny))

        if not isinstance(pad, Pad):
            raise TypeError('Expected Pad object, found %s' % pad.__class__.__name__)

        # Remove old pad?
        # old = self._grid[i][j]
        # if old is not None: self._pads.pop(old)

        self._grid[i, j] = pad  # new
        if not pad: return

        self._pads.append(pad)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __setitem__(self, key, value):
        if not isinstance(key, tuple):
            raise TypeError('XXXX')

        if len(key) != 2:
            raise RuntimeError('Wrong dimension')

        self.attach( value, *key )
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def get(self, i, j):
        pad = self._grid[i, j] if (i, j) in self._grid else None

        return pad
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __getitem__(self, key):
        if not isinstance(key, tuple):
            raise TypeError('XXXX')

        if len(key) != 2:
            raise RuntimeError('Wrong dimension')

        return self.get( *key )

    # __________________________________________________________________________
    def _computesize(self):  # new

        nx = max( i for i, j in self._grid.iterkeys()) + 1
        ny = max( j for i, j in self._grid.iterkeys()) + 1

        # print nx,ny,self._grid.keys()

        mw, mh = self._minsize
        hrows = [mh] * ny
        wcols = [mw] * nx

        for (i, j), pad in self._grid.iteritems():
            if not pad: continue
            wcols[i] = max(wcols[i], pad.w)
            hrows[j] = max(hrows[j], pad.h)
            # print wcols[i],hrows[j]

        self._hrows = hrows
        self._wcols = wcols
        h = sum(self._hrows)
        w = sum(self._wcols)
        return w, h
    # __________________________________________________________________________

    # __________________________________________________________________________
    def size(self):
        return self._computesize()
    # __________________________________________________________________________

    # __________________________________________________________________________
    def gridsize(self):
        nx = max( i for i, j in self._grid.iterkeys()) + 1
        ny = max( j for i, j in self._grid.iterkeys()) + 1
        return nx, ny
    # __________________________________________________________________________

    # __________________________________________________________________________
    def _getanchors(self, i, j):
        return sum(self._wcols[0:i]), sum(self._hrows[0:j])
    # __________________________________________________________________________

    # __________________________________________________________________________
    def makecanvas(self, name=None, title=None):

        if not name:
            name = 'canvas_' + str(uuid.uuid1())
        if not title:
            title = name

        # Calculate the expected canvas size according to the size of all pads
        w, h = self._computesize()  # new

        fw, fh = float(w), float(h)
        c = _makecanvas(name, title, w, h)
        c.Draw()

        k = 2

        for (i, j), pad in self._grid.iteritems():
            # Switch back to the canvas at each iteration
            c.cd()
            if not pad: continue

            # assume top-left alignement
            x0, y0 = self._getanchors(i, j)
            x1, y1 = x0 + pad.w, y0 + pad.h

            gw, gh = self._wcols[i], self._hrows[j]
            # print i,j,gw,gh,pad.w,pad.h

            ha, va = pad._align

            if va == 't':
                pass
            elif va == 'm':
                y0 += (gh - pad.h) / 2.
                y1 += (gh - pad.h) / 2.
            elif va == 'b':
                y0 += gh - pad.h
                y1 += gh - pad.h
            else:
                raise KeyError('Unknown vertical alignement %s', va)

            if ha == 'l':
                pass
            elif ha == 'c':
                x0 += (gw - pad.w) / 2.
                x1 += (gw - pad.w) / 2.
            elif ha == 'r':
                x0 += gw - pad.w
                x1 += gw - pad.w
            else:
                raise KeyError('Unknown horizontal alignement %s', ha)

            pname = 'pad_%d_%d' % (i, j)

#                 print pname,' [%d,%d][%d,%d] - [%d,%d][%d,%d]'% (x0,x1,y0,y1,x0,x1,(h-y1),(h-y0)), k
#                 print pname,x0/fw,(h-y0)/fh,x1/fw,(h-y1)/fh, k
            tpad = ROOT.TPad(pname, pname, x0 / fw, (h - y1) / fh, x1 / fw, (h - y0) / fh )  # , k)
            tpad.Draw()
            ROOT.SetOwnership(tpad, False)
            pad._obj = tpad
            pad._applypadstyle()

            # print 'B',p0._obj
            # for pad in c._pads:
            # print pad, p0._obj
            # pad._obj.cd()
            tpad.cd()
            for d, opts in pad._drawables:
                d.draw(opts)

            k += 1

        ROOT.SetOwnership(c, False)
        self._obj = c
        return c

    # --------------------------------------------------------------------------
    def applystyle(self):

        for p in self._pads:
            p._applyframestyle()

        # restore after makein g a proper interface for pad (or not)
        # map(Pad._applyframestyle,self._pads)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def draw(self):
        tc = self.makecanvas()
        self.applystyle()
        return tc
    # --------------------------------------------------------------------------
