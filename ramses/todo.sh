#! /bin/bash

# ==========================================
# CONFIGURACIÓN DEL PROYECTO
# ==========================================
NOM=maxima_entropia_final
SRC=ramses   # <--- CORREGIDO: Apunta a tu carpeta real
DIR_WRK=.

# IMPORTANTE: Añadimos 'ramses' al PYTHONPATH para que encuentre maxima_entropia.py
export PYTHONPATH=$PYTHONPATH:./$SRC

# Configuración de Logs
DIR_LOG=$DIR_WRK/Log
FIC_LOG=$DIR_LOG/$(basename $0 .sh).$NOM.log
[ -d $DIR_LOG ] || mkdir -p $DIR_LOG

exec > >(tee $FIC_LOG) 2>&1

echo "========================================"
echo " SISTEMA: ESTIMADOR MÁXIMA ENTROPÍA"
echo " Carpeta de fuentes: $SRC"
echo "========================================"

# Rutas
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

# ==========================================
# 1. PARAMETRIZACIÓN (MÁXIMA ENTROPÍA)
# ==========================================
echo "----------------------------------------"
echo " [1/4] Parametrización"
echo "----------------------------------------"

dirSen="-s $DIR_SEN"
dirPrm="-p $DIR_PRM"

# Nombre de la función wrapper
FUNK_PRM=ME

EXEC_PREV=$DIR_PRM/$FUNK_PRM.py
[ -d $(dirname $EXEC_PREV) ] || mkdir -p $(dirname $EXEC_PREV)

# --- INYECCIÓN DE CÓDIGO (Según pág. 82 de los apuntes) ---
ORDEN=8       # Orden óptimo según apuntes
EPS=0.1       # Factor de blanqueo logarítmico

echo "import numpy as np" | tee $EXEC_PREV
# Importamos desde el módulo que está en ramses/maxima_entropia.py
echo "from maxima_entropia import maximaEntropia" | tee -a $EXEC_PREV

echo "orden=$ORDEN" | tee -a $EXEC_PREV
echo "eps=$EPS" | tee -a $EXEC_PREV

echo "def $FUNK_PRM(x):" | tee -a $EXEC_PREV
echo "    # Devolvemos el Logaritmo para blanquear la dinámica" | tee -a $EXEC_PREV
echo "    return np.log(eps + maximaEntropia(x, orden))" | tee -a $EXEC_PREV

funkPrm="-f $FUNK_PRM"
execPrev="-e $EXEC_PREV"

# EJECUCIÓN: Usamos $SRC para encontrar parametriza.py
EXEC="python3 $SRC/parametriza.py $dirSen $dirPrm $funkPrm $execPrev $GUI_ENT $GUI_DEV"
echo "Ejecutando: $EXEC"
$EXEC || exit 1

# ==========================================
# 2. ENTRENAMIENTO
# ==========================================
echo "----------------------------------------"
echo " [2/4] Entrenamiento"
echo "----------------------------------------"
dirPrm="-p $DIR_PRM"
dirMar="-m $DIR_MAR"
lisUni="-l $LIS_MOD"
ficMod="-M $FIC_MOD"

EXEC="python3 $SRC/entrena.py $dirPrm $dirMar $lisUni $ficMod $GUI_ENT"
echo "Ejecutando: $EXEC"
$EXEC || exit 1

# ==========================================
# 3. RECONOCIMIENTO
# ==========================================
echo "----------------------------------------"
echo " [3/4] Reconocimiento"
echo "----------------------------------------"
dirRec="-r $DIR_REC"
dirPrm="-p $DIR_PRM"
ficMod="-M $FIC_MOD"

EXEC="python3 $SRC/reconoce.py $dirRec $dirPrm $ficMod $GUI_DEV"
echo "Ejecutando: $EXEC"
$EXEC || exit 1

# ==========================================
# 4. EVALUACIÓN
# ==========================================
echo "----------------------------------------"
echo " [4/4] Evaluación"
echo "----------------------------------------"
dirRec="-r $DIR_REC" 
dirMar="-m $DIR_MAR" 

# Asegúrate de que esta línea tiene las comillas de apertura y cierre bien puestas:
EXEC="python3 $SRC/evalua.py $dirRec $dirMar $GUI_DEV"

echo "Ejecutando: $EXEC"

# Esta es la línea que suele fallar si falta algo antes:
$EXEC | tee $FIC_RES || exit 1

echo "Proceso finalizado."