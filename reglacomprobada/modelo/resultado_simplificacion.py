class ResultadoSimplificacion:

    def __init__(self, original, simplificada, pasos):
        self._original = original
        self._simplificada = simplificada
        self._pasos = tuple(pasos)

    @property
    def original(self):
        return self._original

    @property
    def simplificada(self):
        return self._simplificada

    @property
    def pasos(self):
        return self._pasos

    @property
    def operadores_antes(self):
        return self._original.contar_operadores()

    @property
    def operadores_despues(self):
        return self._simplificada.contar_operadores()

    @property
    def porcentaje_ahorro(self):
        antes = self.operadores_antes
        if antes == 0:
            return 0
        return (antes - self.operadores_despues) * 100 // antes
