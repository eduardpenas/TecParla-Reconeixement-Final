from pathlib import Path

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
    if name.startswith(dir): name = name[len(dir)+1:]
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


def chkPathName(pathName): 
    """
    Crea el directorio del fichero 'pathName' si es necesario
    """
    Path(pathName).parent.mkdir(parents=True , exist_ok=True)

    
