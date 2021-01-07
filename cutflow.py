import ROOT as r
import os, glob, sys
sys.path.append("/Users/amizukam/DVJets/atlasstyle/")
from AtlasStyle import *
from AtlasLabel import *
from getParams import *

SetAtlasStyle()
r.gROOT.SetBatch()

filepath = "/Volumes/LaCie/DVJets/mc/signal/mc16d/"
inputFile = "mc16d.txt"

infiles = open(inputFile)
files = infiles.readlines()

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

    outputDir = "output"
    if (not os.path.isdir(outputDir)):
        os.makedirs(outputDir)
    outputFile = r.TFile(outputDir + "/" + outputName + ".root", "RECREATE")

    label = "#font[52]{m_{#tilde{g}}} = " + str(gluinoMass) + " GeV, #font[52]{m}_{#font[152]{#tilde{c}_{1}^{0}}} = " + str(chi0Mass) + ", #font[152]{t} = " + tau.replace("p", "0.")

    nCuts = 11
    binLabels = ["Initial", "pass trig", "pass DRAW", "pass Baseline", "DV < 300 mm", "DV > 4 mm from PV", "chisq < 5", "material veto", "strict material veto", "DV nTrk >= 5", "DV mass > 10 GeV"]
    cutflow = r.TH1D("cuflow", label, nCuts, 0, nCuts)
    h_div = r.TH1D("h_div", label, nCuts, 0, nCuts)
    for i, name in enumerate(binLabels):
        cutflow.GetXaxis().SetBinLabel(i+1, name)
        h_div.GetXaxis().SetBinLabel(i+1, name)

    entries = tree.GetEntries()
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
        passNTrack   = False
        passMassCut  = False

        cutflow.AddBinContent(1)
        for i in range(nCuts):
            h_div.AddBinContent(i+1)

        if (not ord(tree.DRAW_pass_triggerFlags)):
            continue
        cutflow.AddBinContent(2)
        if (not ord(tree.DRAW_pass_DVJETS)):
            continue
        cutflow.AddBinContent(3)
        if (not ord(tree.BaselineSel_pass)):
            continue
        cutflow.AddBinContent(4)

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
                passNTrack = True
            if (not tree.DV_passMassCut[idv]):
                continue
            else:
                passMassCut = True

        if (not passFiducial):
            continue
        cutflow.AddBinContent(5)
        if (not passDistCut):
            continue
        cutflow.AddBinContent(6)
        if (not passChiSqCut):
            continue
        cutflow.AddBinContent(7)
        if (not passMaterial):
            continue
        cutflow.AddBinContent(8)
        if (not passMaterial_strict):
            continue
        cutflow.AddBinContent(9)
        if (not passNTrack):
            continue
        cutflow.AddBinContent(10)
        if (not passMassCut):
            continue
        cutflow.AddBinContent(11)
                                    
    cutflow.Draw("hist text")
    c.Print("Cutflow/{}.pdf".format(outputName))
    cutflow_norm = cutflow.Clone("cutflow_norm")
    cutflow_norm.GetYaxis().SetRangeUser(0, 1.05)
    cutflow_norm.Divide(h_div)
    cutflow_norm.Draw("hist text")
    c.Print("Cutflow/{}_normalized.pdf".format(outputName))

    outputFile.Write()
    outputFile.Close()
