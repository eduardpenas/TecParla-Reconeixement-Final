#!/bin/bash

# Archivos donde guardaremos los datos
CSV_EPS="datos_epsilon.csv"
CSV_COEF="datos_coeficientes.csv"

echo "eps,exact" > $CSV_EPS
echo "coef,exact" > $CSV_COEF

# --- PARTE 1: Optimización de Epsilon (con orden 12 fijo) ---
echo "Optimizando Epsilon..."
for e in 0.00001 0.1 1 10 100 1000; do
    echo "Probando eps=$e..."
    ./ramses/todo.sh $e 12 > /dev/null 2>&1
    # Extraemos el porcentaje de Res/uno.res (ej: 73.45)
    ACC=$(grep "exact" Res/uno.res | awk '{print $3}' | sed 's/%//')
    echo "$e,$ACC" >> $CSV_EPS
done

# --- PARTE 2: Optimización de Coeficientes (con el mejor eps encontrado, ej: 10) ---
echo "Optimizando número de coeficientes..."
for c in 2 4 8 12 16 20 24 32 40 48 56 64; do
    echo "Probando coef=$c..."
    ./ramses/todo.sh 10 $c > /dev/null 2>&1
    ACC=$(grep "exact" Res/uno.res | awk '{print $3}' | sed 's/%//')
    echo "$c,$ACC" >> $CSV_COEF
done

echo "¡Sincronización finalizada! Datos guardados en archivos .csv"