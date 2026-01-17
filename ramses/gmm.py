import numpy as np
from scipy.stats import multivariate_normal
from ramses.mod import Modelo
import pickle
import os

class ModGMM(Modelo):
    """
    Clase que implementa el modelado de una unidad mediante Mezcla de Gaussianas (GMM).
    Sigue la lógica del algoritmo EM descrita en los apuntes.
    """
    def __init__(self, pathMod=None, nmix=4):
        super().__init__(pathMod)
        if not pathMod:
            self.nmix = nmix
            self.pesos = None
            self.gauss = None
            self.sumPrm = None

    def inicMod(self):
        """Inicializa acumuladores para una nueva iteración del algoritmo EM (Paso E)"""
        self.sumPrm = None # Acumulador para medias (numerador)
        self.sumPrm2 = None # Acumulador para varianzas
        self.numSen = None # Acumulador para pesos (denominador)
        self.logPrb = 0 # Log-likelihood total para monitorizar convergencia

    def reparte(self, prm):
        """
        Calcula la probabilidad a posteriori p(Gk|x) (responsabilidades).
        Devuelve el reparto y la log-likelihood de la trama.
        """
        # Calculamos log(N(x|mu, sigma)) para cada gaussiana k
        logGauss = np.array([g.logpdf(prm) for g in self.gauss])
        
        # Truco del máximo para estabilidad numérica (evitar underflow en la exp)
        maxGauss = np.max(logGauss)
        logGauss -= maxGauss
        
        # Paso Bayes: P(x|Gk) * P(Gk)
        reparto = np.exp(logGauss) * self.pesos
        
        suma_reparto = np.sum(reparto)
        
        # Calculamos la Log-Likelihood de esta muestra: log(sum(w*p))
        logGMM = maxGauss + np.log(suma_reparto)
        
        # Normalizamos para obtener las probabilidades posteriores reales
        reparto /= suma_reparto
        
        return reparto, logGMM

    def __add__(self, prm):
        """
        Paso E (Expectation): Acumula estadísticas suficientes.
        """
        # --- INICIALIZACIÓN "LAZY" (Primera vez que vemos datos) ---
        if not hasattr(self, 'gauss') or self.gauss is None:
            # Estrategia pedida: Covarianza global, Medias aleatorias del set
            
            # 1. Pesos uniformes iniciales
            self.pesos = np.ones(self.nmix) / self.nmix
            
            # 2. Inicializar lista de gaussianas
            self.gauss = [None] * self.nmix
            
            # 3. Estimar covarianza global rapida (diagonal) usando este primer batch
            # Nota: Esto es una aproximación. Lo ideal sería usar la covarianza de todo el dataset,
            # pero al hacerlo "lazy", usamos la varianza de la primera señal como semilla razonable.
            global_cov = np.var(prm, axis=0)
            # Evitar ceros
            global_cov = np.fmax(global_cov, 1e-5) 
            
            # 4. Elegir N medias aleatorias de los datos disponibles (prm)
            indices = np.random.choice(prm.shape[0], self.nmix, replace=True)
            random_means = prm[indices, :]

            for k in range(self.nmix):
                # Inicialización: Media aleatoria, Covarianza diagonal global
                self.gauss[k] = multivariate_normal(
                    mean=random_means[k], 
                    cov=global_cov, 
                    allow_singular=True
                )

        # --- ACUMULACIÓN EM ---
        if self.sumPrm is None:
            # Inicializar acumuladores a cero
            dim = prm.shape[1]
            self.sumPrm = np.zeros((self.nmix, dim))
            self.sumPrm2 = np.zeros((self.nmix, dim))
            self.numSen = np.zeros(self.nmix)
            self.logPrb = 0

        # Iteramos por cada trama de la señal prm (T, D)
        # Vectorizamos el cálculo para velocidad
        for t in range(prm.shape[0]):
            x_t = prm[t]
            reparto, log_l = self.reparte(x_t)
            
            self.logPrb += log_l
            
            # Acumulamos estadísticas ponderadas por la responsabilidad 'reparto'
            for k in range(self.nmix):
                resp_k = reparto[k]
                self.sumPrm[k] += resp_k * x_t
                self.sumPrm2[k] += resp_k * (x_t ** 2)
                self.numSen[k] += resp_k

        return self

    def calcMod(self):
        """
        Paso M (Maximization): Recalcula pesos, medias y covarianzas.
        """
        total_frames = np.sum(self.numSen)
        if total_frames < 1e-5: return # Evitar división por cero

        for k in range(self.nmix):
            # 1. Actualizar Pesos (ck)
            self.pesos[k] = self.numSen[k] / total_frames
            
            # 2. Actualizar Medias (mu_k)
            # Evitar división por cero si una gaussiana muere
            denom = self.numSen[k] if self.numSen[k] > 0 else 1.0
            
            nueva_media = self.sumPrm[k] / denom
            
            # 3. Actualizar Covarianzas (Sigma_k) - Diagonal
            # Var = E[x^2] - (E[x])^2
            nueva_cov = (self.sumPrm2[k] / denom) - (nueva_media ** 2)
            
            # "Floor" de varianza para evitar colapsos numéricos
            nueva_cov = np.fmax(nueva_cov, 1e-5)
            
            # Actualizar objeto scipy
            if self.numSen[k] > 0: # Solo actualizamos si tuvo datos
                self.gauss[k] = multivariate_normal(mean=nueva_media, cov=nueva_cov, allow_singular=True)
        
        # Opcional: Imprimir log-likelihood promedio para ver si sube
        # print(f"    GMM Avg LogLikelihood: {self.logPrb / total_frames:.4f}")

    def escrMod(self, fpMod):
        """Escribe el modelo en un fichero abierto (formato pickle o custom)"""
        # Usamos pickle para simplificar listas y objetos complejos
        pickle.dump({'nmix': self.nmix, 'pesos': self.pesos, 
                     'means': [g.mean for g in self.gauss],
                     'covs': [g.cov for g in self.gauss]}, fpMod)

class GMM(Modelo):
    """
    Clase Contenedora (Gestor) para el sistema completo.
    Maneja un diccionario de modelos ModGMM (uno por vocal).
    Sustituye a la clase 'Gauss' en entrena.py.
    """
    def __init__(self, lisMod, nmix=4):
        # lisMod puede ser ruta a fichero o lista
        if isinstance(lisMod, str):
            with open(lisMod, 'r') as f:
                self.unidades = [x.strip() for x in f.readlines()]
        else:
            self.unidades = lisMod
            
        # Diccionario: 'a' -> ModGMM(), 'e' -> ModGMM()...
        self.modelos = {u: ModGMM(nmix=nmix) for u in self.unidades}

    def inicMod(self):
        for m in self.modelos.values():
            m.inicMod()

    def __add__(self, args):
        prm, unidad = args
        if unidad in self.modelos:
            self.modelos[unidad] += prm
        return self

    def calcMod(self):
        for m in self.modelos.values():
            m.calcMod()

    def escMod(self, pathMod):
        # Asegurar directorio
        os.makedirs(os.path.dirname(pathMod), exist_ok=True)
        with open(pathMod, 'wb') as f:
            # Guardamos el diccionario completo
            # (Nota: reconoce.py deberá saber cargar esto)
            data_to_save = {}
            for u, mod in self.modelos.items():
                 data_to_save[u] = {
                     'nmix': mod.nmix,
                     'pesos': mod.pesos,
                     'gauss_params': [(g.mean, g.cov) for g in mod.gauss]
                 }
            pickle.dump(data_to_save, f)