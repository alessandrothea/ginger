import ROOT

# ----
import sys


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
