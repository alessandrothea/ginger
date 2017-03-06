# ------------------------------------------------------------------------------
class _baseratiostyle(object):
    '''Base class holding all ratio-plot style settings.

    Derived classes are expected to implement the attributes

    scalemax: float
    scalemin: float
    ltitle: str
        Top-left title.

    rtitle: str
        Top-right title.

    ytitle2: str
        Ratio-plot y-axis title.

    colors: list[int]
        Colors for histograms.

    markers: list[int]
        Markers for histograms.

    fills: list[int]
        Fill styles for histograms.

    plotratio: bool
        Enables/disables the ratio plot.

    left: int
    right: int
    top: int
    bottom: int

    gap: int
    width: int
    heighttop: int
        Height of the upper histogram frame (top/1).

    heightbot: int
        Height of the lower histogram frame (bot/2).

    To be continued...

    '''

    # --------------------------------------------------------------------------
    @property
    def legalign(self):
        '''Legend alignment getter
        '''
        return self._legalign
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    @legalign.setter
    def legalign(self, align):
        '''Legent alignment setter

        Parameters
        ----------
        align: tuple(str,str)
            Horizontal and vertical alignment (ha, va) of the legend with respect to the borders.
            ha: 'l' or 'r'
            va: 't' or 'b'
        '''
        ha, va = align
        if ha not in 'lr': raise ValueError("Align can only be 'l or 'r'")
        if va not in 'tb': raise ValueError("Align can only be 't' or 'b'")
        self._legalign = align
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def scale(self, factor):
        '''Scale all style parameters by a common factor

        Parameters
        ----------
        factor: int
            Scaling factor.
        '''
        self.left        = int(factor * self.left)
        self.right       = int(factor * self.right)
        self.top         = int(factor * self.top)
        self.bottom      = int(factor * self.bottom)

        self.gap         = int(factor * self.gap)
        self.width       = int(factor * self.width)
        self.heighttop    = int(factor * self.heighttop)
        self.heightbot    = int(factor * self.heightbot)

        self.linewidth   = int(factor * self.linewidth)
        self.markersize  = int(factor * self.markersize)
        self.textsize    = int(factor * self.textsize)
        self.titley      = int(factor * self.titley)

        self.legmargin   = int(factor * self.legmargin)
        self.legboxsize  = int(factor * self.legboxsize)
        self.legtextsize = int(factor * self.legtextsize)

        self.axsty['labelsize'   ] = int(factor * self.axsty['labelsize'   ])
        self.axsty['labeloffset' ] = int(factor * self.axsty['labeloffset' ])
        self.axsty['titlesize'   ] = int(factor * self.axsty['titlesize'   ])
        self.axsty['titleoffset' ] = int(factor * self.axsty['titleoffset' ])
        self.axsty['ticklength'  ] = int(factor * self.axsty['ticklength'  ])
    # --------------------------------------------------------------------------
# ------------------------------------------------------------------------------
