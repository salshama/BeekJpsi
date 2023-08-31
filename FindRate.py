import ROOT
import itertools
import os.path
import sys

data_file = "data18_EB_v8_Run3BeekStudy"

my_folder = "/eos/user/h/hrussell/Bphys_Data/synced_files/"

f = ROOT.TFile.Open(my_folder+data_file+".root", "read")
t = f.Get("trig")

t.AddFriend("trig",my_folder+data_file+"_EBweights.root")

print(t.GetEntries(),' events in sample')

em26_weight = 0

em_weight   = 0

for ie,event in enumerate(t):

   if(ie % 10000 == 0): print('event: ',ie)
    
   if event.L1_eEM26M == 1:
      em_weight += event.EBweight
      
   if event.L1_EM24VHI == 1:
       em26_weight += event.EBweight

print(em_weight)

norm_factor = 21.3/ em26_weight

print(em_weight * norm_factor)