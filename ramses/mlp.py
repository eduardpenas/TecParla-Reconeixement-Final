import torch
import torch.nn as nn

def mlp_N(numCap=2, dimIni=18, dimInt=64, dimSal=5, clsAct=nn.ReLU(), clsSal=nn.LogSoftmax(dim=-1)):
    """
    Generador de MLP con Batch Normalization para convergencia rápida.
    """
    if numCap < 2:
        raise ValueError("El número mínimo de capas es 2")
        
    capas = []
    
    # --- MEJORA: Batch Normalization en la entrada ---
    # Esto normaliza los MFCCs (que tienen rangos muy locos) a una media ~0 y var ~1
    capas.append(nn.BatchNorm1d(dimIni))
    
    # Capa de entrada -> Oculta
    capas.append(nn.Linear(dimIni, dimInt))
    capas.append(clsAct)
    
    # Capas ocultas extra
    for _ in range(numCap - 2):
        capas.append(nn.Linear(dimInt, dimInt))
        capas.append(clsAct)
        
    # Capa de salida
    capas.append(nn.Linear(dimInt, dimSal))
    capas.append(clsSal)
    
    base_model = nn.Sequential(*capas)
    return MLP_Wrapper(base_model)

class MLP_Wrapper(nn.Module):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.unidades = ["placeholder"] 
        
    def forward(self, x):
        # Aplanar: (1, 1, 1, F) -> (1, F)
        x_flat = x.reshape(-1, x.shape[-1])
        out = self.base(x_flat)
        # Restaurar: (1, F) -> (1, 1, F)
        return out.reshape(1, 1, -1)