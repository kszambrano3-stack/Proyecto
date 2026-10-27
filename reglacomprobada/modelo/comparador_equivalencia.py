from reglacomprobada.modelo.resultado_comparacion import ResultadoComparacion
from reglacomprobada.modelo.tabla_verdad import TablaVerdad


class ComparadorEquivalencia:

    def comparar(self, regla_a, regla_b):
        nombres = set()
        regla_a.recolectar_variables(nombres)
        regla_b.recolectar_variables(nombres)
        tabla = TablaVerdad(nombres)
        valores_a = []
        valores_b = []
        for fila in range(tabla.numero_filas):
            asignacion = tabla.crear_asignacion(fila)
            valores_a.append(regla_a.evaluar(asignacion))
            valores_b.append(regla_b.evaluar(asignacion))
        return ResultadoComparacion(tabla, regla_a, regla_b, valores_a, valores_b)
