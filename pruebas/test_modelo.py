import itertools
import random
import unittest

from reglacomprobada.modelo.analizador_expresion import AnalizadorExpresion
from reglacomprobada.modelo.catalogo_escenarios import CatalogoEscenarios
from reglacomprobada.modelo.comparador_equivalencia import ComparadorEquivalencia
from reglacomprobada.modelo.excepciones import ExpresionInvalidaError
from reglacomprobada.modelo.mapa_karnaugh import MapaKarnaugh
from reglacomprobada.modelo.nodo import Nodo
from reglacomprobada.modelo.notacion import Notacion
from reglacomprobada.modelo.simplificador import Simplificador


class PruebasAnalizador(unittest.TestCase):

    def setUp(self):
        self.analizador = AnalizadorExpresion()

    def test_acepta_estilo_python(self):
        regla = self.analizador.analizar("not (a and b) or c")
        self.assertEqual(regla.a_texto(Notacion.PYTHON), "not (a and b) or c")

    def test_acepta_estilo_java_y_simbolos(self):
        uno = self.analizador.analizar("!(a && b) || c")
        dos = self.analizador.analizar("\u00ac(a \u2227 b) \u2228 c")
        tres = self.analizador.analizar("not (a and b) or c")
        self.assertEqual(uno, tres)
        self.assertEqual(dos, tres)

    def test_precedencia_not_and_or(self):
        regla = self.analizador.analizar("a or b and not c")
        self.assertTrue(regla.evaluar({"a": False, "b": True, "c": False}))
        self.assertFalse(regla.evaluar({"a": False, "b": True, "c": True}))
        self.assertTrue(regla.evaluar({"a": True, "b": False, "c": True}))

    def test_error_regla_vacia(self):
        with self.assertRaises(ExpresionInvalidaError):
            self.analizador.analizar("   ")

    def test_error_parentesis_sin_cerrar(self):
        with self.assertRaises(ExpresionInvalidaError):
            self.analizador.analizar("(a and b")

    def test_error_operador_suelto(self):
        with self.assertRaises(ExpresionInvalidaError):
            self.analizador.analizar("a and")

    def test_rechaza_caracter_fuera_del_alfabeto(self):
        with self.assertRaises(ExpresionInvalidaError):
            self.analizador.analizar("a $ b")

    def test_variables_con_varias_letras(self):
        regla = self.analizador.analizar("lluvia and not frio_2")
        self.assertTrue(regla.evaluar({"lluvia": True, "frio_2": False}))
        self.assertFalse(regla.evaluar({"lluvia": True, "frio_2": True}))

    def test_negaciones_repetidas(self):
        regla = self.analizador.analizar("not not not a")
        self.assertTrue(regla.evaluar({"a": False}))


class PruebasComparador(unittest.TestCase):

    def setUp(self):
        self.analizador = AnalizadorExpresion()
        self.comparador = ComparadorEquivalencia()

    def comparar(self, uno, otro):
        return self.comparador.comparar(
            self.analizador.analizar(uno), self.analizador.analizar(otro))

    def test_de_morgan_correcto(self):
        self.assertTrue(self.comparar("not (a and b)", "not a or not b").es_equivalente())
        self.assertTrue(self.comparar("not (a or b)", "not a and not b").es_equivalente())

    def test_error_clasico_de_morgan(self):
        resultado = self.comparar("not (u and k)", "not u and not k")
        self.assertFalse(resultado.es_equivalente())
        self.assertEqual(len(resultado.filas_diferentes), 2)
        self.assertEqual(resultado.total_filas, 4)

    def test_orden_de_filas_de_clase(self):
        resultado = self.comparar("p and q", "p and q")
        self.assertEqual(resultado.copiar_valores_a(), [True, False, False, False])

    def test_demasiadas_variables(self):
        nombres = " and ".join("v" + str(i) for i in range(9))
        with self.assertRaises(ExpresionInvalidaError):
            self.comparar(nombres, nombres)


class PruebasSimplificador(unittest.TestCase):

    def setUp(self):
        self.analizador = AnalizadorExpresion()
        self.simplificador = Simplificador()
        self.comparador = ComparadorEquivalencia()

    def simplificar(self, texto):
        return self.simplificador.simplificar(self.analizador.analizar(texto))

    def test_doble_negacion(self):
        resultado = self.simplificar("not not p")
        self.assertEqual(resultado.simplificada.a_texto(Notacion.PYTHON), "p")

    def test_complemento(self):
        resultado = self.simplificar("p or not p")
        self.assertEqual(resultado.simplificada.a_texto(Notacion.PYTHON), "True")

    def test_absorcion(self):
        resultado = self.simplificar("p or (p and q)")
        self.assertEqual(resultado.simplificada.a_texto(Notacion.PYTHON), "p")

    def test_descuento_de_la_tienda(self):
        resultado = self.simplificar(
            "(r and m and p) or (r and m and c and not p) or not (not r or not m or not c)")
        self.assertEqual(resultado.simplificada.a_texto(Notacion.PYTHON), "r and m and (p or c)")
        self.assertEqual(resultado.operadores_antes, 14)
        self.assertEqual(resultado.operadores_despues, 3)
        self.assertEqual(resultado.porcentaje_ahorro, 78)

    def test_cerradura(self):
        resultado = self.simplificar("(h and f) or (h and not f and c)")
        self.assertEqual(resultado.simplificada.a_texto(Notacion.PYTHON), "h and (f or c)")
        self.assertEqual(resultado.operadores_antes, 5)
        self.assertEqual(resultado.operadores_despues, 2)

    def test_cada_paso_conserva_el_resultado(self):
        resultado = self.simplificar(
            "(r and m and p) or (r and m and c and not p) or not (not r or not m or not c)")
        anterior = resultado.original
        for paso in resultado.pasos:
            self.assertTrue(self.comparador.comparar(anterior, paso.resultado).es_equivalente())
            anterior = paso.resultado

    def test_reglas_aleatorias_conservan_el_resultado(self):
        generador = random.Random(2026)
        for _ in range(300):
            regla = self.generar(generador, 4)
            resultado = self.simplificador.simplificar(regla)
            comparacion = self.comparador.comparar(regla, resultado.simplificada)
            self.assertTrue(comparacion.es_equivalente(), str(regla))

    def generar(self, generador, profundidad):
        if profundidad == 0 or generador.random() < 0.2:
            nombre = generador.choice(["a", "b", "c", "d"])
            return Nodo.variable(nombre)
        opcion = generador.randint(0, 2)
        if opcion == 0:
            return Nodo.negacion(self.generar(generador, profundidad - 1))
        hijos = [self.generar(generador, profundidad - 1) for _ in range(generador.randint(2, 3))]
        if opcion == 1:
            return Nodo.conjuncion(hijos)
        return Nodo.disyuncion(hijos)


class PruebasMapaKarnaugh(unittest.TestCase):

    def setUp(self):
        self.analizador = AnalizadorExpresion()
        self.comparador = ComparadorEquivalencia()

    def crear_mapa(self, texto):
        regla = self.analizador.analizar(texto)
        resultado = self.comparador.comparar(regla, regla)
        return MapaKarnaugh(resultado.tabla, resultado.copiar_valores_a())

    def test_encabezados_en_codigo_gray(self):
        mapa = self.crear_mapa("a and b and c and d")
        encabezados = [mapa.encabezado_columna(i) for i in range(4)]
        self.assertEqual(encabezados, ["VV", "VF", "FF", "FV"])

    def test_cada_celda_apunta_a_una_fila_distinta(self):
        mapa = self.crear_mapa("a and b and c and d")
        indices = set()
        for fila, columna in itertools.product(range(4), range(4)):
            indices.add(mapa.indice_tabla(fila, columna))
        self.assertEqual(len(indices), 16)

    def test_rechaza_una_variable(self):
        regla = self.analizador.analizar("a")
        resultado = self.comparador.comparar(regla, regla)
        with self.assertRaises(ExpresionInvalidaError):
            MapaKarnaugh(resultado.tabla, resultado.copiar_valores_a())


class PruebasCatalogo(unittest.TestCase):

    def test_los_cinco_escenarios_se_comportan_como_se_anuncia(self):
        analizador = AnalizadorExpresion()
        comparador = ComparadorEquivalencia()
        esperados = {
            "Descuento en una app de compras": True,
            "Notificaciones del celular": True,
            "Cerradura inteligente de una oficina": True,
            "Bloqueo de cuenta (el error cl\u00e1sico)": False,
            "Filtro de correo (De Morgan bien aplicado)": True,
        }
        escenarios = CatalogoEscenarios().escenarios
        self.assertEqual(len(escenarios), 5)
        for escenario in escenarios:
            original = analizador.analizar(escenario.regla_original)
            nueva = analizador.analizar(escenario.regla_nueva)
            resultado = comparador.comparar(original, nueva)
            self.assertEqual(resultado.es_equivalente(), esperados[escenario.nombre])


if __name__ == "__main__":
    unittest.main()
