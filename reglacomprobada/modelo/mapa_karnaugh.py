from reglacomprobada.modelo.excepciones import ExpresionInvalidaError

MINIMO_VARIABLES = 2
MAXIMO_VARIABLES = 4


class MapaKarnaugh:

    def __init__(self, tabla, valores):
        cantidad = len(tabla.variables)
        if not MapaKarnaugh.puede_generarse(cantidad):
            raise ExpresionInvalidaError(
                "El mapa de Karnaugh necesita entre 2 y 4 variables y la regla tiene " + str(cantidad))
        self._tabla = tabla
        self._valores = list(valores)
        self._variables_en_fila = cantidad // 2
        self._variables_en_columna = cantidad - self._variables_en_fila

    @staticmethod
    def puede_generarse(cantidad_variables):
        return MINIMO_VARIABLES <= cantidad_variables <= MAXIMO_VARIABLES

    @property
    def numero_filas(self):
        return 1 << self._variables_en_fila

    @property
    def numero_columnas(self):
        return 1 << self._variables_en_columna

    @property
    def nombres_fila(self):
        return self._unir_nombres(0, self._variables_en_fila)

    @property
    def nombres_columna(self):
        return self._unir_nombres(self._variables_en_fila,
                                  self._variables_en_fila + self._variables_en_columna)

    def encabezado_fila(self, fila):
        return self._etiqueta_gray(fila, self._variables_en_fila)

    def encabezado_columna(self, columna):
        return self._etiqueta_gray(columna, self._variables_en_columna)

    def indice_tabla(self, fila, columna):
        codigo_fila = self._codigo_gray(fila)
        codigo_columna = self._codigo_gray(columna)
        return (codigo_fila << self._variables_en_columna) | codigo_columna

    def valor(self, fila, columna):
        return self._valores[self.indice_tabla(fila, columna)]

    def contar_verdaderos(self):
        return sum(1 for valor in self._valores if valor)

    def _codigo_gray(self, posicion):
        return posicion ^ (posicion >> 1)

    def _etiqueta_gray(self, posicion, bits):
        codigo = self._codigo_gray(posicion)
        texto = ""
        for bit in range(bits - 1, -1, -1):
            verdadero = ((codigo >> bit) & 1) == 0
            texto += "V" if verdadero else "F"
        return texto

    def _unir_nombres(self, desde, hasta):
        return "".join(self._tabla.variables[desde:hasta])
