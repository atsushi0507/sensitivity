import ROOT as r
from getParams import *

inputFile = open("data/count.txt", "r")
lines = inputFile.readlines()

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

for line in lines:
    line = line.replace("\n", "")
    dsid, nSG = int(line.split("\t")[0]), float(line.split("\t")[1])
    gluinoMass, chi0Mass, tauStr = getParameters(dsid)
    print(gluinoMass, chi0Mass, tauStr)
    if "p" in tauStr:
        tauStr = tauStr.replace("p", "0.")
    if "ns" in tauStr:
        tauStr = tauStr.replace("ns", "")
    tau = float(tauStr)

    gluinoMassList.add(gluinoMass)
    chi0MassList.add(chi0Mass)
    dMassList.add(gluinoMass-chi0Mass)
    tauList.add(tau)

print(gluinoMassList)
print(chi0MassList)
print(dMassList)
print(tauList)
