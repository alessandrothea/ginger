import ROOT


# ------------------------------------------------------------------------------
class TH1AddDirSentry:
    def __init__(self, status=False):
        self.status = ROOT.TH1.AddDirectoryStatus()
        ROOT.TH1.AddDirectory(status)

    def __del__(self):
        ROOT.TH1.AddDirectory(self.status)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.__del__()
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
class TH1Sumw2Sentry:
    def __init__(self, sumw2=True):
        self.status = ROOT.TH1.GetDefaultSumw2()
        ROOT.TH1.SetDefaultSumw2(sumw2)

    def __del__(self):
        ROOT.TH1.SetDefaultSumw2(self.status)

    def __enter__(self, type, value, tb):
        return self

    def __exit__(self):
        self.__del__()
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
class TStyleSentry:
    def __init__(self, style):

        if isinstance(style, str):
            style = ROOT.gROOT.GetStyle(style)
        elif not isinstance(style, ROOT.TStyle):
            raise TypeError('TStyleSentry needs a TStyle')
        # use TROOT.GetStyle to get a reference to the TStyle
        # ROOT.gStyle would return a reference to TStyle*
        self._oldstyle = ROOT.gROOT.GetStyle(ROOT.gStyle.GetName())
        style.cd()

    def __del__(self):
        # restore the old style
        self._oldstyle.cd()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.__del__()
# ------------------------------------------------------------------------------
