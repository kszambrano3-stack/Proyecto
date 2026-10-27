from reglacomprobada.modelo.analizador_expresion import AnalizadorExpresion
from reglacomprobada.modelo.comparador_equivalencia import ComparadorEquivalencia
from reglacomprobada.modelo.excepciones import ExpresionInvalidaError
from reglacomprobada.modelo.mapa_karnaugh import MapaKarnaugh
from reglacomprobada.modelo.notacion import Notacion
from reglacomprobada.modelo.simplificador import Simplificador

INDICE_PESTANA_LABORATORIO = 2
INDICE_PESTANA_MAPAS = 3


class ControladorPrincipal:

    def __init__(self, vista, catalogo):
        self._vista = vista
        self._catalogo = catalogo
        self._analizador = AnalizadorExpresion()
        self._comparador = ComparadorEquivalencia()
        self._simplificador = Simplificador()
        self._regla_original = None
        self._regla_nueva = None
        self._tabla = None
        self._escenario_actual = None

    def iniciar(self):
        self._vista.conectar_acciones(
            self.elegir_escenario,
            self.investigar,
            self.limpiar,
            self.simplificar,
            self.cambiar_interruptor,
            self.cambiar_pestana)
        nombres = [escenario.nombre for escenario in self._catalogo.escenarios]
        self._vista.poblar_escenarios(nombres)
        self._vista.seleccionar_escenario(0)
        self.elegir_escenario()

    def elegir_escenario(self):
        nombre = self._vista.obtener_escenario_elegido()
        escenario = self._catalogo.buscar_por_nombre(nombre)
        if escenario is None:
            return
        self._escenario_actual = escenario
        historia = escenario.historia + "\n" + "   ".join(escenario.significado_variables)
        self._vista.establecer_historia(historia)
        self._vista.establecer_reglas(escenario.regla_original, escenario.regla_nueva)
        self.investigar()
        self.simplificar()

    def investigar(self):
        resultado = self._analizar_y_comparar()
        if resultado is None:
            return
        tabla = resultado.tabla
        filas = []
        for fila in range(resultado.total_filas):
            valores = []
            for indice in range(len(tabla.variables)):
                valores.append(self._letra(tabla.valor_variable(fila, indice)))
            valores.append(self._letra(resultado.valor_a(fila)))
            valores.append(self._letra(resultado.valor_b(fila)))
            es_diferente = resultado.valor_a(fila) != resultado.valor_b(fila)
            valores.append("DIFERENTE" if es_diferente else "igual")
            filas.append((tuple(valores), es_diferente))
        self._vista.mostrar_tabla(tabla.variables, filas)
        self._mostrar_veredicto(resultado)
        self._tabla = tabla
        self._preparar_laboratorio()
        self._preparar_mapas(resultado)

    def limpiar(self):
        self._vista.limpiar_reglas()
        self._vista.limpiar_tabla()
        self._vista.limpiar_veredicto()
        self._vista.mostrar_pasos([])
        self._vista.mostrar_resumen("", "", "")
        self._vista.mostrar_mensaje_laboratorio("Primero investiga dos reglas en la pesta\u00f1a 1.")
        self._vista.mostrar_mensaje_mapas("Primero investiga dos reglas en la pesta\u00f1a 1.")
        self._regla_original = None
        self._regla_nueva = None
        self._tabla = None

    def simplificar(self):
        texto = self._vista.obtener_regla_simplificar()
        try:
            regla = self._analizador.analizar(texto)
        except ExpresionInvalidaError as error:
            self._vista.mostrar_error(error.mensaje)
            return
        resultado = self._simplificador.simplificar(regla)
        lineas = []
        lineas.append(("Regla de partida:", "titulo"))
        lineas.append(("    " + self._texto(resultado.original), "regla"))
        lineas.append(("", "normal"))
        anterior = resultado.original
        numero = 1
        for paso in resultado.pasos:
            lineas.append(("Paso " + str(numero) + ": " + paso.ley.nombre, "titulo"))
            lineas.append(("    " + paso.ley.explicacion, "normal"))
            lineas.append(("    queda: " + self._texto(paso.resultado), "regla"))
            if self._comparador.comparar(anterior, paso.resultado).es_equivalente():
                lineas.append(("    comprobado: sigue dando lo mismo", "ok"))
            else:
                lineas.append(("    atenci\u00f3n: este paso cambi\u00f3 el resultado", "titulo"))
            lineas.append(("", "normal"))
            anterior = paso.resultado
            numero += 1
        if len(resultado.pasos) == 0:
            lineas.append(("Esta regla ya est\u00e1 en su forma m\u00e1s corta.", "normal"))
            lineas.append(("", "normal"))
        lineas.append(("Resultado final:", "titulo"))
        lineas.append(("    " + self._texto(resultado.simplificada), "final"))
        final_igual = self._comparador.comparar(
            resultado.original, resultado.simplificada).es_equivalente()
        if final_igual:
            lineas.append(("    comprobaci\u00f3n final: la regla original y el resultado "
                           "dan lo mismo en todas las combinaciones", "ok"))
        else:
            lineas.append(("    atenci\u00f3n: el resultado no coincide con la regla original",
                           "titulo"))
        self._vista.mostrar_pasos(lineas)
        self._mostrar_resumen(resultado)

    def cambiar_interruptor(self):
        self._actualizar_focos()

    def cambiar_pestana(self, indice):
        if indice != INDICE_PESTANA_LABORATORIO and indice != INDICE_PESTANA_MAPAS:
            return
        try:
            regla_original = self._analizador.analizar(self._vista.obtener_regla_original())
            regla_nueva = self._analizador.analizar(self._vista.obtener_regla_nueva())
        except ExpresionInvalidaError as error:
            self._vista.mostrar_mensaje_laboratorio(error.mensaje)
            self._vista.mostrar_mensaje_mapas(error.mensaje)
            return
        if (self._regla_original is not None and regla_original == self._regla_original
                and regla_nueva == self._regla_nueva):
            return
        self.investigar()

    def _analizar_y_comparar(self):
        try:
            regla_original = self._analizador.analizar(self._vista.obtener_regla_original())
            regla_nueva = self._analizador.analizar(self._vista.obtener_regla_nueva())
            resultado = self._comparador.comparar(regla_original, regla_nueva)
        except ExpresionInvalidaError as error:
            self._vista.mostrar_error(error.mensaje)
            return None
        self._regla_original = regla_original
        self._regla_nueva = regla_nueva
        return resultado

    def _mostrar_veredicto(self, resultado):
        total = resultado.total_filas
        diferencias = resultado.filas_diferentes
        coincide_escenario = self._coincide_con_escenario()
        if resultado.es_equivalente():
            texto = ("CASO CERRADO. Las dos reglas dan el mismo resultado en las "
                     + str(total) + " combinaciones posibles.")
            if coincide_escenario:
                texto += "\n" + self._escenario_actual.mensaje_si_coinciden
            self._vista.mostrar_veredicto(texto, True)
            return
        primera = diferencias[0]
        texto = ("ENCONTR\u00c9 AL CULPABLE. Las reglas dan distinto en " + str(len(diferencias))
                 + " de " + str(total) + " combinaciones.\n"
                 + "Primera fila culpable: " + self._describir_fila(resultado, primera)
                 + ". La original da " + self._letra(resultado.valor_a(primera))
                 + " y la nueva da " + self._letra(resultado.valor_b(primera)) + ".")
        if coincide_escenario:
            texto += "\n" + self._escenario_actual.consecuencia_si_difieren
        self._vista.mostrar_veredicto(texto, False)

    def _describir_fila(self, resultado, fila):
        tabla = resultado.tabla
        partes = []
        for indice, nombre in enumerate(tabla.variables):
            partes.append(nombre + "=" + self._letra(tabla.valor_variable(fila, indice)))
        return ", ".join(partes)

    def _coincide_con_escenario(self):
        if self._escenario_actual is None:
            return False
        original = self._vista.obtener_regla_original().strip()
        nueva = self._vista.obtener_regla_nueva().strip()
        return (original == self._escenario_actual.regla_original
                and nueva == self._escenario_actual.regla_nueva)

    def _mostrar_resumen(self, resultado):
        antes = "Antes: " + str(resultado.operadores_antes) + " operadores"
        despues = "Despu\u00e9s: " + str(resultado.operadores_despues) + " operadores"
        if len(resultado.pasos) == 0:
            ahorro = "Sin cambios"
        elif resultado.porcentaje_ahorro > 0:
            ahorro = "Ahorro: " + str(resultado.porcentaje_ahorro) + " %"
        else:
            ahorro = "Forma equivalente, sin ahorro"
        self._vista.mostrar_resumen(antes, despues, ahorro)

    def _preparar_laboratorio(self):
        etiquetas = []
        for nombre in self._tabla.variables:
            etiquetas.append(self._etiqueta_variable(nombre))
        self._vista.preparar_laboratorio(etiquetas)
        self._actualizar_focos()

    def _etiqueta_variable(self, nombre):
        if self._escenario_actual is not None:
            for significado in self._escenario_actual.significado_variables:
                if significado.startswith(nombre + " = "):
                    return significado
        return nombre

    def _actualizar_focos(self):
        if self._regla_original is None or self._tabla is None:
            return
        estados = self._vista.obtener_estado_interruptores()
        asignacion = {}
        for indice, nombre in enumerate(self._tabla.variables):
            asignacion[nombre] = estados[indice]
        original = self._regla_original.evaluar(asignacion)
        nueva = self._regla_nueva.evaluar(asignacion)
        if original == nueva:
            mensaje = "Los dos focos coinciden con esta combinaci\u00f3n."
        else:
            mensaje = "\u00a1Los focos NO coinciden! Esta combinaci\u00f3n es una fila culpable."
        self._vista.mostrar_focos(original, nueva, mensaje, original == nueva)

    def _preparar_mapas(self, resultado):
        cantidad = len(resultado.tabla.variables)
        if not MapaKarnaugh.puede_generarse(cantidad):
            self._vista.mostrar_mensaje_mapas(
                "El mapa de Karnaugh solo se dibuja con 2 a 4 variables y estas reglas tienen "
                + str(cantidad) + ".")
            return
        mapa_original = MapaKarnaugh(resultado.tabla, resultado.copiar_valores_a())
        mapa_nuevo = MapaKarnaugh(resultado.tabla, resultado.copiar_valores_b())
        indices = set(resultado.filas_diferentes)
        if len(indices) == 0:
            leyenda = "Los dos mapas son id\u00e9nticos: las reglas son equivalentes."
        else:
            leyenda = ("Las celdas rojas son las combinaciones donde las reglas dan distinto ("
                       + str(len(indices)) + ").")
        self._vista.mostrar_mapas(mapa_original, mapa_nuevo, indices, leyenda)

    def _texto(self, nodo):
        return nodo.a_texto(Notacion.PYTHON)

    def _letra(self, valor):
        return "V" if valor else "F"
