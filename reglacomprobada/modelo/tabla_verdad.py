from reglacomprobada.modelo.excepciones import ExpresionInvalidaError

MAXIMO_VARIABLES = 8


class TablaVerdad:

    def __init__(self, nombres):
        nombres = set(nombres)
        if len(nombres) > MAXIMO_VARIABLES:
            raise ExpresionInvalidaError(
                "Hay demasiadas variables: el m\u00e1ximo es " + str(MAXIMO_VARIABLES))
        self._variables = tuple(sorted(nombres))

    @property
    def variables(self):
        return self._variables

    @property
    def numero_filas(self):
        return 1 << len(self._variables)

    def valor_variable(self, fila, indice_variable):
        desplazamiento = len(self._variables) - 1 - indice_variable
        return ((fila >> desplazamiento) & 1) == 0

    def crear_asignacion(self, fila):
        asignacion = {}
        for indice, nombre in enumerate(self._variables):
            asignacion[nombre] = self.valor_variable(fila, indice)
        return asignacion
