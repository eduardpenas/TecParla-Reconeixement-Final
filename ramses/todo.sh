#! /bin/bash

NOM=uno

DIR_WRK=.

DIR_LOG=$DIR_WRK/Log
FIC_LOG=$DIR_LOG/$(basename $0 .sh).$NOM.log
[ -d $DIR_LOG ] || mkdir -p $DIR_LOG

exec > >(tee $FIC_LOG) 2>&1

hostname
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
FIC_MOD=$DIR_MOD/vocales.mod
DIR_REC=$DIR_WRK/Rec/$NOM

LIS_MOD=$DIR_WRK/Lis/vocales.lis

FIC_RES=$DIR_WRK/Res/$NOM.res
[ -d $(dirname $FIC_RES) ] || mkdir -p $(dirname $FIC_RES)

# Parametrización

dirSen="-s $DIR_SEN"
dirPrm="-p $DIR_PRM"

# Definición de la función de parametrización
FUNK_PRM=periodograma
FUNK_PRM=cepstrum

if [ $FUNK_PRM == periodograma ]; then
    EXEC_PREV=$DIR_PRM/$FUNK_PRM
    EPS=${1:-1e-12}

    [ -d $(dirname $EXEC_PREV) ] || mkdir -p $(dirname $FIC_RES)
    echo "import numpy as np" | tee $EXEC_PREV
    echo "def $FUNK_PRM(x):" | tee -a $EXEC_PREV
    echo "    return 10*np.log10($EPS+abs(np.fft.fft(x))**2)" | tee -a $EXEC_PREV

elif [ $FUNK_PRM == cepstrum ]; then
    EXEC_PREV=$DIR_PRM/$FUNK_PRM
    EPS=${1:-0}
    NUM_COF=${2:-}
    [ -d $(dirname $EXEC_PREV) ] || mkdir -p $(dirname $FIC_RES)
    echo "import numpy as np" | tee $EXEC_PREV
    echo "def $FUNK_PRM(x):" | tee -a $EXEC_PREV
    echo "    Sx=10*np.log10($EPS+abs(np.fft.fft(x))**2)" | tee -a $EXEC_PREV
    echo "    cepstrum = np.real(np.fft.ifft(Sx))" | tee -a $EXEC_PREV
    echo "    return cepstrum[:$NUM_COF]" | tee -a $EXEC_PREV


else 
    echo "Parametrización desconocida ($FUNK_PRM)"
    exit 1
fi

funkPrm="-f $FUNK_PRM"
execPrev="-e $EXEC_PREV"

EXEC="parametriza.py $dirSen $dirPrm $funkPrm $execPrev $GUI_ENT $GUI_DEV"
echo $EXEC && $EXEC || exit 1

# Entrenamiento

dirPrm="-p $DIR_PRM"
dirMar="-m $DIR_MAR"
lisUni="-l $LIS_MOD"
ficMod="-M $FIC_MOD"

EXEC="entrena.py $dirPrm $dirMar $lisUni $ficMod $GUI_ENT"
echo $EXEC && $EXEC || exit 1

# Reconocimiento 

dirRec="-r $DIR_REC"
dirPrm="-p $DIR_PRM"
ficMod="-M $FIC_MOD"

EXEC="reconoce.py $dirRec $dirPrm $ficMod $GUI_DEV"
echo $EXEC && $EXEC || exit 1

# Evaluación del resultado 

dirRec="-r $DIR_REC" 
dirMar="-m $DIR_MAR" 

EXEC="evalua.py $dirRec $dirMar $GUI_DEV"
echo $EXEC && $EXEC | tee $FIC_RES || exit 1

date
echo sacabao, chula
