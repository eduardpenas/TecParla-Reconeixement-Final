def leeLis(fitlist): 
    with open(fitlist , "rt") as fpLis: 
        lista = []
        for linia in fpLis :
            lista.append(linia.strip())
    return lista