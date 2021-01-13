import ROOT as r
import os
import json
from getParams import *
from array import array

# AM's own version
import sys
sys.path.append("/Users/amizukam/DVJets/atlasstyle")
from AtlasStyle import *
from AtlasLabel import *
SetAtlasStyle()
alabel = "Work in Progress"

r.gROOT.SetBatch()

inputFile = open("data/count_new.txt", "r")
lines = inputFile.readlines()

outputDir = "eventYield_new"
if (not os.path.isdir(outputDir)):
    os.makedirs(outputDir)

outputFile = r.TFile("{}/eventYield.root".format(outputDir), "UPDATE")

gluinoMassList = set()
chi0MassList = set()
dMassList = set()
tauList = set()

units = {
    "mGluino": "GeV",
    "mChi0": "GeV",
    "dMass": "GeV",
    "tau": "ns"
}

labels = {
    "mGluino": "#font[52]{m_{#tilde{g}}}",
    "mChi0": "#font[52]{m}_{#font[152]{#tilde{c}}_{1}^{0}}",
    "dMass": "#font[152]{D}#font[52]{m}",
    "tau": "#font[152]{t}"
}

lumiInPb = 136.0 * 1000
sampleDict = {}

xsFile = open("data/13TeV_gluglu_NNLO_NNLL.json")
xSecs = json.load(xsFile)
for line in lines:
    line = line.replace("\n", "")
    dsid, initial, nPassed = int(line.split("\t")[0]), float(line.split("\t")[1]), float(line.split("\t")[2])
    gluinoMass, chi0Mass, tauStr = getParameters(dsid)
    lifetimeStr = tauStr
    if "p" in lifetimeStr:
        lifetimeStr = lifetimeStr.replace("p", "0.")
    if "ns" in lifetimeStr:
        lifetimeStr = lifetimeStr.replace("ns", "")
    lifetime = float(lifetimeStr)
    xSec = xSecs[str(gluinoMass)]["xsInPb"]
    nSG = xSec * lumiInPb * (nPassed / initial)
    
    sampleDict[dsid] = {"mGluino": gluinoMass, "mChi0": chi0Mass, "tau": lifetime, "nSG": nSG}

    gluinoMassList.add(gluinoMass)
    chi0MassList.add(chi0Mass)
    dMassList.add(gluinoMass-chi0Mass)
    tauList.add(lifetime)

def getGluinoMassSamples(gluinoMass, d):
    return dict((k, v) for k, v in d.items() if v["mGluino"] == gluinoMass)

def getChiMassSamples(chiMass, d):
    return dict((k, v) for k, v in d.items() if v["mChi0"] == chiMass)

def getDeltaMassSamples(dMass, d):
    return dict((k, v) for k, v in d.items() if v["mGluino"]-v["mChi0"] == dMass)

def getTauSamples(tau, d):
    return dict((k, v) for k, v in d.items() if v["tau"] == tau)

def getValues(key, d):
    tempList = []
    for s in d:
        tempList.append(d[s][key])
    values = list(set(tempList))
    values.sort()
    return values

def setRootColorPalette():
    nRGBs = 5
    nContours = 255
    stops = ( 0.00, 0.34, 0.61, 0.84, 1.00 )
    red   = [ 0.00, 0.00, 0.87, 1.00, 0.51 ]
    green = [ 0.00, 0.81, 1.00, 0.20, 0.00 ]
    blue  = [ 0.51, 1.00, 0.12, 0.00, 0.00 ]
    stopsArray = array('d', stops)
    redArray   = array('d', red)
    greenArray = array('d', green)
    blueArray  = array('d', blue)
    r.TColor.CreateGradientColorTable(nRGBs, stopsArray, redArray, greenArray, blueArray, nContours,0.5)
    r.gStyle.SetNumberContours(nContours)

plots = {}
for gmass in gluinoMassList:
    plots["Yield_tau_vs_mchi_fixed_mg_%sGeV"%gmass] = {
        "x": "tau",
        "y": "mChi0",
        "label": "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq), fixed #font[52]{m_{#tilde{g}}} = %s GeV}"%gmass,
        "sampleDict": getGluinoMassSamples(gmass, sampleDict)
    }

for cmass in chi0MassList:
    plots["Yield_tau_vs_mgluino_fixed_mchi_%sGeV"%cmass] = {
        "x": "tau",
        "y": "mGluino",
        "label": "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq), fixed #font[52]{m}_{#font[152]{#tilde{c}}_{1}^{0}} = %s GeV}"%cmass,
        "sampleDict": getChiMassSamples(cmass, sampleDict)
    }

for dmass in dMassList:
    plots["Yield_tau_vs_mchi_fixed_dm_%sGeV"%dmass] = {
        "x": "tau",
        "y": "mChi0",
        "label": "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq), fixed #font[152]{D}#font[52]{m} = %s GeV}"%dmass,
        "sampleDict": getDeltaMassSamples(dmass, sampleDict)
    }

for t in tauList:
    plots["Yield_mg_vs_mchi_fixed_tau_%sns"%str(t).replace(".", "p")] = {
        "x": "mGluino",
        "y": "mChi0",
        "label": "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq), fixed #font[152]{t} = %s ns}"%t,
        "sampleDict": getTauSamples(t, sampleDict)
    }

r.gStyle.SetPaintTextFormat(".3f")
setRootColorPalette()

latexLabel = r.TLatex()
latexLabel.SetNDC()
latexLabel.SetTextFont(42)
latexLabel.SetTextAlign(13)
latexLabel.SetTextSize(0.04)

canvases = {}
histos = {}

for name in plots:
    canvases[name] = r.TCanvas(name, name, 800, 600)
    canvases[name].SetRightMargin(0.2)
    canvases[name].SetTopMargin(0.075)
    canvases[name].SetLeftMargin(0.15)
    canvases[name].SetBottomMargin(0.15)
    xBins = getValues(plots[name]["x"], plots[name]["sampleDict"])
    yBins = getValues(plots[name]["y"], plots[name]["sampleDict"])
    print(xBins, yBins)
    histos[name] = r.TH2D(name, name, len(xBins), 0, len(xBins), len(yBins), 0, len(yBins))
    # Set the labels
    histos[name].GetXaxis().SetTitle(labels[plots[name]["x"]] + " [%s]" % units[plots[name]["x"]])
    histos[name].GetYaxis().SetTitle(labels[plots[name]["y"]] + " [%s]" % units[plots[name]["y"]])
    histos[name].GetZaxis().SetTitle("Expected event yield")
    histos[name].SetMinimum(0)
    bin = 1
    for label in xBins:
        histos[name].GetXaxis().SetBinLabel(bin, str(label))
        bin += 1
    bin = 1
    for label in yBins:
        histos[name].GetYaxis().SetBinLabel(bin, str(label))
        bin += 1
    # Fill and draw
    xBin = 1

    samples = plots[name]["sampleDict"]
    for dsid in samples:
        xValue = samples[dsid][plots[name]["x"]]
        yValue = samples[dsid][plots[name]["y"]]
        xBin = xBins.index(xValue)
        yBin = yBins.index(yValue)
        nSG = sampleDict[dsid]["nSG"]
        print("DSID: {}, x: {}, y: {}, nSG: {}, ({}, {})".format(dsid, xBin, yBin, nSG, xValue, yValue))
        if (histos[name].GetBinContent(histos[name].FindBin(xBin, yBin))):
            print("Bin already has content: ({}, {}): - will now exit!".format(xBin, yBin))
            sys.exit(1)
        histos[name].Fill(xBin, yBin, nSG)

    histos[name].Smooth()
    histos[name].DrawCopy("colz")
    histos[name].SetContour(1, array('d', [3]))
    histos[name].Draw("cont3 same text")

    ATLASLabel(0.15, 0.945, alabel + "    #font[52]{#sqrt{s}} = 13 TeV, %.1f fb^{-1}"%(lumiInPb*0.001))
    latexLabel.DrawLatex(0.205, 0.075, plots[name]["label"])

    canvases[name].Update()
    canvases[name].Print("{}/{}.pdf".format(outputDir, name))

    outputFile.cd()
    histos[name].Write()
