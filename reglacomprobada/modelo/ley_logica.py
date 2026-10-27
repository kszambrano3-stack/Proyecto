from enum import Enum


class LeyLogica(Enum):
    DOBLE_NEGACION = (
        "Doble negaci\u00f3n",
        "Negar dos veces deja la frase como estaba: not not p equivale a p")
    DE_MORGAN = (
        "Ley de De Morgan",
        "Se niega cada parte y el conectivo cambia: not (p and q) equivale a not p or not q")
    NEGACION_CONSTANTE = (
        "Negaci\u00f3n de una constante",
        "La negaci\u00f3n de verdadero es falso y la de falso es verdadero")
    IDEMPOTENCIA = (
        "Idempotencia",
        "Repetir lo mismo no agrega nada: p or p equivale a p")
    COMPLEMENTO = (
        "Complemento",
        "Algo y su contrario: p or not p siempre es verdadero y p and not p siempre es falso")
    IDENTIDAD_DOMINACION = (
        "Identidad y dominaci\u00f3n",
        "Un verdadero en un AND o un falso en un OR no cambia nada; lo contrario vuelve todo constante")
    ABSORCION = (
        "Absorci\u00f3n",
        "La parte repetida absorbe al resto: p or (p and q) equivale a p")
    DISTRIBUTIVA_COMPLEMENTO = (
        "Distributiva y complemento",
        "Si ya est\u00e1 p, no hace falta not p: p or (not p and q) equivale a p or q")
    DISTRIBUTIVA = (
        "Distributiva",
        "Se saca el factor com\u00fan: (p and q) or (p and r) equivale a p and (q or r)")

    def __init__(self, nombre, explicacion):
        self.nombre = nombre
        self.explicacion = explicacion
