import ROOT

from .stylebase import _baseratiostyle

# --------------------------------------------------------------------------
class smallstyle(_baseratiostyle):
    '''Class holding all ratio-plot style settings for small plots
    '''

    # ----------------------------------------------------------------------
    @classmethod
    def __lazy_init__(cls):
        if hasattr(self, 'plotratio'):
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
        cls.left        = 50
        cls.right       = 35
        cls.top         = 35
        cls.bottom      = 50

        cls.gap         = 5
        cls.width       = 250
        cls.heighttop    = 250
        cls.heightbot    = 100

        cls.linewidth   = 1
        cls.markersize  = 5
        cls.textsize    = 15
        cls.titley      = 30

        cls.legmargin   = 12
        cls.legboxsize  = 25
        cls.legtextsize = 15

        cls.axsty = {
            'labelfamily' : 4,
            'labelsize'   : 15,
            'labeloffset' : 2,
            'titlefamily' : 4,
            'titlesize'   : 15,
            'titleoffset' : 35,
            'ticklength'  : 10,
            'ndivisions'  : 505,
        }

        cls.xaxsty = {}
        cls.yaxsty = {}

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
    def __lazy_init__(self):
        self.__lazy_init__()
    # ----------------------------------------------------------------------
# --------------------------------------------------------------------------
