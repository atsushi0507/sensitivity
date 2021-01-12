import os
import math
import ROOT as r
from getParams import *
import json
from array import array

## AM's own version
import sys
sys.path.append("/Users/amizukam/DVJets/atlasstyle")
#sys.path.append("/Users/atsushi/mvstudy_dv")
from AtlasStyle import *
from AtlasLabel import *
SetAtlasStyle()
label = "Work in Progress"

r.gROOT.SetBatch()

binLabels = ["Initial", "pass trig", "pass DRAW", "pass Baseline", "DV < 300 mm", "DV > 4 mm from PV", "chisq < 5", "material veto", "strict material veto", "DV nTrk >= 5", "mDV > 10 GeV"]
cutflow = r.TH1D("cutflow", "cutflow", 11, 0, 11)
h_div = r.TH1D("h_div", "h_div", 11, 0, 11)
cutflow.Sumw2()
h_div.Sumw2()
for i, name in enumerate(binLabels):
    cutflow.GetXaxis().SetBinLabel(i+1, name)
    h_div.GetXaxis().SetBinLabel(i+1, name)

filepath = "/Volumes/LaCie/DVJets/mc/signal/mc16d/"
#filepath = "/Users/atsushi/DVJets/"
inputFile = "data/mc16d.txt"
#inputFile = "test.txt"

infiles = open(inputFile)
files = infiles.readlines()

lumiInPb = 136.0 * 0.001
xsFile = open("data/13TeV_gluglu_NNLO_NNLL.json")
xSecs = json.load(xsFile)

outputFile = open("data/count.txt", "w")

c = r.TCanvas("c", "c", 800, 600)
for filename in files:        
    filename = filename.replace("\n", "")
    infile = r.TFile(filepath + filename, "READ")
    tree = infile.Get("trees_SRDV_")

    suffix = filename.split("/")[-1]
    print(suffix)
    dsid = int(suffix.split(".")[2])
    gluinoMass, chi0Mass, tau = getParameters(dsid)
    outputName = "cutflow_" + str(gluinoMass) + "_" + str(chi0Mass) + "_" + tau

    entries = tree.GetEntries()
    sumOfWeights = infile.Get("MetaData_EventCount").GetBinContent(3)
    xSec = xSecs[str(gluinoMass)]["xsInPb"]
    for entry in range(entries):
        ientry = tree.LoadTree(entry)
        if ientry < 0:
            break
        nb = tree.GetEntry(entry)
        if nb <= 0:
            continue

        passFiducial = False
        passDistCut  = False
        passChiSqCut = False
        passMaterial = False
        passMaterial_strict = False
        passNTrk     = False
        passMassCut  = False

        mcWeight = tree.mcEventWeight
        #weight = (mcWeight/sumOfWeights) * xSec * lumiInPb
        weight = mcWeight * xSec * lumiInPb
        cutflow.Fill(0, weight)
        for i in range(len(binLabels)):
            h_div.Fill(i, weight)
        if (not ord(tree.DRAW_pass_triggerFlags)):
            continue
        cutflow.Fill(1, weight)
        if (not ord(tree.DRAW_pass_DVJETS)):
            continue
        cutflow.Fill(2, weight)
        if (not ord(tree.BaselineSel_pass)):
            continue
        cutflow.Fill(3, weight)
        if (tree.DV_n < 1):
            continue
        for idv in range(len(tree.DV_m)):
            if (not tree.DV_passFiducialCut[idv]):
                continue
            else:
                passFiducial = True
            if (not tree.DV_passDistCut[idv]):
                continue
            else:
                passDistCut = True
            if (not tree.DV_passChiSqCut[idv]):
                continue
            else:
                passChiSqCut = True
            if (not tree.DV_passMaterialVeto[idv]):
                continue
            else:
                passMaterial = True
            if (not tree.DV_passMaterialVeto_strict[idv]):
                continue
            else:
                passMaterial_strict = True
            if (not tree.DV_passNTrkCut[idv]):
                continue
            else:
                passNTrk = True
            if (not tree.DV_passMassCut[idv]):
                continue
            else:
                passMassCut = True

        if (not passFiducial):
            continue
        cutflow.Fill(4, weight)
        if (not passDistCut):
            continue
        cutflow.Fill(5, weight)
        if (not passChiSqCut):
            continue
        cutflow.Fill(6, weight)
        if (not passMaterial):
            continue
        cutflow.Fill(7, weight)
        if (not passMaterial_strict):
            continue
        cutflow.Fill(8, weight)
        if (not passNTrk):
            continue
        cutflow.Fill(9, weight)
        if (not passMassCut):
            continue
        cutflow.Fill(10, weight)
        
    cutflow.Draw("hist text")
    c.Print("Cutflow/{}.pdf".format(outputName))

    cutflow_norm = cutflow.Clone("cutflow_norm")
    cutflow_norm.GetYaxis().SetRangeUser(0, 1.05)
    cutflow_norm.Divide(h_div)
    cutflow_norm.Draw("hist text")
    c.Print("Cutflow/{}_normalized.pdf".format(outputName))

    N = cutflow.GetBinContent(11)
    initial = cutflow.GetBinContent(1)
    outputFile.write("{} {} {} {} {} {} {}%\n".format(dsid, str(gluinoMass), str(chi0Mass), str(tau), initial, N, (N/initial)*100))
    print("{} {} {} {} {} {} {}%".format(dsid, str(gluinoMass), str(chi0Mass), str(tau), initial, N, (N/initial)*100))
