import os
import ROOT as r
from getParams import *
from array import array

import sys
sys.path.append("/Users/amizukam/DVJets/atlasstyle")
from AtlasStyle import *
from AtlasLabel import *
SetAtlasStyle()
label = "Work in Progress"

r.gROOT.SetBatch()

#binLabels = ["Initial", "pass trig", "pass DRAW", "pass Baseline", "DV < 300 mm", "DV > 4 mm from PV", "chisq < 5", "material veto", "strict material veto", "DV nTrk #geq 5", "mDV > 10 GeV"]
binLabels = ["Initial", "pass trig", "pass DRAW", "pass Baseline", "DV < 300 mm", "DV > 4 mm from PV", "chisq < 5", "material veto", "strict material veto", "pass nTrk & mDV"]

nBins = len(binLabels)
cutflow = r.TH1D("cutflow", "cutflow", nBins, 0, nBins)
for i, name in enumerate(binLabels):
    cutflow.GetXaxis().SetBinLabel(i+1, name)

filepath = "/Volumes/LaCie/DVJets/mc/signal/mc16d/"
inputFile = "data/mc16d.txt"
outputDir = "Cutflow_new"
if (not os.path.isdir(outputDir)):
    os.makedirs(outputDir)

infiles = open(inputFile)
files = infiles.readlines()

canvases = {}
histos = {}

r.gStyle.SetPaintTextFormat(".3f")

outputFile = open("data/count_new.txt", "w")
for filename in files:
    filename = filename.replace("\n", "")
    infile = r.TFile(filepath + filename, "READ")
    tree = infile.Get("trees_SRDV_")

    suffix = filename.split("/")[-1]
    print(suffix)
    dsid = int(suffix.split(".")[2])
    gluinoMass, chi0Mass, tau = getParameters(dsid)
    name = "cutflow_" + str(gluinoMass) + "_" + str(chi0Mass) + "_" + tau

    canvases[dsid] = r.TCanvas(name, name, 800, 600)
    canvases[dsid].SetRightMargin(0.08)
    histos[dsid] = r.TH1D(name, name, nBins, 0, nBins)
    histos[dsid].SetMinimum(0.)
    for i, binLabel in enumerate(binLabels):
        histos[dsid].GetXaxis().SetBinLabel(i+1, binLabel)
        histos[dsid].GetXaxis().SetLabelSize(0.03)
    
    entries = tree.GetEntries()
    sumW = infile.Get("MetaData_EventCount").GetBinContent(3)

    for entry in range(entries):
        ientry = tree.LoadTree(entry)
        if ientry < 0:
            break
        nb = tree.GetEntry(entry)
        if nb <= 0:
            continue

        passFiducial = False
        passDist     = False
        passChiSq    = False
        passMaterial = False
        passMaterial_strict = False
        passSR     = False

        mcWeight = tree.mcEventWeight
        weight = mcWeight/sumW

        histos[dsid].AddBinContent(1, weight)
        if (not ord(tree.DRAW_pass_triggerFlags)):
            continue
        histos[dsid].AddBinContent(2, weight)
        if (not ord(tree.DRAW_pass_DVJETS)):
            continue
        histos[dsid].AddBinContent(3, weight)
        if (not ord(tree.BaselineSel_pass)):
            continue
        histos[dsid].AddBinContent(4, weight)

        for idv in range(len(tree.DV_m)):
            if (not tree.DV_passFiducialCut[idv]):
                continue
            else:
                passFiducial = True
            if (not tree.DV_passDistCut[idv]):
                continue
            else:
                passDist = True
            if (not tree.DV_passChiSqCut[idv]):
                continue
            else:
                passChiSq = True
            if (not tree.DV_passMaterialVeto[idv]):
                continue
            else:
                passMaterial = True
            if (not tree.DV_passMaterialVeto_strict[idv]):
                continue
            else:
                passMaterial_strict = True
            if (not ((tree.DV_nTracks[idv] >= 5 and tree.DV_m[idv] > 10.) or (tree.DV_nTracks[idv] >= 4 and tree.DV_m[idv] > 20.))):
                continue
            else:
                passSR = True


        if (not passFiducial):
            continue
        histos[dsid].AddBinContent(5, weight)
        if (not passDist):
            continue
        histos[dsid].AddBinContent(6, weight)
        if (not passChiSq):
            continue
        histos[dsid].AddBinContent(7, weight)
        if (not passMaterial):
            continue
        histos[dsid].AddBinContent(8, weight)
        if (not passMaterial_strict):
            continue
        histos[dsid].AddBinContent(9, weight)
        if (not passSR):
            continue
        histos[dsid].AddBinContent(10, weight)

    histos[dsid].Draw("hist text")
    canvases[dsid].Print("{}/{}.pdf".format(outputDir, name))

    initial = histos[dsid].GetBinContent(1)
    passed = histos[dsid].GetBinContent(10)
    outputFile.write("{}\t{}\t{}\n".format(dsid, initial, passed))
