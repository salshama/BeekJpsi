#Importing useful packages

import ROOT
import numpy as np
import vector
import sys
import BeekFunctions

#ATLAS plotting style

ROOT.gROOT.LoadMacro("/eos/user/h/hrussell/Bphys_Data/AtlasStyle/AtlasStyle.C")
ROOT.gROOT.LoadMacro("/eos/user/h/hrussell/Bphys_Data/AtlasStyle/AtlasLabels.C")
ROOT.SetAtlasStyle()
def myText( x, y,text, color=ROOT.kBlack,size=None):
  # //Double_t tsize=0.05;
    l = ROOT.TLatex()
    #others.append(l)
    l.SetNDC();
    l.SetTextColor(color);
    if size:
        l.SetTextSize(size)
    l.DrawLatex(x,y,text);
ROOT.gStyle.SetErrorX(0.5)

ROOT.gROOT.SetBatch(True) #tells root not to open canvases to screen

#Reading the file using ROOT
beekj = ROOT.TFile.Open('/eos/user/h/hrussell/Bphys_Data/synced_files/valid1.300592.Bd_Kstar_Kpi_Jpsi_e4e4.r13670.beek_v8.root')

beeke = ROOT.TFile.Open('/eos/user/h/hrussell/Bphys_Data/synced_files/valid1.300590.Bd_Kstar_Kpi_e4e4.r13670.beek_v8.root')

#Getting trees from file using ROOT
mybeekj = beekj.Get("trig")
mybeeke = beeke.Get("trig")

print('There are ',mybeekj.GetEntries(),'entries in BJpsiKstar')

#Creating a TCanvas object
c1 = ROOT.TCanvas("c1","c1",800,600)

# Kinematics plots for electrons with fiducial requirements with reco object that is truth-matched

hist_leading_pTj    = ROOT.TH1D('Leading Electron pT','Kinematics Plots',100,0,20)

hist_leading_pTj.GetXaxis().SetTitle('Truth-matched electron leading p_{T} [GeV]')
hist_leading_pTj.GetYaxis().SetTitle('Events')

hist_subleading_pTj = ROOT.TH1D('Subleading Electron pT','Kinematics Plots',100,0,20)

hist_subleading_pTj.GetXaxis().SetTitle('Truth-matched electron sub-leading p_{T} [GeV]')
hist_subleading_pTj.GetYaxis().SetTitle('Events')

hist_reco_eedRj     = ROOT.TH1D('Reco Dielectron dR','Kinematics Plots',100,0,1)

hist_reco_eedRj.GetXaxis().SetTitle('Reco Dielectron #Delta R')
hist_reco_eedRj.GetYaxis().SetTitle('Events')

hist_invariantmassj = ROOT.TH1D('Dielectron Invariant Mass','Kinematics Plot',100,0,10)

hist_invariantmassj.GetXaxis().SetTitle('Truth-matched Dielectron Mass [GeV]')
hist_invariantmassj.GetYaxis().SetTitle('Events')

hist_leading_pTe    = ROOT.TH1D('Leading Electron pT Nonres','Kinematics Plots',100,0,20)

hist_subleading_pTe = ROOT.TH1D('Subleading Electron pT Nonres','Kinematics Plots',100,0,20)

hist_reco_eedRe     = ROOT.TH1D('Reco Dielectron dR Nonres','Kinematics Plots',100,0,1)

hist_invariantmasse = ROOT.TH1D('Dielectron Invariant Mass Nonres','Kinematics Plot',100,0,10)

#Filling histograms

for event in enumerate(mybeekj):

	if mybeekj.true_eemass[0] > 0 and mybeekj.true_eedR[0] > 0 and \
	mybeekj.true_ept1[0] > 4500 and abs(mybeekj.true_eeta1[0]) < 2.5 and \
    mybeekj.true_ept2[0] > 4500 and abs(mybeekj.true_eeta2[0]) < 2.5 and \
    mybeekj.true_hadpt1[0] > 1000 and abs(mybeekj.true_hadeta1[0]) < 2.5 and \
    mybeekj.true_hadpt2[0] > 1000 and abs(mybeekj.true_hadeta2[0]) < 2.5 and \
    mybeekj.eemass_tm > -1 and mybeekj.eedR_tm > 0.1:
    
		#e1j = mybeekj.recoelectrons[0]
		#e2j = mybeekj.recoelectrons[1]
    	
		#reco_eemassj = (e1j+e2j).M()
	
		#reco_eedRj = e1j.DeltaR(e2j)
	
		#leading_pTj = e1j.Pt()
		#subleading_pTj = e2j.Pt()
	
		#continue
	
		hist_leading_pTj.Fill(mybeekj.eept1_tm*0.001) #Changing from MeV to GeV
		hist_subleading_pTj.Fill(mybeekj.eept2_tm*0.001)
		hist_invariantmassj.Fill(mybeekj.eemass_tm*0.001)
		hist_reco_eedRj.Fill(mybeekj.eedR_tm)
    
for event in enumerate(mybeeke):

	if mybeeke.true_eemass[0] > 0 and mybeeke.true_eedR[0] > 0 and \
    mybeeke.true_ept1[0] > 4500 and abs(mybeeke.true_eeta1[0]) < 2.5 and \
    mybeeke.true_ept2[0] > 4500 and abs(mybeeke.true_eeta2[0]) < 2.5 and \
    mybeeke.true_hadpt1[0] > 1000 and abs(mybeeke.true_hadeta1[0]) < 2.5 and \
    mybeeke.true_hadpt2[0] > 1000 and abs(mybeeke.true_hadeta2[0]) < 2.5 and \
    mybeeke.eemass_tm > -1 and mybeeke.eedR_tm > 0.1:
    
		#e1e = mybeeke.recoelectrons[0]
		#e2e = mybeeke.recoelectrons[1]
	
		#reco_eemasse   = (e1e+e2e).M()
	
		#reco_eedRe     = e1e.DeltaR(e2e)
	
		#leading_pTe    = e1e.Pt()
		#subleading_pTe = e2e.Pt()
		
		#continue
		
		hist_leading_pTe.Fill(mybeeke.eept1_tm*0.001) #Leading electron pT
		hist_subleading_pTe.Fill(mybeeke.eept2_tm*0.001) #Subleading electron pT
		hist_invariantmasse.Fill(mybeeke.eemass_tm*0.001) #Invariant mass
		hist_reco_eedRe.Fill(mybeeke.eedR_tm) #dR

#ATLAS legend style

c1.cd()

leg_kinematics = ROOT.TLegend(0.7,0.75,0.9,0.88)

leg_kinematics.SetBorderSize(0)
leg_kinematics.SetFillStyle(0)

leg_kinematics.AddEntry(hist_invariantmassj,"Resonant","f")
leg_kinematics.AddEntry(hist_invariantmasse,"Nonresonant","f")

#ATLAS filling style

hist_invariantmassj.SetLineColorAlpha(ROOT.kBlue,0.35)
hist_invariantmassj.SetFillColorAlpha(ROOT.kBlue,0.35)


hist_invariantmasse.SetLineColorAlpha(ROOT.kViolet,0.35)
hist_invariantmasse.SetFillColorAlpha(ROOT.kViolet,0.35)


hist_leading_pTj.SetLineColorAlpha(ROOT.kBlue,0.35)
hist_leading_pTj.SetFillColorAlpha(ROOT.kBlue,0.35)


hist_leading_pTe.SetLineColorAlpha(ROOT.kViolet,0.35)
hist_leading_pTe.SetFillColorAlpha(ROOT.kViolet,0.35)

hist_subleading_pTj.SetLineColorAlpha(ROOT.kBlue,0.35)
hist_subleading_pTj.SetFillColorAlpha(ROOT.kBlue,0.35)

hist_subleading_pTe.SetLineColorAlpha(ROOT.kViolet,0.35)
hist_subleading_pTe.SetFillColorAlpha(ROOT.kViolet,0.35)

hist_reco_eedRj.SetLineColorAlpha(ROOT.kBlue,0.35)
hist_reco_eedRj.SetFillColorAlpha(ROOT.kBlue,0.35)

hist_reco_eedRe.SetLineColorAlpha(ROOT.kViolet,0.35)
hist_reco_eedRe.SetFillColorAlpha(ROOT.kViolet,0.35)

#Drawing histograms

hist_invariantmassj.Draw()

hist_invariantmassj.SetMinimum(0)
hist_invariantmassj.SetMaximum(400)

hist_invariantmasse.Draw('same')

leg_kinematics.Draw('same')
ROOT.ATLASLabel(0.18,0.88,"Internal Simulation, ",ROOT.kBlack)
myText(0.18,0.81,"#sqrt{s} = 13 TeV")
#c1.Draw()
c1.Print("/eos/user/s/salshama/BeekJpsi/Fall_Plots/Kinematics_Plots_ResoAndNonreso_invmass.pdf")

hist_leading_pTj.Draw('')

hist_leading_pTj.SetMinimum(0)
hist_leading_pTj.SetMaximum(200)

hist_leading_pTe.Draw('same')

leg_kinematics.Draw('same')
ROOT.ATLASLabel(0.18,0.88,"Internal Simulation, ",ROOT.kBlack)
myText(0.18,0.81,"#sqrt{s} = 13 TeV")
#c1.Draw()
c1.Print("/eos/user/s/salshama/BeekJpsi/Fall_Plots/Kinematics_Plots_ResoAndNonreso_leadpt.pdf")

hist_subleading_pTj.Draw('')

hist_subleading_pTj.SetMinimum(0)
hist_subleading_pTj.SetMaximum(200)

hist_subleading_pTe.Draw('same')

leg_kinematics.Draw('same')
ROOT.ATLASLabel(0.18,0.88,"Internal Simulation, ",ROOT.kBlack)
myText(0.18,0.81,"#sqrt{s} = 13 TeV")
#c1.Draw()
c1.Print("/eos/user/s/salshama/BeekJpsi/Fall_Plots/Kinematics_Plots_ResoAndNonreso_subleadpt.pdf")

hist_reco_eedRj.Draw('')

hist_reco_eedRj.SetMinimum(0)
hist_reco_eedRj.SetMaximum(250)

hist_reco_eedRe.Draw('same')

leg_kinematics.Draw('same')
ROOT.ATLASLabel(0.18,0.88,"Internal Simulation, ",ROOT.kBlack)
myText(0.18,0.81,"#sqrt{s} = 13 TeV")
#c1.Draw()
c1.Print("/eos/user/s/salshama/BeekJpsi/Fall_Plots/Kinematics_Plots_ResoAndNonreso_dR.pdf")