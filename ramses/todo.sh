#! /bin/bash

NOM=uno

DIR_WRK=.

DIR_LOG=$DIR_WRK/Log
FIC_LOG=$DIR_LOG/$(basename $0 .sh).$NOM.log
[ -d $DIR_LOG ] || mkdir -p $DIR_LOG

exec > >(tee $FIC_LOG) 2>&1

hostname >> FIC_LOG
pwd
date 

#Ficheros guia

DIR_GUI=$DIR_WRK/Gui
GUI_ENT=$DIR_GUI/train.gui
GUI_DEV=$DIR_GUI/devel.gui

DIR_SEN=$DIR_WRK/Sen
DIR_MAR=$DIR_WRK/Sen
DIR_PRM=$DIR_WRK/Prm/$NOM
DIR_MOD=$DIR_WRK/Mod/$NOM
FIC_MOD=$DIR_WRK/Mod/vocales.mod
DIR_REC=$DIR_WRK/Rec/$NOM

LIS_MOD=$DIR_WRK/Lis/vocales.lis

FIC_RES=$DIR_WRK/Res/$NOM.res
[ -d $(dirname $FIC_RES) ] || mkdir -p $(dirname $FIC_RES)

# Parametrización

dirSen="-s $DIR_SEN"
dirPrm="-p $DIR_PRM"

EXEC="parametriza.py $dirSen $dirPrm $GUI_ENT $GUI_DEV"
echo $EXEC && $EXEC || exit 1

# Entrenamiento 

dirPrm="-p $DIR_PRM"
dirMar="-m $DIR_MAR"
lisUni="-l $LIS_MOD"
ficMod="-M $FIC_MOD" # <--- Usamos -M para el fichero de modelo

# $GUI_ENT es el argumento posicional <guia> requerido.
EXEC="entrena.py $dirPrm $dirMar $lisUni $ficMod $GUI_ENT"
echo $EXEC && $EXEC || exit 1

# Reconocimiento
dirRec="-r $DIR_REC"
dirPrm="-p $DIR_PRM"
ficMod="-M $FIC_MOD"

EXEC="reconoce.py $dirRec $dirPrm $ficMod $GUI_DEV"
echo $EXEC && $EXEC || exit 1

# Evaluación
dirRec="-r $DIR_REC"
dirMar="-m $DIR_MAR"

EXEC="evalua.py $dirRec $dirMar $GUI_DEV"
echo $EXEC && $EXEC | tee $FIC_RES || exit 1

