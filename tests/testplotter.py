#!/usr/bin/env python

import os.path
import ROOT

from ginger.plotter import H1RatioPlotter

ROOT.TH1.SetDefaultSumw2()
# mypath = os.path.dirname(os.path.abspath(__file__))
# ROOT.gInterpreter.ExecuteMacro(mypath+'/LatinoStyle2.C')

# def resize(x, ratio):
#     x.SetLabelSize(x.GetLabelSize() * ratio / (1 - ratio))
#     x.SetTitleSize(x.GetTitleSize() * ratio / (1 - ratio))

h1 = ROOT.TH1F('aa', 'aaaaaaaa;Some X;Entries', 100, 0, 100)
h2 = ROOT.TH1F('bb', 'bbbbbbbb;Some X;Entries', 100, 0, 100)

hFill = ROOT.TH1F.Fill
gaus = ROOT.gRandom.Gaus

entries = 100000

for i in xrange(entries):
    hFill(h1, gaus(50, 10))
    hFill(h2, gaus(48, 10))

diff = H1RatioPlotter()
diff.set(h2, h1)

diff.yaxsty['titleoffset'] = 100
diff.left = 150
diff.ltitle = "left"
diff.rtitle = "right"

c = diff.plot()

c.Print('H1DiffTester.pdf')
