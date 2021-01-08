import os
import math
import ROOT as r
from getParams import *
import json
from array import array

## AM's own version
import sys
#sys.path.append("/Users/amizukam/DVJets/atlasstyle")
sys.path.append("/Users/atsushi/mvstudy_dv")
from AtlasStyle import *
from AtlasLabel import *
SetAtlasStyle()
label = "Work in Progress"

r.gROOT.SetBatch()

binLabels = ["Initial", "pass trig", "pass DRAW", "pass Baseline", "DV < 300 mm", "DV > 4 mm from PV", "chisq < 5", "material veto", "strict material veto", "DV nTrk >= 5", "mDV > 10 GeV"]
cutflow = r.TH1D("cutflow", "cutflow", 11, 0, 11)
h_div = r.TH1D("h_div", "h_div", 11, 0, 11)
for i, name in enumerate(binLabels):
    cutflow.GetXaxis().SetBinLabel(i+1, name)
    h_div.GetXaxis().SetBinLabel(i+1, name)

#filepath = "/Volumes/LaCie/DVJets/mc/signal/mc16d/"
filepath = "/Users/atsushi/DVJets/"
inputFile = "test.txt"

infiles = open(inputFile)
files = infiles.readlines()

lumiInPb = 136000.0
xsFile = open("data/13TeV_gluglu_NNLO_NNLL.json")
xSecs = json.load(xsFile)

c = r.TCanvas("c", "c", 800, 600)

def getNumber(cut):
    tree.Draw(">>elist", cut)
    elist = r.gDirectory.Get("elist")
    nPassed = elist.GetN()
    return nPassed

for filename in files:
    filename = filename.replace("\n", "")
    infile = r.TFile(filepath + filename, "READ")
    tree = infile.Get("trees_SRDV_")

    suffix = filename.split("/")[-1]
    print(suffix)
    dsid = int(suffix.split(".")[2])
    gluinoMass, chi0Mass, tau = getParameters(dsid)
    outputName = "cutflow_" + str(gluinoMass) + "_" + str(chi0Mass) + "_" + tau

    outputDir = "output2"
    if (not os.path.isdir(outputDir)):
        os.makedirs(outputDir)

    outputFile = r.TFile(outputDir + "/" + outputName + ".root", "RECREATE")
    """
    cut = ""
    initial = getNumber(cut)
    cut += "DRAW_pass_triggerFlags"
    passTrig = getNumber(cut)
    cut += "&&DRAW_pass_DVJETS"
    passDVJETS = getNumber(cut)
    cut += "&&BaselineSel_pass"
    passBaseline = getNumber(cut)
    cut += "&&DV_passFiducialCut"
    passFiducial = getNumber(cut)
    cut += "&&DV_passDistCut"
    passDistCut = getNumber(cut)
    cut += "&&DV_passChiSqCut"
    passChiSqCut = getNumber(cut)
    cut += "&&DV_passMaterialVeto"
    passMaterial = getNumber(cut)
    cut += "&&DV_passMaterialVeto_strict"
    passMaterial_strict = getNumber(cut)
    cut += "&&DV_passNTrkCut"
    passNTrk = getNumber(cut)
    cut += "&&DV_passMassCut"
    passMass = getNumber(cut)

    xSec = xSecs[str(gluinoMass)]["xsInPb"]
    mcWeight = 0

    print(initial, passTrig, passDVJETS, passBaseline, passFiducial, passDistCut, passChiSqCut, passMaterial, passMaterial_strict, passNTrk, passMass)

    cutflow.SetBinContent(1, initial)
    cutflow.SetBinContent(2, passTrig)
    cutflow.SetBinContent(3, passDVJETS)
    cutflow.SetBinContent(4, passBaseline)
    cutflow.SetBinContent(5, passFiducial)
    cutflow.SetBinContent(6, passDistCut)
    cutflow.SetBinContent(7, passChiSqCut)
    cutflow.SetBinContent(8, passMaterial)
    cutflow.SetBinContent(9, passMaterial_strict)
    cutflow.SetBinContent(10, passNTrk)
    cutflow.SetBinContent(11, passMass)
    
    cutflow.Draw("hist text")
    c.Print("Cutflow2/{}.pdf".format(outputName))
    """
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
        weight = (mcWeight/sumOfWeights) * xSec * lumiInPb
        
        cutflow.Fill(0, weight)
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
    c.Print("Cutflow2/{}.pdf".format(outputName))
    
    outputFile.Write()
    outputFile.Close()
