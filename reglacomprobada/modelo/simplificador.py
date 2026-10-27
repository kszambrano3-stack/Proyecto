from reglacomprobada.modelo.ley_logica import LeyLogica
from reglacomprobada.modelo.nodo import Nodo
from reglacomprobada.modelo.paso_simplificacion import PasoSimplificacion
from reglacomprobada.modelo.resultado_simplificacion import ResultadoSimplificacion
from reglacomprobada.modelo.tipo_nodo import TipoNodo

LIMITE_PASOS = 60


class Simplificador:

    def __init__(self):
        self._reglas = {
            LeyLogica.DOBLE_NEGACION: self._doble_negacion,
            LeyLogica.DE_MORGAN: self._de_morgan,
            LeyLogica.NEGACION_CONSTANTE: self._negacion_constante,
            LeyLogica.IDEMPOTENCIA: self._idempotencia,
            LeyLogica.COMPLEMENTO: self._complemento,
            LeyLogica.IDENTIDAD_DOMINACION: self._identidad_dominacion,
            LeyLogica.ABSORCION: self._absorcion,
            LeyLogica.DISTRIBUTIVA_COMPLEMENTO: self._distributiva_complemento,
            LeyLogica.DISTRIBUTIVA: self._distributiva,
        }

    def simplificar(self, original):
        pasos = []
        actual = original
        for _ in range(LIMITE_PASOS):
            aplicado = False
            for ley in LeyLogica:
                nuevo, cambio = self._reescribir(actual, ley)
                if cambio and nuevo != actual:
                    pasos.append(PasoSimplificacion(ley, nuevo))
                    actual = nuevo
                    aplicado = True
                    break
            if not aplicado:
                break
        return ResultadoSimplificacion(original, actual, pasos)

    def _reescribir(self, nodo, ley):
        reemplazo = self._reglas[ley](nodo)
        if reemplazo is not None:
            return reemplazo, True
        if len(nodo.hijos) == 0:
            return nodo, False
        nuevos_hijos = []
        hubo_cambio = False
        for hijo in nodo.hijos:
            nuevo_hijo, cambio_hijo = self._reescribir(hijo, ley)
            nuevos_hijos.append(nuevo_hijo)
            if cambio_hijo:
                hubo_cambio = True
        if not hubo_cambio:
            return nodo, False
        return self._reconstruir(nodo, nuevos_hijos), True

    def _reconstruir(self, modelo, hijos):
        if modelo.tipo == TipoNodo.NEGACION:
            return Nodo.negacion(hijos[0])
        if modelo.tipo == TipoNodo.CONJUNCION:
            return Nodo.conjuncion(hijos)
        return Nodo.disyuncion(hijos)

    def _reconstruir_interno(self, interno, hijos):
        if interno == TipoNodo.CONJUNCION:
            return Nodo.conjuncion(hijos)
        return Nodo.disyuncion(hijos)

    def _tipo_interno(self, nodo):
        if nodo.tipo == TipoNodo.DISYUNCION:
            return TipoNodo.CONJUNCION
        return TipoNodo.DISYUNCION

    def _doble_negacion(self, nodo):
        if nodo.tipo == TipoNodo.NEGACION and nodo.hijos[0].tipo == TipoNodo.NEGACION:
            return nodo.hijos[0].hijos[0]
        return None

    def _de_morgan(self, nodo):
        if nodo.tipo != TipoNodo.NEGACION:
            return None
        interior = nodo.hijos[0]
        if not interior.es_compuesto():
            return None
        negados = [Nodo.negacion(hijo) for hijo in interior.hijos]
        if interior.tipo == TipoNodo.CONJUNCION:
            return Nodo.disyuncion(negados)
        return Nodo.conjuncion(negados)

    def _negacion_constante(self, nodo):
        if nodo.tipo == TipoNodo.NEGACION and nodo.hijos[0].tipo == TipoNodo.CONSTANTE:
            return Nodo.constante(not nodo.hijos[0].valor)
        return None

    def _idempotencia(self, nodo):
        if not nodo.es_compuesto():
            return None
        unicos = {}
        for hijo in nodo.hijos:
            unicos.setdefault(hijo.clave, hijo)
        if len(unicos) == len(nodo.hijos):
            return None
        return self._reconstruir(nodo, list(unicos.values()))

    def _son_contrarios(self, uno, otro):
        if uno.tipo == TipoNodo.NEGACION and uno.hijos[0] == otro:
            return True
        return otro.tipo == TipoNodo.NEGACION and otro.hijos[0] == uno

    def _complemento(self, nodo):
        if not nodo.es_compuesto():
            return None
        hijos = nodo.hijos
        for i in range(len(hijos)):
            for j in range(i + 1, len(hijos)):
                if self._son_contrarios(hijos[i], hijos[j]):
                    return Nodo.constante(nodo.tipo == TipoNodo.DISYUNCION)
        return None

    def _identidad_dominacion(self, nodo):
        if not nodo.es_compuesto():
            return None
        es_conjuncion = nodo.tipo == TipoNodo.CONJUNCION
        neutro = es_conjuncion
        dominante = not es_conjuncion
        hay_constante = False
        restantes = []
        for hijo in nodo.hijos:
            if hijo.tipo == TipoNodo.CONSTANTE:
                hay_constante = True
                if hijo.valor == dominante:
                    return Nodo.constante(dominante)
                if hijo.valor != neutro:
                    restantes.append(hijo)
            else:
                restantes.append(hijo)
        if not hay_constante:
            return None
        return self._reconstruir(nodo, restantes)

    def _factores_clave(self, operando, interno):
        if operando.tipo == interno:
            return [hijo.clave for hijo in operando.hijos]
        return [operando.clave]

    def _factores_nodo(self, operando, interno):
        if operando.tipo == interno:
            return list(operando.hijos)
        return [operando]

    def _absorcion(self, nodo):
        if not nodo.es_compuesto():
            return None
        interno = self._tipo_interno(nodo)
        operandos = list(nodo.hijos)
        total = len(operandos)
        eliminado = [False] * total
        hubo_cambio = False
        for j in range(total):
            factores_j = self._factores_clave(operandos[j], interno)
            for i in range(total):
                if i == j or eliminado[i]:
                    continue
                factores_i = self._factores_clave(operandos[i], interno)
                contenido = all(clave in factores_j for clave in factores_i)
                iguales = len(factores_i) == len(factores_j)
                if contenido and (not iguales or i < j):
                    eliminado[j] = True
                    hubo_cambio = True
                    break
        if not hubo_cambio:
            return None
        restantes = [operandos[k] for k in range(total) if not eliminado[k]]
        return self._reconstruir(nodo, restantes)

    def _distributiva_complemento(self, nodo):
        if not nodo.es_compuesto():
            return None
        interno = self._tipo_interno(nodo)
        operandos = list(nodo.hijos)
        for j in range(len(operandos)):
            candidato = operandos[j]
            if candidato.tipo != interno:
                continue
            for factor in candidato.hijos:
                for i in range(len(operandos)):
                    if i != j and self._son_contrarios(factor, operandos[i]):
                        sin_factor = list(candidato.hijos)
                        sin_factor.remove(factor)
                        reducido = self._reconstruir_interno(interno, sin_factor)
                        nuevos = list(operandos)
                        nuevos[j] = reducido
                        return self._reconstruir(nodo, nuevos)
        return None

    def _distributiva(self, nodo):
        if not nodo.es_compuesto():
            return None
        interno = self._tipo_interno(nodo)
        operandos = list(nodo.hijos)
        frecuencia = {}
        for operando in operandos:
            distintos = list(dict.fromkeys(self._factores_clave(operando, interno)))
            for clave in distintos:
                frecuencia[clave] = frecuencia.get(clave, 0) + 1
        mejor = None
        mejor_conteo = 1
        for clave, conteo in frecuencia.items():
            if conteo > mejor_conteo:
                mejor = clave
                mejor_conteo = conteo
        if mejor is None:
            return None
        grupo = [i for i in range(len(operandos))
                 if mejor in self._factores_clave(operandos[i], interno)]
        comunes = list(self._factores_clave(operandos[grupo[0]], interno))
        for indice in grupo:
            claves = self._factores_clave(operandos[indice], interno)
            comunes = [clave for clave in comunes if clave in claves]
        factores_comunes = [factor for factor in self._factores_nodo(operandos[grupo[0]], interno)
                            if factor.clave in comunes]
        restos = []
        for indice in grupo:
            resto = [factor for factor in self._factores_nodo(operandos[indice], interno)
                     if factor.clave not in comunes]
            if len(resto) == 0:
                return None
            restos.append(self._reconstruir_interno(interno, resto))
        suma_de_restos = self._reconstruir(nodo, restos)
        factorizado = factores_comunes + [suma_de_restos]
        nuevo_operando = self._reconstruir_interno(interno, factorizado)
        resultado = []
        colocado = False
        for i in range(len(operandos)):
            if i in grupo:
                if not colocado:
                    resultado.append(nuevo_operando)
                    colocado = True
            else:
                resultado.append(operandos[i])
        return self._reconstruir(nodo, resultado)
