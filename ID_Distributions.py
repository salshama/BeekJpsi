#Importing useful packages

import ROOT
import numpy as np
import itertools
import os.path
import sys
import argparse
import BeekFunctions

parser = argparse.ArgumentParser(description="make plots")
parser.add_argument("-f","--OutputFolder",type=str,action='store', default = "",help="fill in")
parser.add_argument("-n","--OutputName",type=str,action='store', default = "", help="fill in")
parser.add_argument("-i","--InputFiles",type=str,action='store', default="mc21", choices=['mc20','mc21'],help="fill in")

#too many things need to be changed along with this, leave out for now
#parser.add_argument("-t","--ThresholdNames",type=str,action='store', nargs="+", default=[],help="fill in")

args = parser.parse_args()

#ATLAS plotting style
ROOT.gROOT.LoadMacro("/eos/user/h/hrussell/Bphys_Data/AtlasStyle/AtlasStyle.C")
ROOT.gROOT.LoadMacro("/eos/user/h/hrussell/Bphys_Data/AtlasStyle/AtlasLabels.C")

ROOT.SetAtlasStyle()

ROOT.gStyle.SetErrorX(0.5)

#Tells root not to open canvases to screen
ROOT.gROOT.SetBatch(True)

#Reading the file using ROOT
beekj = None
beeke = None

if args.InputFiles == "mc20":

    beekj = ROOT.TFile.Open('/eos/user/h/hrussell/Bphys_Data/synced_files/valid1.300592.Bd_Kstar_Kpi_Jpsi_e4e4.r13670.beek_v8.root')
    beeke = ROOT.TFile.Open('/eos/user/h/hrussell/Bphys_Data/synced_files/valid1.300590.Bd_Kstar_Kpi_e4e4.r13670.beek_v8.root')
    
elif args.InputFiles == "mc21":

    beekj = ROOT.TFile.Open('/eos/user/h/hrussell/Bphys_Data/synced_files/mc21_13p6TeV.801874.Bd_Kstar_Kpi_Jpsi_e4e4.r14016.beek_v8.root')
    beeke = ROOT.TFile.Open('/eos/user/h/hrussell/Bphys_Data/synced_files/mc21_13p6TeV.801872.Bd_Kstar_Kpi_e4e4.r14016.beek_v8.root')

else:

    print("no files yet for",args.InputFiles)
    
mybeekj = beekj.Get("trig")
mybeeke = beeke.Get("trig")

print('There are ',mybeekj.GetEntries(),'events in J/psi Kstar')

output_dir = '/eos/user/s/salshama/BeekJpsi/Fall_Plots/'

if args.OutputFolder != '':
    output_dir = args.OutputFolder
#output_dir = '/eos/user/h/hrussell/Bphys_Data/AnalysisResults/run3L1/'

print('Putting plots into this directory:',output_dir)

plot_tag = args.OutputName

#Creating a TCanvas object
c1 = ROOT.TCanvas("c1","c1",800,600)

BeekFunctions.plot_reta(mybeekj,'mybeekj')
BeekFunctions.plot_reta(mybeeke,'mybeeke')