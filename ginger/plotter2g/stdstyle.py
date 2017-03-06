import ROOT

from .stylebase import _baseratiostyle


# --------------------------------------------------------------------------
class stdstyle(_baseratiostyle):
    '''Class holding all ratio-plot style settings
    '''
    # ----------------------------------------------------------------------
    @classmethod
    def __lazy_init__(cls):
        '''Lazy initialiset to ROOT being fully loaded at import'''

        if hasattr(cls, 'plotratio'):
            return

        from ROOT import kRed, kOrange, kAzure
        from ROOT import kFullCircle, kOpenCircle

        cls.scalemax  = 1.
        cls.scalemin  = 1.
        cls.ltitle    = ''
        cls.rtitle    = ''
        cls.ytitle2   = 'ratio'
        cls.colors    = [kRed + 1    , kOrange + 7 , kAzure - 6  , kAzure + 9  , kOrange + 7 , kOrange - 2]
        cls.markers   = [kFullCircle , kOpenCircle , kFullCircle , kOpenCircle , kFullCircle , kFullCircle]
        cls.fills     = [0           , 0           , 0           , 0           , 0           , 0          ]
        cls.plotratio = True

        # lenghts
        cls.left        = 100
        cls.right       = 75
        cls.top         = 75
        cls.bottom      = 100

        cls.gap         = 5
        cls.width       = 500
        cls.heighttop   = 500
        cls.heightbot   = 200

        cls.linewidth   = 2
        cls.markersize  = 10
        cls.textsize    = 30
        cls.titley      = 60

        cls.legmargin   = 25
        cls.legboxsize  = 50
        cls.legtextsize = 30

        cls.axsty = {
            'labelfamily' : 4,
            'labelsize'   : 30,
            'labeloffset' : 5,
            'titlefamily' : 4,
            'titlesize'   : 30,
            'titleoffset' : 75,
            'ticklength'  : 20,
            'ndivisions'  : 505,
        }

        cls.xaxsty = {
        }

        cls.yaxsty = {
        }

        cls.errsty      = 3005
        cls.errcol      = ROOT.kGray + 1

        cls.logx        = False
        cls.logy        = False

        cls.morelogx    = False
        cls.morelogy    = False

        cls.userrangex = (0., 0.)

        cls.yrange = (0., 0.)

        # something more active
        cls._legalign  = ('l', 't')
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    def __init__(self):
        self.__lazy_init__()
    # ----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    @property
    def legalign(self):
        return self._legalign
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    @legalign.setter
    def legalign(self, align):
        ha, va = align
        if ha not in 'lr': raise ValueError('Align can only be \'l\' or \'r\'')
        if va not in 'tb': raise ValueError('Align can only be \'t\' or \'b\'')
        self._legalign = align
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    def scale(self, factor):
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
    # ----------------------------------------------------------------------
# --------------------------------------------------------------------------
