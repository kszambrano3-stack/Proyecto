from enum import Enum


class TipoNodo(Enum):
    VARIABLE = 1
    CONSTANTE = 2
    NEGACION = 3
    CONJUNCION = 4
    DISYUNCION = 5
