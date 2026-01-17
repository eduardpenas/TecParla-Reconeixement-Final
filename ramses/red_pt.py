import torch
import numpy as np
import os
import sys
import random  # <--- IMPORTANTE
from collections import namedtuple
from torch.nn.functional import nll_loss
from torch.optim import SGD, Adam

# --- IMPORTS ROBUSTOS ---
try:
    from ramses.util import *
    from ramses.mod import Modelo
    from ramses.mar import *
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from ramses.util import *
    from ramses.mod import Modelo
    from ramses.mar import *

# --- FUNCIONES ---

def robust_load(path):
    try: return np.loadtxt(path)
    except: return np.load(path)

def lotesPT(dirPrm, dirMar, ficLisUni, ficLisSen, batch_size=64):
    unidades = leeLis(ficLisUni)
    SenalPT = namedtuple('senal', ['sen', 'prm', 'trn'])
    todas = []
    lista = leeLis(ficLisSen)
    
    print(f"DEBUG: Cargando {len(lista)} señales desde {dirPrm}...")
    validas = 0

    for sen in lista:
        base = str(pathName(dirPrm, sen, 'prm'))
        cands = [base, base+'.npy', os.path.join(dirPrm, sen+'.npy'), os.path.join(dirPrm, sen+'.prm.npy')]
        pathPrm = next((c for c in cands if os.path.exists(c)), None)
        
        if not pathPrm: continue

        try:
            arr = robust_load(pathPrm)
            # Mean Pooling si es matriz
            if arr.ndim > 1: arr = np.mean(arr, axis=0)
            prm_t = torch.tensor(arr, dtype=torch.float).reshape(1, 1, 1, -1)
            
            trn_t = None
            uni = None
            
            if dirMar:
                pathMar = str(pathName(dirMar, sen, 'mar'))
                if os.path.exists(pathMar):
                    try: uni = cogeTrn(pathMar).strip().lower()
                    except: pass
            
            # Fallback nombre fichero
            if not uni or uni not in unidades:
                try: 
                    b = os.path.basename(sen)
                    if b[0].lower() in unidades: uni = b[0].lower()
                except: pass

            if uni and uni in unidades:
                trn_t = torch.tensor([unidades.index(uni)], dtype=torch.long)
                validas += 1
            
            todas.append(SenalPT(sen=sen, prm=prm_t, trn=trn_t))
            
        except: continue
    
    if len(todas) == 0: return []
    print(f"DEBUG: Cargadas {len(todas)} señales. Con etiqueta válida: {validas}")
    
    # --- SHUFFLE: CRÍTICO PARA QUE LA RED APRENDA ---
    random.shuffle(todas)
    # -----------------------------------------------
    
    # Crear mini-lotes
    return [todas[i:i + batch_size] for i in range(0, len(todas), batch_size)]

def calcDimIni(d, f): return 18
def calcDimSal(f): return len(leeLis(f))

# --- CLASE MODPT ---

class ModPT(Modelo):
    def __init__(self, ficLisUni=None, ficMod=None, red=None, funcLoss=nll_loss, Optim=lambda p: Adam(p, lr=1e-3)):
        self.red = None
        if ficMod:
            self.leeMod(ficMod)
        elif ficLisUni:
            self.unidades = leeLis(ficLisUni)
            self.red = red
            self.red.unidades = self.unidades
            self.funcLoss = funcLoss
            self.optim = Optim(self.red.parameters())

    def escrMod(self, f):
        os.makedirs(os.path.dirname(f), exist_ok=True)
        self.red.unidades = self.unidades
        torch.jit.script(self.red).save(f)

    def leeMod(self, f):
        self.red = torch.jit.load(f)
        self.red.eval()
        self.unidades = getattr(self.red, 'unidades', ['a','e','i','o','u'])

    def inicEntr(self):
        self.red.train()
        self.optim.zero_grad()

    def batch_add(self, lote):
        batch_valid = [s for s in lote if s.trn is not None]
        if not batch_valid: return
        
        input_tensor = torch.cat([s.prm for s in batch_valid], dim=0)
        target_tensor = torch.cat([s.trn for s in batch_valid], dim=0)
        
        output = self.red(input_tensor).reshape(len(batch_valid), -1)
        loss = self.funcLoss(output, target_tensor)
        loss.backward()

    def recaMod(self):
        self.optim.step()
        self.optim.zero_grad()

    def batch_eval(self, lote):
        self.red.eval()
        batch_valid = [s for s in lote if s.trn is not None]
        if not batch_valid: return
        
        with torch.no_grad():
            input_tensor = torch.cat([s.prm for s in batch_valid], dim=0)
            target_tensor = torch.cat([s.trn for s in batch_valid], dim=0)
            
            out = self.red(input_tensor).reshape(len(batch_valid), -1)
            loss = self.funcLoss(out, target_tensor)
            
            self.loss_acum += loss.item() * len(batch_valid)
            preds = out.argmax(dim=1)
            self.aciertos += (preds == target_tensor).sum().item()
            self.n_muestras += len(batch_valid)

    def inicEval(self):
        self.loss_acum = 0; self.n_muestras = 0; self.aciertos = 0
        
    def recaEval(self):
        d = max(1, self.n_muestras)
        self.avg = self.loss_acum/d; self.acc = self.aciertos/d*100
        
    def printEval(self, epo):
        print(f"  Epo {epo+1}: Loss={self.avg:.4f} | Acc={self.acc:.2f}%")
        
    def __call__(self, senal):
        self.red.eval()
        with torch.no_grad():
            idx = self.red(senal.prm).reshape(-1).argmax().item()
            return self.red.unidades[idx]