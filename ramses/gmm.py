import numpy as np
from scipy.stats import multivariate_normal
from ramses.mod import Modelo
import pickle
import os

class ModGMM(Modelo):
    """
    Clase que implementa el modelado de una unidad mediante Mezcla de Gaussianas (GMM).
    """
    def __init__(self, pathMod=None, nmix=4):
        super().__init__(pathMod)
        if not pathMod:
            self.nmix = nmix
            self.pesos = None
            self.gauss = None
            self.sumPrm = None

    def inicMod(self):
        self.sumPrm = None 
        self.sumPrm2 = None 
        self.numSen = None 
        self.logPrb = 0 

    def reparte(self, prm):
        logGauss = np.array([g.logpdf(prm) for g in self.gauss])
        maxGauss = np.max(logGauss)
        logGauss -= maxGauss
        reparto = np.exp(logGauss) * self.pesos
        suma_reparto = np.sum(reparto)
        logGMM = maxGauss + np.log(suma_reparto)
        reparto /= suma_reparto
        return reparto, logGMM

    def __add__(self, prm):
        if not hasattr(self, 'gauss') or self.gauss is None:
            # Inicialización Aleatoria
            self.pesos = np.ones(self.nmix) / self.nmix
            self.gauss = [None] * self.nmix
            global_cov = np.var(prm, axis=0)
            global_cov = np.fmax(global_cov, 1e-5) 
            indices = np.random.choice(prm.shape[0], self.nmix, replace=True)
            random_means = prm[indices, :]

            for k in range(self.nmix):
                self.gauss[k] = multivariate_normal(mean=random_means[k], cov=global_cov, allow_singular=True)

        if self.sumPrm is None:
            dim = prm.shape[1]
            self.sumPrm = np.zeros((self.nmix, dim))
            self.sumPrm2 = np.zeros((self.nmix, dim))
            self.numSen = np.zeros(self.nmix)
            self.logPrb = 0

        for t in range(prm.shape[0]):
            x_t = prm[t]
            reparto, log_l = self.reparte(x_t)
            self.logPrb += log_l
            for k in range(self.nmix):
                resp_k = reparto[k]
                self.sumPrm[k] += resp_k * x_t
                self.sumPrm2[k] += resp_k * (x_t ** 2)
                self.numSen[k] += resp_k
        return self

    def calcMod(self):
        total_frames = np.sum(self.numSen)
        if total_frames < 1e-5: return

        for k in range(self.nmix):
            self.pesos[k] = self.numSen[k] / total_frames
            denom = self.numSen[k] if self.numSen[k] > 0 else 1.0
            nueva_media = self.sumPrm[k] / denom
            nueva_cov = (self.sumPrm2[k] / denom) - (nueva_media ** 2)
            nueva_cov = np.fmax(nueva_cov, 1e-5)
            
            if self.numSen[k] > 0:
                self.gauss[k] = multivariate_normal(mean=nueva_media, cov=nueva_cov, allow_singular=True)

class GMM(Modelo):
    """
    Clase Gestora que maneja el diccionario de modelos (uno por vocal).
    """
    def __init__(self, lisMod=None, nmix=4, pathMod=None):
        self.modelos = {}
        # Si se pasa un path, intentamos cargar
        if pathMod:
            self.leeMod(pathMod)
        # Si se pasa una lista, inicializamos vacíos
        elif lisMod:
            if isinstance(lisMod, str):
                with open(lisMod, 'r') as f:
                    self.unidades = [x.strip() for x in f.readlines() if x.strip()]
            else:
                self.unidades = lisMod
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

    # --- MÉTODO AÑADIDO: NECESARIO PARA QUE RECONOCE.PY CARGUE LOS DATOS ---
    def leeMod(self, pathMod):
        with open(pathMod, 'rb') as f:
            data = pickle.load(f)
        
        self.modelos = {}
        # Reconstruimos los objetos ModGMM a partir del diccionario guardado
        for u, d in data.items():
            mod = ModGMM(nmix=d['nmix'])
            mod.pesos = d['pesos']
            mod.gauss = []
            for mean, cov in d['gauss_params']:
                mod.gauss.append(multivariate_normal(mean=mean, cov=cov, allow_singular=True))
            self.modelos[u] = mod

    def escMod(self, pathMod):
        os.makedirs(os.path.dirname(pathMod), exist_ok=True)
        with open(pathMod, 'wb') as f:
            data_to_save = {}
            for u, mod in self.modelos.items():
                 data_to_save[u] = {
                     'nmix': mod.nmix,
                     'pesos': mod.pesos,
                     'gauss_params': [(g.mean, g.cov) for g in mod.gauss]
                 }
            pickle.dump(data_to_save, f)
            
    def prob(self, prm):
        """Devuelve diccionario {vocal: log_prob} para una señal de entrada"""
        resultados = {}
        for u, mod in self.modelos.items():
            # Sumamos la log-likelihood de todos los frames
            log_prob_total = 0
            for t in range(prm.shape[0]):
                _, lp = mod.reparte(prm[t])
                log_prob_total += lp
            resultados[u] = log_prob_total
        return resultados