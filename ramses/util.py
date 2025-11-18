from pathlib import Path 

def leeLis(*ficLis):
    """
    Lee el contenido de uno o más ficheros de texto, devolviendo las palabras en ellos
    contenidas en la forma de lista de cadenas de texto.
    """
    lista = []
    for fic in ficLis:
        with open(fic, 'rt') as fpLis:
         lista += [pal for linea in fpLis for pal in linea.split()]
    return lista


def pathName(dir, name: str, ext):
    if ext[0] != '.': ext = f".{ext}"
    if name.startswith(dir): name = name[len(dir)+1:]
    return Path(dir).joinpath(name).with_suffix(ext)


def chkPathName(pathName):
    """
    Crea, en el caso de que no exista previamente, el directorio del fichero
    'pathName'.
    ···
    ↪→
    """
    Path(pathName).parent.mkdir(parents=True, exist_ok=True)
