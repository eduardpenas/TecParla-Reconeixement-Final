#!/bin/bash
# SCRIPT FINAL OPTIMIZADO (RAMSES)
# Configuracion Ganadora: MLP 2 capas, 64 neuronas, ReLU, Adam lr=0.0001

# 1. Parametrizacion (Si no existe, se crea)
if [ ! -d "Prm/mfcc_optimo" ]; then
    echo "Generando MFCC..."
    # Aqui iria tu comando de parametrizacion si fuera necesario
    # python3 ramses/parametriza.py ... 
fi

# 2. Configuración Python para entrena.py
cat <<EOT > conf/final_config.py
import torch
from ramses.red_pt import ModPT, lotesPT
from ramses.mlp import mlp_N
dirPrm='Prm/mfcc_optimo'
dirMar='Sen'
ficLisUni='Lis/vocales.lis'
guiTrain='Gui/train.gui'
guiDevel='Gui/devel.gui'
lotesEnt = lotesPT(dirPrm, dirMar, ficLisUni, guiTrain)
lotesDev = lotesPT(dirPrm, dirMar, ficLisUni, guiDevel)
EOT

# 3. Entrenamiento
echo "Entrenando Modelo Final..."
python3 ramses/entrena.py \
    -e 400 \
    --execPrev conf/final_config.py \
    --lotesEnt lotesEnt \
    --lotesDev lotesDev \
    -M "ModPT(ficLisUni='Lis/vocales.lis', red=mlp_N(numCap=2, dimIni=18, dimInt=128, dimSal=5, clsAct=torch.nn.ReLU()), Optim=lambda p: torch.optim.Adam(p, lr=0.0001))" \
    Mod/modelo_final.mod

# 4. Reconocimiento
echo "Reconociendo..."
python3 ramses/reconoce.py \
    -r Rec/final \
    -p Prm/mfcc_optimo \
    -M Mod/modelo_final.mod \
    --classMod ModPT \
    Gui/devel.gui

# 5. Evaluación
echo "Evaluando..."
python3 ramses/evalua.py -r Rec/final -m Sen Gui/devel.gui
