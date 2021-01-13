import ROOT as r
from array import array
from collections import OrderedDict
import os

# AM's own version
import sys
sys.path.append("/Users/amizukam/DVJets/atlasstyle")
from AtlasStyle import *
from AtlasLabel import *
SetAtlasStyle()
alabel = "Work in Progress"

r.gROOT.SetBatch()

inputFile = r.TFile("eventYield/eventYield.root", "READ")
outputDir = "limitPlots"
if (not os.path.isdir(outputDir)):
    os.makedirs(outputDir)

tauList = [0.01, 0.1, 1., 10.]
#gluinoList = [1600, 1800, 2000, 2200, 2400, 2600]
#chiList = [10, 50, 200, 450, 850, 1250, 1550, 1650, 1750, 1950, 2050, 2150, 2350, 2450, 2550]
gluinoList = [2000, 2200, 2400, 2600]
chiList = [10, 50, 200, 450]

lumiInPb = 136*1000.0

labels = {}
labels["tau"] = "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq)}, fixed #font[152]{t}"
labels["gluino"] = "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq)}, fixed #font[52]{m_{#tilde{g}}}"
labels["chi0"] = "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq)}, fixed #font[52]{m}_{#font[152]{#tilde{c}}_{1}^{0}}"

colors = [41, 30, 46, 9]
plots = {}
plots["tau"] = OrderedDict()
plots["gluino"] = OrderedDict()
plots["chi0"] = OrderedDict()

for t in tauList:
    plots["tau"]["Yield_mg_vs_mchi_fixed_tau_{}ns".format(str(t).replace(".", "p"))] = {
        "x": "mGluino",
        "y": "mChi0",
        "label": "#font[152]{t} = %s ns"%t
    }

for g in gluinoList:
    plots["gluino"]["Yield_tau_vs_mchi_fixed_mg_{}GeV".format(g)] = {
        "x": "tau",
        "y": "mChi0",
        "label": "#font[52]{m_{#tilde{g}}} = %s GeV"%g
    }

for c in chiList:
    plots["chi0"]["Yield_tau_vs_mgluino_fixed_mchi_{}GeV".format(c)] = {
        "x": "tau",
        "y": "mGluino",
        "label": "#font[52]{m}_{#font[152]{#tilde{c}}_{1}^{0}} = %s GeV"%c
    }

canvas = r.TCanvas("c", "c", 800, 600)
canvas.SetTopMargin(0.075)
canvas.cd()

latexLabel = r.TLatex()
latexLabel.SetNDC()
latexLabel.SetTextFont(42)
latexLabel.SetTextAlign(13)
latexLabel.SetTextSize(0.04)

for plot in plots:
    contours = {}
    counter = 0
    if len(plots[plot]) < 3:
        legend = r.TLegend(0.2, 0.2, 0.45, 0.3)
    else:
        legend = r.TLegend(0.2, 0.2, 0.45, 0.4)
    legend.SetFillStyle(0)
    legend.SetLineStyle(0)
    legend.SetBorderSize(0)
    legend.SetEntrySeparation(0.1)
    legend.SetTextFont(42)
    legend.SetTextSize(0.03)

    for limit in plots[plot]:
        print(limit)
        histo = inputFile.Get(limit)
        histo.SetLineColor(colors[counter])
        histo.SetContour(1, array('d', [3]))
        histo.Draw("cont list")
        canvas.Update()
        listOfGraphs = r.gROOT.GetListOfSpecials().FindObject("contours").At(0)
        contour = [r.TGraph(listOfGraphs.At(i)) for i in range(listOfGraphs.GetSize())]
        for co in range(len(contour)):
            contour[co].SetLineWidth(2)
            contour[co].SetLineColor(colors[counter])
            contour[co].SetName("Contour_{}".format(limit))
        print(contour)
        contours[limit] = contour
        counter += 1

    counter = 0
    for limit in plots[plot]:
        contour = contours[limit]
        if not len(contour):
            continue
        if counter == 0:
            contour[0].Draw()
        else:
            contour[0].Draw("same")
        for c in range(1, len(contour)):
            contour[c].Draw("same")
        counter += 1
        legend.AddEntry(contour[0], plots[plot][limit]["label"], "l")

        ATLASLabel(0.15, 0.945, alabel)
        latexLabel.DrawLatex(0.25, 0.075, labels[plot])

        legend.Draw()

        canvas.Update()
        canvas.Print("{}/limits_fixed_{}.pdf".format(outputDir, plot))
