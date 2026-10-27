from enum import Enum


class Notacion(Enum):
    PYTHON = ("not ", " and ", " or ", "True", "False")
    LOGICA = ("\u00ac", " \u2227 ", " \u2228 ", "V", "F")

    def __init__(self, simbolo_negacion, simbolo_conjuncion, simbolo_disyuncion,
                 texto_verdadero, texto_falso):
        self.simbolo_negacion = simbolo_negacion
        self.simbolo_conjuncion = simbolo_conjuncion
        self.simbolo_disyuncion = simbolo_disyuncion
        self.texto_verdadero = texto_verdadero
        self.texto_falso = texto_falso
