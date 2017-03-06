import ROOT

from .stdstyle import stdstyle
from ..utils import TH1AddDirSentry
from ..painter import Canvas, Pad, Legend, Latex

from copy import deepcopy


# --------------------------------------------------------------------------
class H1RatioPlotter(object):
    '''
    '''

    # --------------------------------------------------------------------------
    def __init__(self, styleclass=stdstyle, **kwargs):

        from ROOT import kRed, kOrange, kAzure
        from ROOT import kFullCircle, kOpenCircle

        # self.__dict__['_style'] = self.ratiostyle()
        self.__dict__['_style'] = styleclass()

        for k, v in kwargs.iteritems():
            if not hasattr(self._style, k): raise AttributeError('No ' + k + ' style attribute')
            setattr(self._style, k, v)

        self._h0     = None
        self._hists  = []
        self._canvas = None
        self._pad0   = None
        self._pad1   = None
        self._legend = None
        self._stack  = None
        self._dstack = None
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __del__(self):
        if self._canvas: del self._canvas
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __getattr__(self, name):
        if hasattr(self, '_style'):
            return getattr(self._style, name)
        else:
            raise AttributeError('Attribute ' + name + ' not found')
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __setattr__(self, name, value):
        # if the name starts with '_' it is a data member
        if name[0] != '_' and hasattr(self, '_style') and hasattr(self._style, name):
            return setattr(self._style, name, value)
        else:
            self.__dict__[name] = value
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def set(self, h0, *hs ):
        if not hs and self._style.plotratio:
            raise RuntimeError('cannot compare only 1 histogram')
        n = h0.GetDimension()
        if True in [ h.GetDimension() != n for h in hs ]:
            raise ValueError('Cannot compare histograms with different dimensions')
        sentry = TH1AddDirSentry()
        self._h0 = h0.Clone()
        self._hists = [ h.Clone() for h in hs ]
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    @staticmethod
    def _setrangeuser( ax, urange ):
        lb  = ax.FindBin( urange[0] )
        ub  = ax.FindBin( urange[1] )
        print lb, ub
        ax.SetRange( lb, ub )
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def plot(self, options=''):
        '''

        Parameters
        ----------
        options: str
            Additional TH1::Draw options
        '''

        style     = self._style

        # Local references of style variables
        left       = style.left
        right      = style.right
        top        = style.top
        bottom     = style.bottom

        gap        = style.gap
        width      = style.width
        heighttop   = style.heighttop
        heightbot   = style.heightbot

        linewidth  = style.linewidth
        markersize = style.markersize
        textsize   = style.textsize
        legmargin  = style.legmargin
        titley     = style.titley

        # Generic style
        axsty      = style.axsty

        # X/Y axis style: common + specific settings
        xaxsty     = deepcopy(axsty)
        yaxsty     = deepcopy(axsty)

        xaxsty.update(style.xaxsty)
        yaxsty.update(style.yaxsty)

        # Calculate height and width for the 2 pads
        pw = width + left + right
        ph = heighttop + top + bottom

        ph0 = heighttop + top + gap
        ph1 = heightbot + gap + bottom

        # Special settings for ratio-plot bounday axis
        rxaxsty, ryaxsty = deepcopy(xaxsty), deepcopy(axsty)

        # No label for top-xaxis
        rxaxsty['labelsize'] = 0
        # Special tick spacing for bottom y axis
        ryaxsty['ndivisions'] = 505

        # Create a new ginger Canvas with 1 or 2 pads
        c = Canvas()
        if style.plotratio:
            self._pad0 = c[0, 0] = Pad('p0', pw, ph0, margins=(left, right, top,    gap), xaxis=rxaxsty, yaxis=yaxsty)
            self._pad1 = c[0, 1] = Pad('p1', pw, ph1, margins=(left, right, gap, bottom), xaxis=xaxsty,  yaxis=ryaxsty)
        else:
            self._pad0 = c[0, 0] = Pad('p0', pw, ph,  margins=(left, right, top, bottom), xaxis=xaxsty, yaxis=yaxsty)

        # Instantiate the canvas
        c.makecanvas()
        self._canvas = c

        # Assemble the main plot
        self._pad0.cd()
        self._pad0.SetLogx(style.logx)
        self._pad0.SetLogy(style.logy)

        hists = [self._h0] + self._hists

        # Set linewidth for all histograms
        map(lambda h: ROOT.TH1.SetLineWidth(h, linewidth), hists)

        # border between frame and legend
        ha, va = style.legalign
        x0 = (left + legmargin) if ha == 'l' else (left + width    - legmargin)
        y0 = (top  + legmargin) if va == 't' else (top  + heighttop - legmargin)
        leg = Legend(1, len(hists), style.legboxsize, anchor=(x0, y0),  style={'textsize': self.legtextsize},  align=style.legalign)

        # ROOT marker size 1 = 8px. Convert pixel to root size
        markersize /= 8.

        from itertools import izip

        # Assign colors, markers and fill styles to all histograms
        for h, col, mrk, fll in izip(hists, style.colors, style.markers, style.fills):
            h.SetFillStyle  (fll)
            h.SetFillColor  (col)
            h.SetLineColor  (col)
            h.SetMarkerColor(col)
            h.SetMarkerStyle(mrk)
            h.SetMarkerSize (markersize)
            leg.addentry( h, 'pl')

        # Use a stack to draw the histograms
        stack = ROOT.THStack('overlap', '')

        map(stack.Add, hists)
        stack.Draw('nostack %s' % options)

        # Final tweak to the axis title styles
        stack.GetXaxis().SetTitle(self._h0.GetXaxis().GetTitle())
        stack.GetXaxis().SetMoreLogLabels(style.morelogx)

        stack.GetYaxis().SetTitle(self._h0.GetYaxis().GetTitle())
        stack.GetYaxis().SetMoreLogLabels(style.morelogy)

        # Apply corrections to the x and Y ranges
        # Apply custom range to X-axis if required
        if style.userrangex != (0., 0.):
            stack.GetXaxis().SetRangeUser(*(style.userrangex) )

        # Apply custom range to X-axis if required
        if style.yrange != (0., 0.):
            ymin, ymax = style.yrange
        else:
            yminstored = stack.GetHistogram().GetMinimumStored()
            ymaxstored = stack.GetHistogram().GetMaximumStored()

            ymin = stack.GetMinimum('nostack ' + options) if yminstored == -1111 else yminstored
            ymax = stack.GetMaximum('nostack ' + options) if ymaxstored == -1111 else ymaxstored

        stack.SetMinimum( style.scalemin * ymin)
        stack.SetMaximum( style.scalemax * ymax)

        # Store a reference
        self._stack = stack

        # Draw the legend
        leg.draw()
        self._legend = leg

        # Left title
        self._ltitleobj = Latex(style.ltitle, anchor=(left, titley),     align=('l', 'b'), style={'textsize': textsize} )
        self._ltitleobj.draw()

        # Right title
        self._rtitleobj = Latex(style.rtitle, anchor=(pw - right, titley), align=('r', 'b'), style={'textsize': textsize} )
        self._rtitleobj.draw()

        # Plot the ratio
        if style.plotratio:
            # kill the xtitle of the upper plot
            self._stack.GetXaxis().SetTitle('')

            # ---
            # ratio plot
            self._pad1.cd()
            self._pad1.SetLogx(style.logx)
            h0 = self._h0
            nbins = h0.GetNbinsX()
            # xax   = h0.GetXaxis()

            sentry = TH1AddDirSentry()

            # create the h0 to hx rato
            hratios = []
            colors  = [style.errcol]     + (style.colors[1:]  if len(self._hists) > 1 else [ROOT.kBlack]     )
            markers = [ROOT.kFullCircle] + (style.markers[1:] if len(self._hists) > 1 else [ROOT.kFullCircle])
            allh    = [self._h0] + self._hists

            for hx, col, mrk in izip(allh, colors, markers):
                hr = hx.Clone('ratio_%s_%s' % (hx.GetName(), h.GetName()) )

                # divide by hand to preserve the errors
                for k in xrange(nbins + 2):
                    br, er = hr.GetBinContent(k), hr.GetBinError(k)
                    b0  = h0.GetBinContent(k)
                    if b0 == 0:
                        # empty h0 bin
                        br = 0
                        er = 0
                    else:
                        br /= b0
                        er /= b0

                    hr.SetBinContent(k, br)
                    hr.SetBinError(k, er)

                hr.SetLineWidth   (linewidth)
                hr.SetMarkerSize  (markersize)
                hr.SetMarkerStyle (mrk)
                hr.SetLineColor   (col)
                hr.SetMarkerColor (col)
                hratios.append(hr)

            dstack = ROOT.THStack('ratios', 'ratios')
            ROOT.SetOwnership(dstack, True)

            # and then the ratios
            herr = hratios[0]
            herr.SetNameTitle('err0', 'zero errors')
            herr.SetMarkerSize(0)
            herr.SetMarkerColor(style.errcol)
            herr.SetFillStyle(0)
            herr.SetFillColor(style.errcol)
            herr.SetLineColor(style.errcol)

            # error borders
            herrUp = herr.Clone('errup')
            herrDw = herr.Clone('errdw')

            herrUp.Reset()
            herrDw.Reset()

            for k in xrange(nbins + 2):
                b, e = herr.GetBinContent(k), herr.GetBinError(k)
                herrUp.SetAt( 1 + e, k)
                herrDw.SetAt( 1 - e, k)

            herr.SetFillStyle(style.errsty)

            # build the stack
            dstack.Add(herr, 'E2')
            dstack.Add(herrUp, 'hist')
            dstack.Add(herrDw, 'hist')
            map(dstack.Add, hratios[1:])

            self._pad1.cd()
            dstack.Draw('nostack %s' % options )
            dstack.SetMinimum(0.)
            dstack.SetMaximum(2.)

            ax = dstack.GetXaxis()
            ay = dstack.GetYaxis()
            ax.SetTitle(h0.GetXaxis().GetTitle())
            ax.SetMoreLogLabels(style.morelogx)
            ay.SetTitle(style.ytitle2)

            self._dstack = dstack

            line = ROOT.TGraph(2)
            line.SetNameTitle('oneline', 'oneline')
            line.SetPoint(0, ax.GetXmin(), 1)
            line.SetPoint(1, ax.GetXmax(), 1)
            line.SetBit(ROOT.kCanDelete)
            ROOT.SetOwnership(line, False)
            line.Draw()

            if style.userrangex != (0., 0.): ax.SetRangeUser(*(style.userrangex) )

        c.applystyle()

        return c
