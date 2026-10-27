from reglacomprobada.modelo.notacion import Notacion
from reglacomprobada.modelo.tipo_nodo import TipoNodo


class Nodo:

    def __init__(self, tipo, nombre="", valor=False, hijos=None):
        self._tipo = tipo
        self._nombre = nombre
        self._valor = valor
        self._hijos = tuple(hijos) if hijos is not None else ()
        self._clave = self._calcular_clave()

    @staticmethod
    def variable(nombre):
        return Nodo(TipoNodo.VARIABLE, nombre=nombre)

    @staticmethod
    def constante(valor):
        return Nodo(TipoNodo.CONSTANTE, valor=valor)

    @staticmethod
    def negacion(hijo):
        return Nodo(TipoNodo.NEGACION, hijos=[hijo])

    @staticmethod
    def conjuncion(operandos):
        return Nodo._combinar(TipoNodo.CONJUNCION, operandos)

    @staticmethod
    def disyuncion(operandos):
        return Nodo._combinar(TipoNodo.DISYUNCION, operandos)

    @staticmethod
    def _combinar(tipo, operandos):
        planos = []
        for operando in operandos:
            if operando.tipo == tipo:
                planos.extend(operando.hijos)
            else:
                planos.append(operando)
        if len(planos) == 0:
            return Nodo.constante(tipo == TipoNodo.CONJUNCION)
        if len(planos) == 1:
            return planos[0]
        return Nodo(tipo, hijos=planos)

    def _calcular_clave(self):
        if self._tipo == TipoNodo.VARIABLE:
            return self._nombre
        if self._tipo == TipoNodo.CONSTANTE:
            return "V" if self._valor else "F"
        if self._tipo == TipoNodo.NEGACION:
            return "!" + self._hijos[0].clave
        claves = sorted(hijo.clave for hijo in self._hijos)
        prefijo = "&(" if self._tipo == TipoNodo.CONJUNCION else "|("
        return prefijo + ",".join(claves) + ")"

    def evaluar(self, asignacion):
        if self._tipo == TipoNodo.VARIABLE:
            return asignacion.get(self._nombre, False) is True
        if self._tipo == TipoNodo.CONSTANTE:
            return self._valor
        if self._tipo == TipoNodo.NEGACION:
            return not self._hijos[0].evaluar(asignacion)
        if self._tipo == TipoNodo.CONJUNCION:
            for hijo in self._hijos:
                if not hijo.evaluar(asignacion):
                    return False
            return True
        for hijo in self._hijos:
            if hijo.evaluar(asignacion):
                return True
        return False

    def recolectar_variables(self, destino):
        if self._tipo == TipoNodo.VARIABLE:
            destino.add(self._nombre)
        for hijo in self._hijos:
            hijo.recolectar_variables(destino)

    def contar_operadores(self):
        total = 0
        if self._tipo == TipoNodo.NEGACION:
            total = 1
        elif self.es_compuesto():
            total = len(self._hijos) - 1
        for hijo in self._hijos:
            total = total + hijo.contar_operadores()
        return total

    def es_compuesto(self):
        return self._tipo == TipoNodo.CONJUNCION or self._tipo == TipoNodo.DISYUNCION

    def a_texto(self, notacion):
        if self._tipo == TipoNodo.VARIABLE:
            return self._nombre
        if self._tipo == TipoNodo.CONSTANTE:
            return notacion.texto_verdadero if self._valor else notacion.texto_falso
        if self._tipo == TipoNodo.NEGACION:
            interior = self._hijos[0]
            if interior.es_compuesto():
                return notacion.simbolo_negacion + "(" + interior.a_texto(notacion) + ")"
            return notacion.simbolo_negacion + interior.a_texto(notacion)
        if self._tipo == TipoNodo.CONJUNCION:
            separador = notacion.simbolo_conjuncion
        else:
            separador = notacion.simbolo_disyuncion
        partes = []
        for hijo in self._hijos:
            if hijo.es_compuesto():
                partes.append("(" + hijo.a_texto(notacion) + ")")
            else:
                partes.append(hijo.a_texto(notacion))
        return separador.join(partes)

    @property
    def tipo(self):
        return self._tipo

    @property
    def nombre(self):
        return self._nombre

    @property
    def valor(self):
        return self._valor

    @property
    def hijos(self):
        return self._hijos

    @property
    def clave(self):
        return self._clave

    def __eq__(self, otro):
        if self is otro:
            return True
        if not isinstance(otro, Nodo):
            return False
        return self._clave == otro._clave

    def __hash__(self):
        return hash(self._clave)

    def __str__(self):
        return self.a_texto(Notacion.PYTHON)
