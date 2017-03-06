import ROOT

# ----
import sys


# ------------------------------------------------------------------------------
class Directory(object):

    # --------------------------------------------------------------------------
    @property
    def name(self):
        return self._name
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    @property
    def objs(self):
        return {
            # k: a for k, a in self.__dict__.iteritems()
            # if (not isinstance(a, Directory) and not k[0] == '_')
            k: a for k, a in self._children.iteritems()
            if not isinstance(a, Directory)
        }
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    @property
    def dirs(self):
        return {
            # (k, a) for k, a in self.__dict__.iteritems()
            # if (isinstance(a, Directory) and not k[0] == '_')
            k: a for k, a in self._children.iteritems()
            if isinstance(a, Directory)
        }
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def get(self, name):
        # if name[0] == '_':
            # return None
        # return self.__dict__[name]
        return self._children[name]
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __getattr__(self, name):
        print '>>>', name
        try:
            return self._children[name]
        except:
            raise
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __getitem__(self, name):
        return self.get(name)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def show(self, indent=0, level=-1):
        print ' ' * indent + '+', self._name
        # for k, a in self.__dict__.iteritems():
        for k, a in self._children.iteritems():
            # if k[0] == '_':
                # continue
            if isinstance(a, Directory):
                a.show(indent + 1)
            else:
                print ' ' * (indent + 1) + '-', k, '=', a
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __init__(self, tdir):
        if not isinstance(tdir, ROOT.TDirectory):
            raise TypeError('Can\t build a Directory from a %s' % tdir.__class__.__name__)

#         dir = Directory(tdir.GetName())
        self._name = tdir.GetName()
        children = {}

        for k in tdir.GetListOfKeys():
            o = k.ReadObj()
            ROOT.SetOwnership(o, False)
            if k.GetClassName().startswith('TDirectory'):
                o = Directory(o)

            children[k.GetName()] = o

        self._children = children
    # --------------------------------------------------------------------------


class Tee(object):
    def __init__(self, name, mode='w'):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        self.file.close()
        del self.stdout

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
        self.stdout.flush()
# ------------------------------------------------------------------------------


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


# ------------------------------------------------------------------------------
class PadPrinter(object):
    _tcanvas_winframe_width = 4
    _tcanvas_winframe_height = 28

    # ---
    def __init__(self, prefix='', types=['pdf', 'png']):
        self.prefix = prefix
        self.types = types

    # ---
    def saveas(self, pad, filename):

        oldpad = ROOT.gPad.func()
        ww = int(pad.GetWNDC() * pad.GetWw())
        wh = int(pad.GetHNDC() * pad.GetWh())

        nm = '%s_%s' % (filename, pad.GetName())

        c = ROOT.TCanvas(nm, nm, ww + self._tcanvas_winframe_width, wh + self._tcanvas_winframe_height)
        c.cd()

        newpad = pad.DrawClone()
        newpad.SetPad(0, 0, 1, 1)

        for ext in self.types:
            c.Print('%s/%s.%s' % (self.prefix, filename, ext))

        oldpad.cd()

    # ---
    def saveall(self, **pads):

        for filename, pad in pads.iteritems():
            self.saveas(pad, filename)

    # ---
    def savefromcanvas(self, canvas, **pads):
        # waiting for python 2.7
        # args = {n:canvas.GetPad(i) for n,i in pads.iteritems()}
        args = dict( [ (n, canvas.GetPad(i)) for n, i in pads.iteritems() ] )

        self.saveall(**args)

    __call__ = saveall
