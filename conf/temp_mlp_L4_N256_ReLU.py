import torch
from ramses.red_pt import ModPT, lotesPT, calcDimIni, calcDimSal
from ramses.mlp import mlp_N
dirPrm='Prm/mfcc_optimo'
dirMar='Sen'
ficLisUni='Lis/vocales.lis'
guiTrain='Gui/train.gui'
guiDevel='Gui/devel.gui'
# Generación de lotes
lotesEnt = lotesPT(dirPrm, dirMar, ficLisUni, guiTrain)
lotesDev = lotesPT(dirPrm, dirMar, ficLisUni, guiDevel)
