Ejercicio Final de TecParla
===========================
Eduard Peñas Balart 

# A. Implementación del Estimador de Máxima Entropía

En esta práctica se ha implementado el estimador espectral basado en el principio de Máxima Entropía (Método de Burg/Yule-Walker) para el reconocimiento de vocales. Se han optimizado los hiperparámetros fundamentales del sistema: el orden del filtro LPC y el factor de blanqueo ($\epsilon$).

## 1. Optimización del Orden del Análisis (LPC)

El primer experimento consistió en evaluar la dependencia de la exactitud del sistema en función del orden del filtro de predicción lineal. El objetivo es encontrar un compromiso entre la capacidad de modelado y la generalización.

![Gráfica de Exactitud vs Orden](imágenes/exactitud_vs_orden.png)
*Figura 1: Evolución de la exactitud (%) en función del orden del análisis LPC.*

### Análisis de resultados
Como se observa en la gráfica, la exactitud aumenta rápidamente con los primeros órdenes.
* **Órdenes bajos ($N < 6$):** El modelo es incapaz de capturar los dos primeros formantes necesarios para distinguir las vocales, resultando en una baja exactitud.
* **Órdenes medios ($N \approx 8$):** Se alcanza un rendimiento óptimo. El sistema modela correctamente la envolvente espectral sin ajustar detalles innecesarios.
* **Órdenes altos:** Aumentar el orden más allá de 10-12 no aporta mejoras significativas y aumenta el coste computacional. Además, un orden excesivo podría empezar a modelar la estructura fina (el pitch) en lugar de solo la envolvente, lo que podría reducir la robustez (overfitting).

**Conclusión:** Se selecciona **Orden = 8** como el valor óptimo para las siguientes etapas.

---

## 2. Dependencia con el Umbral Epsilon ($\epsilon$)

El parámetro $\epsilon$ se utiliza en la transformación logarítmica $S_{log} = \log(\epsilon + S(\omega))$ para simular la percepción auditiva (escala logarítmica) y evitar inestabilidades numéricas. Fijando el orden en 8, se obtuvieron los siguientes resultados:

| Epsilon ($\epsilon$) | 1e-05 | 0.1 | 1 | 10 | 100 | 1000 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Exactitud** | **84.55 %** | 83.45 % | 80.05 % | 74.90 % | 70.65 % | 71.30 % |

### Análisis de resultados
Se observa una relación inversa entre el valor de $\epsilon$ y la exactitud:
1.  **Valores bajos:** Permiten una mayor dinámica en el espectro, resaltando los picos de los formantes. El mejor resultado numérico se obtiene con `1e-05` (84.55%).
2.  **Valores altos:** Tienden a "blanquear" o aplanar el espectro, reduciendo la distancia euclídea entre los modelos de distintas vocales y empeorando la tasa de acierto.

**Elección:** Aunque `1e-05` ofrece la máxima exactitud, se selecciona **$\epsilon = 0.1$** (83.45%) por ser un valor estándar que ofrece un excelente compromiso entre precisión y estabilidad numérica frente a silencios o señales de muy baja energía.

---

## 3. Modelado Espectral de las Vocales

Utilizando la configuración óptima (**Orden=8, $\epsilon$=0.1**), se han generado los modelos espectrales promedio para las cinco vocales.

![Modelos espectrales de las vocales](imágenes/modelos_vocales_orden_8.png)
*Figura 2: Estimación espectral de Máxima Entropía para las 5 vocales y comparativa conjunta.*

### Interpretación Visual
El estimador de Máxima Entropía genera espectros suaves (sin el ruido característico del periodograma), lo cual es ideal para el reconocimiento de patrones:
* **Identificación de Formantes:** Se distinguen claramente los picos de resonancia (F1 y F2) que definen cada vocal.
* **Separabilidad:** En la gráfica comparativa (inferior derecha), se aprecia cómo los modelos ocupan diferentes regiones espectrales. Por ejemplo, la vocal /i/ (línea azul) presenta un primer formante muy bajo y un segundo muy alto, diferenciándose claramente de la /a/ (línea roja) que tiene la energía más centrada. Esto justifica la alta tasa de acierto del sistema (>83%).|
-----------------------------------------------------

#### Utilización de los coeficientes cepstrales en escala Mel (MFCC)

Se usará la biblioteca `python_speech_features` para incorporar a `ramses` los coeficientes MFCC. En la sección
4.4.3 de los apuntes hay una explicación de estos coeficientes, aunque no se proporciona su implementación detallada.

Deberán optimizarse todos los parámetros involucrados en el cálculo de los MFCC, pero, en concreto, deberá seleccionarse
la mejor combinación del número de coeficientes y del número de bandas del banco de filtros.

Para el número de coeficientes y de bandas deberá aportarse justificación gráfica adecuada para apoyar la elección.
# B. Utilización de los Coeficientes Cepstrales en Escala Mel (MFCC)

Para mejorar el reconocimiento, se ha sustituido la parametrización LPC por **MFCC** (Mel-Frequency Cepstral Coefficients). Este método imita la percepción auditiva humana utilizando un banco de filtros espaciados logarítmicamente (Escala Mel) y decorrela las características mediante la Transformada Discreta del Coseno (DCT).

Se ha utilizado la librería `python_speech_features` y se han optimizado los dos parámetros críticos en dos fases.

## 1. Optimización del Número de Coeficientes (`numcep`)

**Análisis:**
El experimento determinó que **18 coeficientes** proporcionan el mejor rendimiento.
* Un número bajo de coeficientes (<12) solo captura la envolvente espectral básica (formantes).
* Al aumentar a 18, capturamos detalles espectrales finos necesarios para distinguir vocales confusas sin llegar a modelar el ruido de excitación (pitch), lo cual ocurriría con un número excesivo de coeficientes.

## 2. Optimización del Banco de Filtros (`nfilt`)

Manteniendo los 18 coeficientes óptimos, se procedió a ajustar el número de filtros del banco triangular Mel.

![Exactitud vs Filtros](imágenes/mfcc_exactitud_vs_nfilt.png)
*Figura 3: Optimización del número de filtros para numcep=18.*

**Análisis:**
La gráfica muestra un comportamiento interesante con dos picos de rendimiento:
* **Máximo global en 20 filtros:** Se alcanza una exactitud de **~92.7%**. Esto indica que, para la frecuencia de muestreo de 8kHz (ancho de banda 4kHz), un banco de filtros menos denso (20 filtros) es suficiente y quizás más robusto, evitando el solapamiento excesivo de bandas en altas frecuencias.
* Se observa otro pico de rendimiento en 30 filtros, pero decae drásticamente al aumentar a 40, probablemente debido a que los filtros se vuelven demasiado estrechos y sensibles a variaciones no fonéticas.

**Conclusión MFCC:** La configuración final seleccionada es **NumCep=18** y **NFilt=20**, alcanzando una exactitud del **92.7%**, superando ampliamente al estimador de Máxima Entropía.

# C. Modelado Estadístico con Mezcla de Gaussianas (GMM)

Tras optimizar la parametrización utilizando coeficientes MFCC, el siguiente paso para mejorar la robustez del sistema ha sido sustituir el modelado unimodal (una única media y varianza por vocal) por un modelo probabilístico más potente: los **Modelos de Mezcla de Gaussianas (GMM)**.

Tal y como se describe en la teoría, la distribución acústica real de una vocal no suele seguir una única campana de Gauss perfecta debido a la variabilidad inherente del habla (género del locutor, acento, coarticulación). Un GMM permite modelar esta densidad compleja mediante la suma ponderada de varias gaussianas:

$$f(x|\lambda) = \sum_{k=1}^{M} c_k \mathcal{N}(x, \mu_k, \Sigma_k)$$

Para el entrenamiento de los parámetros $(\mu_k, \Sigma_k, c_k)$, se ha implementado el algoritmo **EM (Expectation-Maximization)**, que itera entre estimar la probabilidad de pertenencia de cada dato a una gaussiana (Paso E) y recalcular los parámetros para maximizar la verosimilitud (Paso M).

## Diseño del Experimento

* **Características de entrada:** Configuración óptima de MFCC (18 coeficientes, 20 filtros).
* **Inicialización:** Se utilizaron medias aleatorias seleccionadas del conjunto de entrenamiento y matrices de covarianza diagonales inicializadas con la varianza global, conforme a las especificaciones del apartado 5.4.
* **Variable de optimización:** Se varió el número de gaussianas por mezcla (`nmix`) en potencias de 2 (desde 1 hasta 32).

## Resultados Obtenidos

| N.º Gaussianas (`nmix`) | Exactitud (%) | Mejora relativa |
| :---: | :---: | :---: |
| **1** | 92.90 % | - |
| **2** | 92.80 % | -0.10 % |
| **4** | 95.65 % | **+2.85 %** |
| **8** | **95.85 %** | +0.20 % |
| **16** | 95.55 % | -0.30 % |
| **32** | 95.80 % | +0.25 % |

![Gráfica de Exactitud vs Número de Gaussianas](imagenes/gmm_exactitud_vs_nmix.png)
*Figura 5: Evolución de la exactitud del sistema en función del número de gaussianas por mezcla.*

## Análisis y Discusión

1.  **El salto de la multimodalidad (N=2 a N=4):**
    Se observa un incremento drástico en la exactitud (casi un 3%) al pasar de 2 a 4 gaussianas. Esto confirma la limitación del modelo unimodal. Con 4 gaussianas, el sistema empieza a ser capaz de separar subgrupos naturales dentro de la nube de puntos de cada vocal. Un ejemplo típico es la separación espectral entre voces masculinas y femeninas, o variantes alofónicas de la misma vocal.

2.  **El punto óptimo (N=8):**
    El máximo rendimiento global se alcanza con **8 gaussianas**, logrando una exactitud del **95.85%**. Este valor representa el equilibrio ideal donde el modelo tiene suficiente flexibilidad para capturar los matices finos de la pronunciación sin aumentar innecesariamente la complejidad.

3.  **Saturación y Sobreajuste (N > 8):**
    Al aumentar la complejidad a 16 y 32 gaussianas, la exactitud se estanca e incluso oscila ligeramente a la baja (95.55%).
    * Esto indica que añadir más componentes no aporta nueva información fonética relevante.
    * Existe un riesgo de **sobreajuste (overfitting)**: con demasiadas gaussianas para la cantidad de datos disponibles, el modelo empieza a "memorizar" el ruido específico o las particularidades de los locutores de entrenamiento en lugar de generalizar la forma de la vocal, lo que penaliza el rendimiento en el conjunto de test.

## Conclusión

La configuración final seleccionada para el sistema Ramsés utiliza una parametrización **MFCC (18 coef, 20 filtros)** junto con un modelado **GMM de 8 gaussianas**, alcanzando una tasa de acierto final del **95.85%**.

# D. Optimización Final y Análisis de Resultados (Deep Learning)

Como culminación del proyecto, se ha desarrollado un sistema de modelado acústico basado en **Redes Neuronales Artificiales (ANN)** utilizando el framework PyTorch. El objetivo era superar la barrera de rendimiento impuesta por los modelos estadísticos tradicionales (GMM) mediante el aprendizaje de características no lineales.

Para alcanzar el máximo rendimiento posible (**96.75%**), se implementó una estrategia de entrenamiento avanzada denominada "Configuración Turbo", integrando técnicas del estado del arte en Deep Learning para garantizar la convergencia y la generalización del modelo.

## 5.1. Arquitectura y Configuración del Sistema

A diferencia de los modelos paramétricos simples, este sistema aprende a extraer patrones complejos directamente de los coeficientes MFCC. La configuración óptima resultante de la búsqueda de hiperparámetros fue:

* **Arquitectura:** MLP (Perceptrón Multicapa) con topología *Feed-Forward*.
* **Dimensiones:** 2 Capas (Entrada $\to$ Oculta de **128 neuronas** $\to$ Salida). Se aumentó la capa oculta de 64 a 128 neuronas para incrementar la capacidad de abstracción de la red.
* **Optimizador:** **Adam** (Adaptive Moment Estimation), seleccionado por su capacidad de adaptar la tasa de aprendizaje dinámicamente, superando al SGD clásico en velocidad de convergencia.
* **Regularización y Estabilidad:**
    * **Batch Normalization (1D):** Aplicado a la entrada para normalizar la distribución de los MFCCs, evitando la saturación de gradientes y permitiendo un aprendizaje más agresivo.
    * **Data Shuffling:** Barajado aleatorio de los mini-lotes (*batch size=64*) en cada época para romper la correlación temporal de los datos y asegurar un descenso de gradiente estocástico real.

## 5.2. Dinámica del Entrenamiento

El modelo fue entrenado durante **400 épocas**. Como se observa en la gráfica siguiente, la inclusión de *Batch Normalization* permitió una curva de aprendizaje suave y constante. 

Se observa que el modelo alcanza su pico de rendimiento (**96.85%**) alrededor de la época 385, estabilizándose finalmente en un **96.75%**. Esta mínima oscilación final (0.1%) indica que el modelo ha alcanzado su capacidad máxima de aprendizaje sin entrar en un sobreajuste (overfitting) destructivo.

![Curva de Aprendizaje del Modelo](imágenes/grafica_curva_aprendizaje.png)
*Figura 1: Evolución del entrenamiento. Se observa la convergencia asintótica del modelo y la estabilidad del Loss en las últimas 100 épocas.*

## 5.3. Comparativa Global de Sistemas

El proyecto ha seguido una evolución incremental, desde algoritmos básicos hasta inteligencia artificial moderna. La siguiente tabla resume el salto cualitativo obtenido:

| Sistema | Tecnología Base | Exactitud Final | Análisis |
| :--- | :--- | :---: | :--- |
| **Básico** | Distancia Euclídea | ~83.00% | Modelo ingenuo, insuficiente para variabilidad real. |
| **Intermedio** | GMM (8 Gaussianas) | 95.85% | Modelo estadístico robusto. |
| **Avanzado** | **Deep Learning (MLP)** | **96.75%** | **SOTA (State of the Art). Supera la barrera estadística.** |

![Comparativa de Modelos](imágenes/grafica_comparativa_modelos.png)
*Figura 2: Comparativa de rendimiento. El sistema de Deep Learning logra reducir el error residual del GMM en casi un 1% absoluto.*

## 5.4. Análisis Detallado de Errores

Para validar la robustez del sistema, se ha analizado la **Matriz de Confusión** final sobre el conjunto de desarrollo (2000 muestras).

![Matriz de Confusión Final](imágenes/grafica_matriz_confusion.png)
*Figura 3: Matriz de confusión del sistema optimizado.*

**Discusión de Resultados:**
1.  **Robustez en Vocales Anteriores:** Las vocales **/e/** y **/i/** presentan una tasa de acierto casi perfecta (>99%). Esto indica que la red ha aprendido a separar perfectamente sus formantes característicos.
2.  **El Desafío /o/ - /u/:** El único error sistemático residual se encuentra en la confusión entre las vocales posteriores **/o/** y **/u**. Acústicamente, estas vocales comparten un primer formante (F1) muy bajo y cercano. Aun así, el sistema de Deep Learning ha minimizado este error mejor que el GMM.

## 5.5. Conclusión Final

La implementación de un Perceptrón Multicapa optimizado con **Batch Normalization** y **Adam** ha demostrado ser superior a los enfoques clásicos. El sistema final obtiene una exactitud del **96.75%**, demostrando una estabilidad matemática y una capacidad de generalización idóneas para tareas de reconocimiento de vocales de alta precisión.
