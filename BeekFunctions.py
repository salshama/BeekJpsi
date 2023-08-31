#Importing functions to use for later

#Importing useful packages

import ROOT
import itertools
import os.path
import sys
import numpy as np


#Function for using text in plots

def myText( x, y,text, color=ROOT.kBlack,size=None):
  # //Double_t tsize=0.05;
    l = ROOT.TLatex()
    #others.append(l)
    l.SetNDC();
    l.SetTextColor(color);
    if size:
        l.SetTextSize(size)
    l.DrawLatex(x,y,text);
    
output_dir = '/eos/user/s/salshama/BeekJpsi/Fall_Plots/'

#Different combinations of permutations with requirements for None, Loose, Medium, Tight
all_64 = ['NNN', 'NNL', 'NNM', 'NNT', 'NLN', 'NLL', 'NLM', 'NLT', 'NMN', 'NML', 'NMM',\
'NMT', 'NTN', 'NTL', 'NTM', 'NTT', 'LNN', 'LNL', 'LNM', 'LNT', 'LLN', 'LLL', 'LLM',\
'LLT', 'LMN', 'LML', 'LMM', 'LMT', 'LTN', 'LTL', 'LTM', 'LTT', 'MNN', 'MNL', 'MNM',\
'MNT', 'MLN', 'MLL', 'MLM', 'MLT','MMN', 'MML', 'MMM', 'MMT', 'MTN', 'MTL', 'MTM',\
'MTT', 'TNN', 'TNL', 'TNM', 'TNT', 'TLN', 'TLL', 'TLM', 'TLT', 'TMN', 'TML', 'TMM',\
'TMT', 'TTN', 'TTL', 'TTM', 'TTT']

#Creating a class for ROI information

class ROI_Info:

    def __init__(self, energy, energy_threshold):
    
       self.energy_threshold = energy_threshold
       self.energy  = energy
       self.nNoID   = 0
       self.nLoose  = 0
       self.nMedium = 0
       self.nTight  = 0
       self.nThresholds = dict.fromkeys(all_64,0) #rhad, wstot, reta in order
       
    def passes_n_noid(self, n_ROIs):
       if self.nNoID >= n_ROIs: return True
       else: return False
       
    def passes_n_loose(self, n_ROIs):
       if self.nLoose >= n_ROIs: return True
       else: return False
       
    def passes_n_medium(self, n_ROIs):
       if self.nMedium >= n_ROIs: return True
       else: return False
       
    def passes_n_tight(self, n_ROIs):
       if self.nTight >= n_ROIs: return True
       else: return False
       
#Function for creating efficiency dictionary by creating histograms, and storing them all
#into a dictionary. Parameters: name of dictionary, number of bins for histograms,
#min/max limits of x-axis, and the title of the histograms.

def get_eff_hist_dict(th_names, dname, nbins,xmin,xmax,xtitle):

    eff_dicts = []
    for th_name in th_names:
    
        eff_dict = {'num_all': ROOT.TH1D("numerator_all_"+th_name+"_"+dname,"",nbins,xmin,xmax),
                    'den_all': ROOT.TH1D("denominator_all_"+th_name+"_"+dname,"",nbins,xmin,xmax),
                    'num_fid': ROOT.TH1D("numerator_fid_"+th_name+"_"+dname,"",nbins,xmin,xmax),
                    'den_fid': ROOT.TH1D("denominator_fid_"+th_name+"_"+dname,"",nbins,xmin,xmax),
                    'num_fidreco': ROOT.TH1D("numerator_fidreco_"+th_name+"_"+dname,"",nbins,xmin,xmax),
                    'den_fidreco': ROOT.TH1D("denominator_fidreco_"+th_name+"_"+dname,"",nbins,xmin,xmax)}
        
        #Sets x-axis and y-axis labels by looping through the given key and histogram in efficiency dictionary           
        for histkey,hist in eff_dict.items():
            hist.GetXaxis().SetTitle(xtitle)
            hist.GetYaxis().SetTitle('Efficiency')
    
        eff_dicts += [eff_dict]
        
    return eff_dicts
    
#Function for filling the given IDs. Parameters: the needed ROI and rhad, wstot, and reta
#in the given tree

def fill_IDs(ROIs, rhad, wstot, reta):

    ROIs.nNoID += 1
    
    #64 possibilities for 4 thresholds (N,L,M,T) and 3 variables (rhad, wstot, reta)
    
    variables  = [rhad, wstot, reta]
    thresholds = [0,1,2,3]
    th_map     = {'N':0, 'L':1,'M':2,'T':3} #dictionary that maps N->0, L->1, M->2, T->3
    
    #For each key in the dictionary all_64, a variable pass_th is set to True. Given an
    #iterator from 0 to 2, the value of variables corresponding to that index is stored
    #in pass_th which is then compared to th_map at th at that index value. This results
    #in True/False. When pass_th = True is multiplied by true, pass_th = 1 (true), but if
    #pass_th = True is multiplied by false, pass_th = 0 (or false).
    #The if statement will run only when pass_th = True for all variables, then
    #ROIs.nThresholds at the value th will increase by 1.
        
    for th in all_64:
    
        pass_th = True
        
        for iv in range(0,3):
           pass_th *= variables[iv] >= th_map[th[iv]]
           
        if pass_th:
            ROIs.nThresholds[th] += 1

    #If statements to check the given requirements for three variables. If these are
    #satisfied, each of the corresponding ROI will increase by 1.
    
    if rhad >= 1 and wstot >= 1 and reta >= 1: 
        ROIs.nLoose +=1
        
    if rhad >= 2 and wstot >= 2 and reta >= 2: 
        ROIs.nMedium +=1
        
    if rhad >= 3 and wstot >= 3 and reta >= 3: 
        ROIs.nTight +=1

#Creating a function to fill out the ROI information given a specific tree

def fill_ROI_infos(tree):

  ROI_infos = []    
  n_events = tree.GetEntries()
  for i,event in enumerate(tree):
    if (i % 10000 == 0): print('event: ',i,'/',n_events,'=',float(i)/n_events*100.,'%')
    
    #Get the ROI info for 5GeV and 7GeV
    
    ROIs_5GeV = ROI_Info(5,3000)
    ROIs_7GeV = ROI_Info(7,5000)
    
    #This loops through these items in the tree and checks if:
    #the energy is greater than the 5GeV threshold. If yes, it calls the fill_IDs function
    #that was defined above. After that, if the energy is greater than 7GeV, it does the
    #same thing using the 7GeV ROI
    
    for l1em_p4, l1em_rhad_th, l1em_wstot_th, l1em_reta_th in zip(tree.newl1ems,\
    tree.newl1ems_rhad_th, tree.newl1ems_wstot_th, tree.newl1ems_reta_th):

        if int(l1em_p4.Et()) > ROIs_5GeV.energy_threshold:
            #print('   ',l1em_rhad_th,l1em_wstot_th,l1em_reta_th)
            fill_IDs(ROIs_5GeV, l1em_rhad_th,l1em_wstot_th,l1em_reta_th)
            
            if int(l1em_p4.Et()) > ROIs_7GeV.energy_threshold:
                fill_IDs(ROIs_7GeV, l1em_rhad_th,l1em_wstot_th,l1em_reta_th)
                
    #Stores the ROI info in a list and returns that list
                
    ROI_infos +=[(ROIs_5GeV, ROIs_7GeV)]
     
  return ROI_infos

#Function that sets the triggers to either true or false. Parameters: dictionary of
#efficiencies, pass_th, pass_fidreco, and variable in tree (either mass or dR).

def fill_threshold(eff_dict, pass_th, pass_fid, pass_fidreco, eevar):

    eff_dict['den_all'].Fill(eevar)
    
    if pass_fid:
        eff_dict['den_fid'].Fill(eevar)
    
        if pass_fidreco:
            eff_dict['den_fidreco'].Fill(eevar)
    
    if pass_th:
        eff_dict['num_all'].Fill(eevar)
        
        if pass_fid:
            eff_dict['num_fid'].Fill(eevar)
        
            if pass_fidreco:
                eff_dict['num_fidreco'].Fill(eevar)
                
#Function to calculate thresholds. Parameters: th_list and ROIs. Starts with an empty list
#pass_list and for every item in list th_list, if certain conditions are met
#(such as name in th_list and ROIs), then the value of true is added to pass_list
  
def calc_thresholds(th_list,ROIs):

    pass_list = []
    
    for th in th_list:
    
        if th == '2eEM5L':
             if ROIs[0].nLoose >= 2: pass_list += [True]
             else: pass_list += [False]
             
        if th == '2eEM5M':
            if ROIs[0].nMedium >= 2: pass_list += [True]
            else: pass_list += [False]
        
        if th == '2eEM5T':
            if ROIs[0].nTight >= 3: pass_list += [True]
            else: pass_list += [False]
             
        if th == '2eEM5':  
            if ROIs[0].nNoID  >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == 'eEM7_2eEM5':  
            if ROIs[0].nNoID  >= 2 and ROIs[0].nNoID >= 1: pass_list += [True]
            else: pass_list += [False]
              
        if th == 'eEM7_2eEM5_LNN_LNN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['LNN'] >= 2 and ROIs[1].nThresholds['LNN'] >= 1:\
            pass_list       += [True]
            else: pass_list += [False]
        
        if th == 'eEM7_2eEM5_NLN_NLN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['NLN'] >= 2 and ROIs[1].nThresholds['NLN'] >= 1:\
            pass_list       += [True]
            else: pass_list += [False]
        
        if th == 'eEM7_2eEM5_NNL_NNL':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['NNL'] >= 2 and ROIs[1].nThresholds['NNL'] >= 1:\
            pass_list       += [True]
            else: pass_list += [False]
            
        if th == 'eEM7_2eEM5_TNN_TNN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['TNN'] >= 2 and ROIs[1].nThresholds['TNN'] >= 1:\
            pass_list       += [True]
            else: pass_list += [False]
            
        if th == 'eEM7_2eEM5_TTN_LLN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['TTN'] >= 1 and ROIs[0].nThresholds['LLN'] >= 2 and\
            ROIs[1].nThresholds['LLN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == 'eEM7_2eEM5_TTN_MMN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['TTN'] >= 1 and ROIs[0].nThresholds['MMN'] >= 2 and\
            ROIs[1].nThresholds['MMN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == 'eEM7_2eEM5_MMN_LLN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['MMN'] >= 1 and ROIs[0].nThresholds['LLN'] >= 2 and\
            ROIs[1].nThresholds['LLN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == 'eEM7_2eEM5_TTN_NNN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['TTN'] >= 1 and ROIs[0].nThresholds['NNN'] >= 2 and\
            ROIs[1].nThresholds['NNN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == 'eEM7_2eEM5_MMN_MMN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['MMN'] >= 2 and ROIs[1].nThresholds['MMN'] >= 1:
                pass_list += [True]
            else: pass_list += [False]
            
        if th == 'eEM7_2eEM5_TTN_TTN':
        
            if ROIs[1].nNoID >= 1 and ROIs[0].nNoID >= 2 and\
            ROIs[0].nThresholds['TTN'] >= 2 and ROIs[1].nThresholds['TTN'] >= 1:
                pass_list += [True]
            else: pass_list += [False]
        
        if th == '2eEM5_LNN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['LNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_NLN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['NLN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_NNL':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['NNL'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_TTN_MMN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['TTN'] >= 1 and ROIs[0].nThresholds['MMN'] >= 2:
                pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5L_LNN':
            if ROIs[0].nLoose >= 2 and ROIs[0].nThresholds['LNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5L_NLN':
            if ROIs[0].nLoose >= 2 and ROIs[0].nThresholds['NLN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5L_NNL':
            if ROIs[0].nLoose >= 2 and ROIs[0].nThresholds['NNL'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5M_LNN':
            if ROIs[0].nMedium >= 2 and ROIs[0].nThresholds['LNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5M_NLN':
            if ROIs[0].nMedium >= 2 and ROIs[0].nThresholds['NLN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5M_NNL':
            if ROIs[0].nMedium >= 2 and ROIs[0].nThresholds['NNL'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5T_LNN':
            if ROIs[0].nTight >= 3 and ROIs[0].nThresholds['LNN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5T_NLN':
            if ROIs[0].nTight >= 3 and ROIs[0].nThresholds['NLN'] >= 1: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_LNN_LNN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['LNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_MNN_MNN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['MNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_MMN_MMN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['MMN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_TNN_TNN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['TNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_NLN_NLN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['NLN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_NNL_NNL':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['NNL'] >= 2: pass_list += [True]
            else: pass_list += [False]

        if th == '2eEM7_LNN_LNN':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['LNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7_MNN_MNN':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['MNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7_MMN_MMN':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['MMN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7_TNN_TNN':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['TNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7_NLN_NLN':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['NLN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7_LLN_LLN':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['LNN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7_NNL_NNL':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['NNL'] >= 2: pass_list += [True]
            else: pass_list += [False]
             
        if th == '2eEM5_NLL_NNN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['NLL'] >= 1: pass_list += [True]
            else: pass_list += [False]
             
        if th == '2eEM5T_NNL':
            if ROIs[0].nTight >= 3 and ROIs[0].nThresholds['NNL'] >= 1: pass_list += [True]
            else: pass_list += [False]
                                   
        if th == '2eEM5_NLL_NLL':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['NLL'] >= 2: pass_list += [True]
            else: pass_list += [False]
        
        if th == '2eEM5_TTN_TTN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['TTN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM5_TTN_LLN':
            if ROIs[0].nNoID >= 2 and ROIs[0].nThresholds['TTN'] >= 1 and\
            ROIs[0].nThresholds['LLN'] >= 1:\
            pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7_TTN_TTN':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['TTN'] >= 2: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7_TTN_LLN':
            if ROIs[1].nNoID >= 2 and ROIs[1].nThresholds['TTN'] >= 1 and\
            ROIs[1].nThresholds['LLN'] >= 1:\
            pass_list       += [True]
            else: pass_list += [False]
            
        if th == '2eEM7L':
             if ROIs[1].nLoose >= 2: pass_list += [True]
             else: pass_list += [False]
             
        if th == '2eEM7M':
            if ROIs[1].nMedium >= 2: pass_list += [True]
            else: pass_list += [False]
        
        if th == '2eEM7T':
            if ROIs[1].nTight >= 3: pass_list += [True]
            else: pass_list += [False]
            
        if th == '2eEM7':
            if ROIs[1].nNoID >= 2: pass_list += [True]
            else: pass_list += [False]
                    
    if len(th_list) != len(pass_list):
    
        print('calc_thresholds mismatch between number of requested thresholds and the output pass_list - revisit function')
        
        print('for calc_thresholds, len(th_list) = ',len(th_list),' and len(pass_list)=',len(pass_list))
        print('threshold list: ',th_list)
        
        #Customized error message. Just because the code is right, that does not mean it "is" right.
        raise Exception('Fix calc_thresholds!')
        
    return pass_list

#Function for filling histograms with the threshold requirements, the efficiency dictionary
#calculated earlier (one for mass and one for dR), the ROI info and the given tree

def fill_hists(th_names, eff_dicts_mass, eff_dicts_dR, ROI_info, tree):

    for ievt,(event,ROIs) in enumerate(zip(tree,ROI_info)):
        
        #This list takes in a function and calculates the passed thresholds
        pass_thresholds_list = calc_thresholds(th_names,ROIs)
        
        #could do sometihng with regex https://regex101.com
        #e.g. [1-9]eEM[1-9]([N|L|M|T])?(_[N|L|M|T][N|L|M|T][N|L|M|T])?$
                 
        pass_fid     = False
        pass_fidreco = False 
            
        ##FIDUCIAL REQUIREMENTS
        
        if tree.true_eemass[0] > 0 and tree.true_eedR[0] > 0 and \
         tree.true_ept1[0] > 4500 and abs(tree.true_eeta1[0]) < 2.5 and \
         tree.true_ept2[0] > 4500 and abs(tree.true_eeta2[0]) < 2.5 and \
         tree.true_hadpt1[0] > 1000 and abs(tree.true_hadeta1[0]) < 2.5 and \
         tree.true_hadpt2[0] > 1000 and abs(tree.true_hadeta2[0]) < 2.5:
         
          pass_fid = True
         
          #FIDRECO REQUIREMENTS
         
          if tree.eemass_tm > -1 and tree.eedR_tm > 0.1:
          
            pass_fidreco = True 

        for ith,(th_name,pass_threshold) in enumerate(zip(th_names,pass_thresholds_list)):
        
            fill_threshold(eff_dicts_mass[ith], pass_threshold, pass_fid, pass_fidreco, tree.true_eemass[0]*0.001)
            fill_threshold(eff_dicts_dR[ith], pass_threshold, pass_fid, pass_fidreco, tree.true_eedR[0])
                        
            #if ievt < 2: 
            
                #print('threshold:', th_name,' being filled, does it pass?',pass_threshold)

#Function for drawing and displaying histograms

def display_hists_oneTrigger(c1, eff_dict, output_tag, plot_tag):

    #Adding color to differentiate between efficiencies

    #print("Test efficiency? ",eff_dict['eff_all'].GetEfficiency(30))

    eff_dict['eff_all'].SetLineColor(ROOT.kRed)
    eff_dict['eff_all'].SetLineStyle(6)
    eff_dict['eff_all'].SetMarkerStyle(32)
    eff_dict['eff_all'].SetMarkerColor(ROOT.kRed)

    eff_dict['eff_fid'].SetLineColor(ROOT.kBlue)
    eff_dict['eff_fid'].SetLineStyle(7)
    eff_dict['eff_fid'].SetMarkerStyle(26)
    eff_dict['eff_fid'].SetMarkerColor(ROOT.kBlue)

    eff_dict['eff_fidreco'].SetLineColor(ROOT.kViolet)
    eff_dict['eff_fidreco'].SetLineStyle(4)
    eff_dict['eff_fidreco'].SetMarkerStyle(25)
    eff_dict['eff_fidreco'].SetMarkerColor(ROOT.kViolet)

    #Drawing the efficiencies 

    eff_dict['eff_all'].Draw()

    ROOT.gPad.Update()
    resograph = eff_dict['eff_all'].GetPaintedGraph()
    resograph.SetMinimum(0)
    resograph.SetMaximum(1.4) 
    ROOT.gPad.Update()

    eff_dict['eff_fid'].Draw('same')
    eff_dict['eff_fidreco'].Draw('same')
    
    #ATLAS legend style

    leg = ROOT.TLegend(0.7,0.75,0.9,0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(eff_dict['eff_all'],"All","lp")
    leg.AddEntry(eff_dict['eff_fid'],"Fiducial","lp")
    leg.AddEntry(eff_dict['eff_fidreco'],"Fiducial + Reco","lp")
    
    leg.Draw('same')

    ROOT.ATLASLabel(0.18,0.88,"Internal Simulation, ",ROOT.kBlack)
    
    if 'nonres' in output_tag:
        myText(0.18,0.81,"#sqrt{s} = 13 TeV, e+e- (nonresonant)")
        
    elif 'res' in output_tag:
        myText(0.18,0.81,"#sqrt{s} = 13 TeV, J/#psi #rightarrow e+e- (resonant)")
        
    else:
        myText(0.18,0.81,"#sqrt{s} = 13 TeV")
        
    c1.Draw()
    c1.Print(output_dir+"Effs_AllFidFidReco_"+output_tag+"_"+plot_tag+".pdf")

def display_hists_oneSelection(c1, eff_dicts, legend_labels, selection_tag, output_tag, plot_tag):

    #Adding color to differentiate between efficiencies

    #print("Test efficiency? ",eff_dict['eff_all'].GetEfficiency(30))
    
    colours = [ROOT.kRed-4, ROOT.kBlue+2, ROOT.kViolet+1, ROOT.kGreen-2, ROOT.kCyan-3, ROOT.kOrange-7]
    markers = [32,20,25,26,27,28]
    
    #ATLAS legend style
    leg = ROOT.TLegend(0.5,0.75,0.9,0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    for idict, eff_dict in enumerate(eff_dicts):
    
        eff_dict['eff_'+selection_tag].SetLineColor(colours[idict])
        eff_dict['eff_'+selection_tag].SetMarkerStyle(markers[idict])
        eff_dict['eff_'+selection_tag].SetMarkerColor(colours[idict])
        
        leg.AddEntry(eff_dict['eff_'+selection_tag],legend_labels[idict],"lp")

        #Drawing the efficiencies
        
        if idict == 0:

            eff_dict['eff_'+selection_tag].Draw()

            ROOT.gPad.Update()
            resograph = eff_dict['eff_'+selection_tag].GetPaintedGraph()
            resograph.SetMinimum(0)
            resograph.SetMaximum(1.4) 
            ROOT.gPad.Update()
            
        else:
            eff_dict['eff_'+selection_tag].Draw('same')
            eff_dict['eff_'+selection_tag].Draw('same')
        
    leg.Draw('same')

    ROOT.ATLASLabel(0.18,0.88,"Internal Simulation, ",ROOT.kBlack)
    
    if 'nonres' in output_tag:
        myText(0.18,0.81,"#sqrt{s} = 13 TeV, e+e- (nonresonant)")
        
    elif 'res' in output_tag:
        myText(0.18,0.81,"#sqrt{s} = 13 TeV, J/#psi #rightarrow e+e- (resonant)")
        
    else:
        myText(0.18,0.81,"#sqrt{s} = 13 TeV")  
          
    c1.Draw()
    c1.Print(output_dir+"Effs_fidreco_alltrigs_"+output_tag+"_"+plot_tag+".pdf")

def calc_efficiencies(eff_dicts):

    #num_all --> [num, all] -> all
    
    hist_types = list(set([ key.split("_")[1] for key in eff_dicts[0].keys()]))
    
    for eff_dict in eff_dicts:
    
        for hist_type in hist_types:
        
            eff_dict['eff_'+hist_type] = ROOT.TEfficiency(eff_dict['num_'+hist_type],eff_dict['den_'+hist_type])
            
#Finding rates of emulated triggers

def find_rate(th_names):

    data_file = "data18_EB_v8_Run3BeekStudy"
    my_folder = "/eos/user/h/hrussell/Bphys_Data/synced_files/"

    f = ROOT.TFile.Open(my_folder+data_file+".root", "read")
    t = f.Get("trig")

    t.AddFriend("trig",my_folder+data_file+"_EBweights.root")

    print(t.GetEntries(),' events in sample')

    data_RoI_infos = fill_ROI_infos(t)

    em26_weight  = 0
    em_weights   = [0]*len(th_names)
    
    rates = []

    for ie, event in enumerate(t):
    
        if (ie % 10000 == 0): print('event: ',ie)
        
        pass_thresholds_list = calc_thresholds(th_names,data_RoI_infos[ie])
        
        for ith,pass_th in enumerate(pass_thresholds_list):
        
            if pass_th == True:
            
            #if passes threshold
            
                em_weights[ith] += event.EBweight

        if event.L1_EM24VHI == 1:
        
            em26_weight += event.EBweight
    
    norm_factor = 21.3 / em26_weight
    
    for em_weight in em_weights:
    
        print("The rates are:",rates.append(em_weight * norm_factor))
        
    return rates
    
#Plotting reta vs dR in 2D for leading and sub-leading electrons

def plot_reta(tree,tree_name):

    c1 = ROOT.TCanvas('c1','c1',800,600)

    #Plotting Reta vs dR
    
    leading_electron_reta_dR    = ROOT.TH2D('Leading Electron Reta','Leading Electron Reta',100,0,1,100,0,1)
    subleading_electron_reta_dR = ROOT.TH2D('Subleading Electron Reta','Subleading Electron Reta',100,0,1,100,0,1)
    
    leading_electron_reta_dR.GetXaxis().SetTitle('Reco Dielectron #Delta R')
    leading_electron_reta_dR.GetYaxis().SetTitle('Reta')
    
    subleading_electron_reta_dR.GetXaxis().SetTitle('Reco Dielectron #Delta R')
    subleading_electron_reta_dR.GetYaxis().SetTitle('Reta')
    
    for event in enumerate(tree):
    
        if tree.true_eemass[0] > 0 and tree.true_eedR[0] > 0 and \
        tree.true_ept1[0] > 4500 and abs(tree.true_eeta1[0]) < 2.5 and \
        tree.true_ept2[0] > 4500 and abs(tree.true_eeta2[0]) < 2.5 and \
        tree.true_hadpt1[0] > 1000 and abs(tree.true_hadeta1[0]) < 2.5 and \
        tree.true_hadpt2[0] > 1000 and abs(tree.true_hadeta2[0]) < 2.5 and \
        tree.eemass_tm > -1 and tree.eedR_tm > 0.1 and tree.newl1ems_match_n > 1:
        
            reta1 = 0
            reta2 = 0
            has_leading = False
            
            for l1reta,l1m in zip(tree.newl1ems_reta, tree.newl1ems_match):
            
                if l1m and not has_leading:
                
                   reta1 = l1reta
                   
                elif l1m and has_leading:
                
                   reta2 = l1reta
                   
                   break
        
            leading_electron_reta_dR.Fill(tree.true_eedR[0],reta1)
            subleading_electron_reta_dR.Fill(tree.true_eedR[0],reta2)

    leading_electron_reta_dR.Draw("COLZ")
    
    #ROOT.ATLASLabel(0.18,1.01,"Internal Simulation, ",ROOT.kBlack)
    
    if tree_name == 'mybeeke': myText(0.18,1.01,"#sqrt{s} = 13 TeV, e+e- (nonresonant)")
    
    elif tree_name == 'mybeekj': myText(0.18,1.01,"#sqrt{s} = 13 TeV, J/#psi #rightarrow e+e- (resonant)")
    
    else: myText(0.18,1.01,"#sqrt{s} = 13 TeV")
    
    c1.Draw()
    c1.Print("/eos/user/s/salshama/BeekJpsi/Fall_Plots/Reta_distributions_"+tree_name+".pdf")
    
#Plotting wstot vs dR in 2D for leading and sub-leading electrons

def plot_wstot(tree,tree_name):

    c2 = ROOT.TCanvas('c2','c2',800,600)

    #Plotting wstot vs dR
    
    leading_electron_wstot_dR    = ROOT.TH2D('Leading Electron Wstot','Leading Electron Wstot',100,0,1,100,0,1)
    subleading_electron_wstot_dR = ROOT.TH2D('Subleading Electron Wstot','Subleading Electron Wstot',100,0,1,100,0,1)
    
    leading_electron_wstot_dR.GetXaxis().SetTitle('Reco Dielectron #Delta R')
    leading_electron_wstot_dR.GetYaxis().SetTitle('Wstot')
    
    subleading_electron_wstot_dR.GetXaxis().SetTitle('Reco Dielectron #Delta R')
    subleading_electron_wstot_dR.GetYaxis().SetTitle('Wstot')
    
    for event in enumerate(tree):
    
        if tree.true_eemass[0] > 0 and tree.true_eedR[0] > 0 and \
        tree.true_ept1[0] > 4500 and abs(tree.true_eeta1[0]) < 2.5 and \
        tree.true_ept2[0] > 4500 and abs(tree.true_eeta2[0]) < 2.5 and \
        tree.true_hadpt1[0] > 1000 and abs(tree.true_hadeta1[0]) < 2.5 and \
        tree.true_hadpt2[0] > 1000 and abs(tree.true_hadeta2[0]) < 2.5 and \
        tree.eemass_tm > -1 and tree.eedR_tm > 0.1 and tree.newl1ems_match_n > 1:
        
            wstot1 = 0
            wstot2 = 0
            has_leading = False
            
            for l1wstot,l1m in zip(tree.newl1ems_wstot, tree.newl1ems_match):
            
                if l1m and not has_leading:
                
                   wstot1 = l1wstot
                   
                elif l1m and has_leading:
                
                   wstot2 = l1wstot
                   
                   break
        
            leading_electron_wstot_dR.Fill(tree.true_eedR[0],wstot1)
            subleading_electron_wstot_dR.Fill(tree.true_eedR[0],wstot2)

    leading_electron_wstot_dR.Draw("COLZ")
    
    #ROOT.ATLASLabel(0.18,1.01,"Internal Simulation, ",ROOT.kBlack)
    
    if tree_name == 'mybeeke': myText(0.18,1.01,"#sqrt{s} = 13 TeV, e+e- (nonresonant)")
    
    elif tree_name == 'mybeekj': myText(0.18,1.01,"#sqrt{s} = 13 TeV, J/#psi #rightarrow e+e- (resonant)")
    
    else: myText(0.18,1.01,"#sqrt{s} = 13 TeV")
    
    c2.Draw()
    c2.Print("/eos/user/s/salshama/BeekJpsi/Fall_Plots/Wstot_distributions_"+tree_name+".pdf")
    
#Plotting rhad vs dR in 2D for leading and sub-leading electrons

def plot_rhad(tree,tree_name):

    c3 = ROOT.TCanvas('c3','c3',800,600)

    #Plotting rhad vs dR
    
    leading_electron_rhad_dR    = ROOT.TH2D('Leading Electron Rhad','Leading Electron Rhad',100,0,1,100,0,1)
    subleading_electron_rhad_dR = ROOT.TH2D('Subleading Electron Rhad','Subleading Electron Rhad',100,0,1,100,0,1)
    
    leading_electron_rhad_dR.GetXaxis().SetTitle('Reco Dielectron #Delta R')
    leading_electron_rhad_dR.GetYaxis().SetTitle('Rhad')
    
    subleading_electron_rhad_dR.GetXaxis().SetTitle('Reco Dielectron #Delta R')
    subleading_electron_rhad_dR.GetYaxis().SetTitle('Rhad')
    
    for event in enumerate(tree):
    
        if tree.true_eemass[0] > 0 and tree.true_eedR[0] > 0 and \
        tree.true_ept1[0] > 4500 and abs(tree.true_eeta1[0]) < 2.5 and \
        tree.true_ept2[0] > 4500 and abs(tree.true_eeta2[0]) < 2.5 and \
        tree.true_hadpt1[0] > 1000 and abs(tree.true_hadeta1[0]) < 2.5 and \
        tree.true_hadpt2[0] > 1000 and abs(tree.true_hadeta2[0]) < 2.5 and \
        tree.eemass_tm > -1 and tree.eedR_tm > 0.1 and tree.newl1ems_match_n > 1:
        
            rhad1 = 0
            rhad2 = 0
            has_leading = False
            
            for l1rhad,l1m in zip(tree.newl1ems_rhad, tree.newl1ems_match):
            
                if l1m and not has_leading:
                
                   rhad1 = l1rhad
                   
                elif l1m and has_leading:
                
                   rhad2 = l1rhad
                   
                   break
        
            leading_electron_rhad_dR.Fill(tree.true_eedR[0],rhad1)
            subleading_electron_rhad_dR.Fill(tree.true_eedR[0],rhad2)

    leading_electron_rhad_dR.Draw("COLZ")
    
    #ROOT.ATLASLabel(0.18,1.01,"Internal Simulation, ",ROOT.kBlack)
    
    if tree_name == 'mybeeke': myText(0.18,1.01,"#sqrt{s} = 13 TeV, e+e- (nonresonant)")
    
    elif tree_name == 'mybeekj': myText(0.18,1.01,"#sqrt{s} = 13 TeV, J/#psi #rightarrow e+e- (resonant)")
    
    else: myText(0.18,1.01,"#sqrt{s} = 13 TeV")
    
    c3.Draw()
    c3.Print("/eos/user/s/salshama/BeekJpsi/Fall_Plots/Rhad_distributions_"+tree_name+".pdf")