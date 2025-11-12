def leeList (fitLis): 
    # with apertura [as objeto]
    # No siempre apertura saca un objeto. Utilizaremos pytorch 
    # with torch_nograd() -> no devuelve nigun objeto pero va muy rápido
    # with apertura as objeto: -> si nos devuelve un objeto
    with open(fitLis, "rt") as fpLis:
        lista = []
        for linea in fpLis: 
            lista.append(linea.strip())
    return lista