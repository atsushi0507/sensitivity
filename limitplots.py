import ROOT as r
import json
from array import array
from getParams import *
import os

# AM's own version
import sys
sys.path.append("/Users/amizukam/DVJets/atlasstyle")
from AtlasStyle import *
from AtlasLabel import *
SetAtlasStyle()
alabel = "Work in Progress"

r.gROOT.SetBatch()

def setRootColorPalette():
    nRGBs = 5
    nContours = 255
    stops = (0.00, 0.34, 0.61, 0.84, 1.00)
    red   = [0.00, 0.00, 0.87, 1.00, 0.51]
    green = [0.00, 0.81, 1.00, 0.20, 0.00]
    blue  = [0.51, 1.00, 0.12, 0.00, 0.00]
    stopsArray = array('d', stops)
    redArray   = array('d', red)
    greenArray = array('d', green)
    blueArray  = array('d', blue)
    r.TColor.CreateGradientColorTable(nRGBs, stopsArray, redArray, greenArray, blueArray, nContours, 0.5)
    r.gStyle.SetNumberContours(nContours)

def getTauSamples(tau, d):
    return dict((k, v) for k, v in d.items() if v["tau"] == tau)

def getChiMassSamples(chiMass, d):
    return dict((k, v) for k, v in d.items() if v["mChi0"] == chiMass)

def getGluinoMassSamples(gluinoMass, d):
    return dict((k, v) for k, v in d.items() if v["mGluino"] == gluinoMass)

def getDeltaMassSamples(dMass, d):
    return dict((k, v) for k, v in d.items() if v["mGluino"]-v["mChi0"] == dMass)

def getValues(key, d):
    tempList = []
    for s in d:
        tempList.append(d[s][key])
    values = list(set(tempList))
    values.sort()
    return values

lumiInPb = 136000.0

cutStr = "DRAW_pass_triggerFlags && DRAW_pass_DVJETS && BaselineSel_pass && DV_passFiducialCut && DV_passDistCut && DV_passChiSqCut && DV_passMaterialVeto && DV_passMaterialVeto_strict && DV_passNTrkCut && DV_passMassCut"

xsFile = open("data/13TeV_gluglu_NNLO_NNLL.json")
xSecs = json.load(xsFile)

outputDir = "limitPlots"
if (not os.path.isdir(outputDir)):
    os.makedirs(outputDir)

outFile = r.TFile("{}/limits.root".format(outputDir), "UPDATE")

filepath = "/Volumes/LaCie/DVJets/mc/signal/mc16d/"
inputFile = "data/mc16d.txt"

infiles = open(inputFile)
files = infiles.readlines()

directory = "limitPlots"
if (not os.path.isdir(directory)):
    os.makedirs(directory)

c = r.TCanvas("c", "c", 800, 600)
sampleDict = {}
gluinoMassList = set()
deltaMassList = set()
chiMassList = set()
tauList = set()
for filename in files:
    filename = filename.replace("\n", "")
    infile = r.TFile(filepath + filename, "READ")
    tree = infile.Get("trees_SRDV_")

    suffix = filename.split("/")[-1]
    print(suffix)
    dsid = int(suffix.split(".")[2])
    gluinoMass, chi0Mass, tauStr = getParameters(dsid)
    if "p" in tauStr:
        tauStr = tauStr.replace("p", "0.")
    if "ns" in tauStr:
        tauStr = tauStr.replace("ns", "")
    tau = float(tauStr)
    sampleDict[dsid] = {"mGluino": gluinoMass, "mChi0": chi0Mass, "dMass": gluinoMass-chi0Mass, "tau": tau}

    gluinoMassList.add(sampleDict[dsid]["mGluino"])
    chiMassList.add(sampleDict[dsid]["mChi0"])
    deltaMassList.add(sampleDict[dsid]["dMass"])
    tauList.add(sampleDict[dsid]["tau"])

    sumW = infile.Get("MetaData_EventCount").GetBinContent(3)
    mcWeight = tree.mcEventWeight
    gMass = sampleDict[dsid]["mGluino"]
    xSec = xSecs[str(gMass)]["xsInPb"]
    tree.Draw(">>elist", cutStr)
    elist = r.gDirectory.Get("elist")
    nPassed = elist.GetN()
    weight = xSec * lumiInPb * (mcWeight / sumW)
    print(xSec, lumiInPb, mcWeight, sumW, weight)
    
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
    
    plots = {}
    
    for gmass in gluinoMassList:
        plots["Limit_tau_vs_mchi_fixed_mg_%sGeV"%gmass] = {
            "x": "tau",
            "y": "mChi0",
            "label": "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq), fixed #font[52]{m_{#tilde{g}}} = %s GeV}"%gmass,
            "sampleDict": getGluinoMassSamples(gmass, sampleDict)
        }
        
    for cmass in chiMassList:
        plots["Limit_tau_vs_mgluino_fixed_mchi_{}GeV".format(cmass)] = {
            "x": "tau",
            "y": "mGluino",
            "label": "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq), fixed #font[52]{m}_{#font[152]{#tilde{c}}_{1}^{0}} = %s GeV}"%cmass,
            "sampleDict": getChiMassSamples(cmass, sampleDict)
        }
        
    for dmass in deltaMassList:
        plots["Limit_tau_vs_mchi_fixed_dm_{}GeV".format(dmass)] = {
            "x": "tau",
            "y": "mChi0",
            "label": "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq), fixed #font[152]{D}#font[52]{m} = %s GeV}"%dmass,
            "sampleDict": getDeltaMassSamples(dmass, sampleDict)
        }
        
    for t in tauList:
        plots["Limit_mg_vs_mchi_fixed_tau_{}ns".format(str(t).replace(".", "p"))] = {
            "x": "mGluino",
            "y": "mChi0",
            "label": "#font[42]{#tilde{g}#rightarrowqq}#font[152]{#tilde{c}}_{#font[52]{0}}#font[42]{(#rightarrowqqq), fixed #font[152]{t} = %s ns}"%t,
            "sampleDict": getTauSamples(t, sampleDict)
        }
        
    r.gStyle.SetPaintTextFormat(".3f") # for text draw option
    setRootColorPalette() # for smoother rainbow palette
    
    # for drawing labels
    latexLabel = r.TLatex()
    latexLabel.SetNDC()
    latexLabel.SetTextFont(42)
    latexLabel.SetTextAlign(13)
    latexLabel.SetTextSize(0.04)
    
    canvases = {}
    pads = {}
    histos = {}
    for name in plots:
        canvases[name] = r.TCanvas(name, name, 800, 600)
        canvases[name].SetRightMargin(0.2)
        xBins = getValues(plots[name]["x"], plots[name]["sampleDict"])
        yBins = getValues(plots[name]["y"], plots[name]["sampleDict"])
        #print("xBins: ", xBins)
        #print("yBins: ", yBins)
        histos[name] = r.TH2F(name, name, len(xBins), 0, len(xBins), len(yBins), 0, len(yBins))
        # set the labels
        histos[name].GetXaxis().SetTitle(labels[plots[name]["x"]] + " [%s]" % units[plots[name]["x"]])
        histos[name].GetYaxis().SetTitle(labels[plots[name]["y"]] + " [%s]" % units[plots[name]["y"]])
        histos[name].GetZaxis().SetTitle("Expected event yield") # yield
        histos[name].SetMinimum(0) # yield
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
            print("DSID {}: x: {}, y: {}, weight: {}, ({}, {})".format(dsid, xBin, yBin, weight, xValue, yValue))
            if (histos[name].GetBinContent(histos[name].FindBin(xBin, yBin))):
                print("Bin already has content: (%d, %d): %f - will now exit!" % (xBin, yBin, histos[name].GetBinContent(histos[name].FindBin(xBin, yBin))))
                sys.exit(1)
            histos[name].Fill(xBin, yBin, nPassed)

        histos[name].Smooth()
        histos[name].DrawCopy("colz")
        histos[name].SetContour(1, array('d', [3]))
        histos[name].Draw("cont3 same")
        
        ATLASLabel(0.179083, 0.991579, alabel)
        latexLabel.DrawLatex(0.25, 0.075, plots[name]["label"])
        canvases[name].Update()
        canvases[name].Print("{}/{}.pdf".format(directory, name))

        outFile.cd()
        histos[name].Write()
