class ResultadoComparacion:

    def __init__(self, tabla, regla_a, regla_b, valores_a, valores_b):
        self._tabla = tabla
        self._regla_a = regla_a
        self._regla_b = regla_b
        self._valores_a = list(valores_a)
        self._valores_b = list(valores_b)
        self._filas_diferentes = tuple(
            fila for fila in range(len(self._valores_a))
            if self._valores_a[fila] != self._valores_b[fila])

    @property
    def tabla(self):
        return self._tabla

    @property
    def regla_a(self):
        return self._regla_a

    @property
    def regla_b(self):
        return self._regla_b

    @property
    def filas_diferentes(self):
        return self._filas_diferentes

    @property
    def total_filas(self):
        return len(self._valores_a)

    def valor_a(self, fila):
        return self._valores_a[fila]

    def valor_b(self, fila):
        return self._valores_b[fila]

    def copiar_valores_a(self):
        return list(self._valores_a)

    def copiar_valores_b(self):
        return list(self._valores_b)

    def es_equivalente(self):
        return len(self._filas_diferentes) == 0
