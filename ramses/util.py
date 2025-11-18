from pathlib import Path

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


def pathName(dir, name: str, ext):
    '''
        Te retorna una cadena de Strings con el nombre del path
    '''
    # se puede hacer también con 
    # return dir + '/' + name + '.' + ext
    # f"{dir}/{name}{ext}"

    # Libreria para generación de path
    # https://docs.python.org/3/library/pathlib.html

    if ext[0] != '.': ext = f".{ext}"
    if name.startswith(dir): name = 
    return Path(dir).joinpath(name).with_suffix(ext)


def leeLis(*ficLis):
    """
        Lee el contenido de uno o más ficheros de texto, devolviendo las palabras en ellos
        contenidas en la forma de lista de cadenas de texto.
    """
    lista = []
    for fichero in ficLis:
        with open(fichero, 'rt') as fpLis:
            lista += [pal for linea in fpLis for pal in linea.split()]
    return lista