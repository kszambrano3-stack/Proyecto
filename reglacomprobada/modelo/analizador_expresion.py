from reglacomprobada.modelo.excepciones import ExpresionInvalidaError
from reglacomprobada.modelo.nodo import Nodo

SIMBOLO_Y = "\u2227"
SIMBOLO_O = "\u2228"
SIMBOLO_NO = "\u00ac"


class AnalizadorExpresion:

    def __init__(self):
        self._fichas = []
        self._posicion = 0

    def analizar(self, texto):
        if texto is None or texto.strip() == "":
            raise ExpresionInvalidaError("La regla est\u00e1 vac\u00eda")
        self._fichas = self._separar_fichas(texto)
        self._posicion = 0
        resultado = self._leer_disyuncion()
        if self._posicion < len(self._fichas):
            raise ExpresionInvalidaError(
                "Sobra algo despu\u00e9s de la regla: " + self._describir(self._fichas[self._posicion]))
        return resultado

    def _separar_fichas(self, texto):
        resultado = []
        indice = 0
        while indice < len(texto):
            caracter = texto[indice]
            if caracter.isspace():
                indice += 1
            elif caracter == "(" or caracter == ")":
                resultado.append(caracter)
                indice += 1
            elif caracter == "!" or caracter == "~" or caracter == SIMBOLO_NO:
                resultado.append("NO")
                indice += 1
            elif caracter == "&" or caracter == SIMBOLO_Y:
                resultado.append("Y")
                indice += 1
                if indice < len(texto) and texto[indice] == "&":
                    indice += 1
            elif caracter == "|" or caracter == SIMBOLO_O:
                resultado.append("O")
                indice += 1
                if indice < len(texto) and texto[indice] == "|":
                    indice += 1
            elif caracter.isalpha() or caracter == "_":
                inicio = indice
                while indice < len(texto) and (texto[indice].isalnum() or texto[indice] == "_"):
                    indice += 1
                resultado.append(self._clasificar_palabra(texto[inicio:indice]))
            else:
                raise ExpresionInvalidaError(
                    "Car\u00e1cter no v\u00e1lido '" + caracter + "' en la posici\u00f3n " + str(indice + 1))
        return resultado

    def _clasificar_palabra(self, palabra):
        minuscula = palabra.lower()
        if minuscula == "and":
            return "Y"
        if minuscula == "or":
            return "O"
        if minuscula == "not":
            return "NO"
        if minuscula == "true":
            return "CONST:V"
        if minuscula == "false":
            return "CONST:F"
        return "VAR:" + palabra

    def _leer_disyuncion(self):
        operandos = [self._leer_conjuncion()]
        while self._hay_ficha("O"):
            self._posicion += 1
            operandos.append(self._leer_conjuncion())
        return Nodo.disyuncion(operandos)

    def _leer_conjuncion(self):
        operandos = [self._leer_negacion()]
        while self._hay_ficha("Y"):
            self._posicion += 1
            operandos.append(self._leer_negacion())
        return Nodo.conjuncion(operandos)

    def _leer_negacion(self):
        if self._hay_ficha("NO"):
            self._posicion += 1
            return Nodo.negacion(self._leer_negacion())
        return self._leer_primario()

    def _leer_primario(self):
        if self._posicion >= len(self._fichas):
            raise ExpresionInvalidaError(
                "La regla termina antes de tiempo: falta una variable o un par\u00e9ntesis")
        ficha = self._fichas[self._posicion]
        if ficha == "(":
            self._posicion += 1
            interior = self._leer_disyuncion()
            if not self._hay_ficha(")"):
                raise ExpresionInvalidaError("Falta cerrar un par\u00e9ntesis")
            self._posicion += 1
            return interior
        if ficha.startswith("VAR:"):
            self._posicion += 1
            return Nodo.variable(ficha[4:])
        if ficha.startswith("CONST:"):
            self._posicion += 1
            return Nodo.constante(ficha.endswith("V"))
        raise ExpresionInvalidaError("Se esperaba una variable y se encontr\u00f3 " + self._describir(ficha))

    def _hay_ficha(self, esperada):
        return self._posicion < len(self._fichas) and self._fichas[self._posicion] == esperada

    def _describir(self, ficha):
        if ficha == "Y":
            return "el conectivo AND"
        if ficha == "O":
            return "el conectivo OR"
        if ficha == "NO":
            return "una negaci\u00f3n"
        if ficha.startswith("VAR:"):
            return "la variable " + ficha[4:]
        return "'" + ficha + "'"
