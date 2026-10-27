import tkinter as tk

from reglacomprobada.vista import colores

TAMANO_CELDA = 64
ALTO_ENCABEZADO = 36
ANCHO_ENCABEZADO = 74
ANCHO_PANEL = 360
ALTO_PANEL = 360


class PanelKarnaugh(tk.Canvas):

    def __init__(self, contenedor, titulo):
        super().__init__(contenedor, width=ANCHO_PANEL, height=ALTO_PANEL, bg=colores.BLANCO,
                         highlightthickness=1, highlightbackground=colores.BORDE)
        self._titulo = titulo
        self.limpiar()

    def limpiar(self):
        self.delete("all")
        self.create_text(ANCHO_PANEL // 2, 20, text=self._titulo,
                         font=("TkDefaultFont", 12, "bold"), fill=colores.TEXTO)

    def mostrar(self, mapa, indices_diferentes):
        self.limpiar()
        ancho_total = ANCHO_ENCABEZADO + mapa.numero_columnas * TAMANO_CELDA
        origen_x = (ANCHO_PANEL - ancho_total) // 2
        origen_y = 50
        esquina = mapa.nombres_fila + " \\ " + mapa.nombres_columna
        self.create_rectangle(origen_x, origen_y, origen_x + ANCHO_ENCABEZADO,
                              origen_y + ALTO_ENCABEZADO, fill=colores.ENCABEZADO_MAPA,
                              outline=colores.BORDE)
        self.create_text(origen_x + ANCHO_ENCABEZADO // 2, origen_y + ALTO_ENCABEZADO // 2,
                         text=esquina, font=("TkDefaultFont", 10, "bold"), fill=colores.TEXTO)
        for columna in range(mapa.numero_columnas):
            izquierda = origen_x + ANCHO_ENCABEZADO + columna * TAMANO_CELDA
            self.create_rectangle(izquierda, origen_y, izquierda + TAMANO_CELDA,
                                  origen_y + ALTO_ENCABEZADO, fill=colores.ENCABEZADO_MAPA,
                                  outline=colores.BORDE)
            self.create_text(izquierda + TAMANO_CELDA // 2, origen_y + ALTO_ENCABEZADO // 2,
                             text=mapa.encabezado_columna(columna),
                             font=("TkDefaultFont", 11, "bold"), fill=colores.TEXTO)
        for fila in range(mapa.numero_filas):
            arriba = origen_y + ALTO_ENCABEZADO + fila * TAMANO_CELDA
            self.create_rectangle(origen_x, arriba, origen_x + ANCHO_ENCABEZADO,
                                  arriba + TAMANO_CELDA, fill=colores.ENCABEZADO_MAPA,
                                  outline=colores.BORDE)
            self.create_text(origen_x + ANCHO_ENCABEZADO // 2, arriba + TAMANO_CELDA // 2,
                             text=mapa.encabezado_fila(fila),
                             font=("TkDefaultFont", 11, "bold"), fill=colores.TEXTO)
            for columna in range(mapa.numero_columnas):
                izquierda = origen_x + ANCHO_ENCABEZADO + columna * TAMANO_CELDA
                indice = mapa.indice_tabla(fila, columna)
                verdadero = mapa.valor(fila, columna)
                if indice in indices_diferentes:
                    relleno = colores.CELDA_DIFERENTE
                elif verdadero:
                    relleno = colores.CELDA_VERDADERA
                else:
                    relleno = colores.CELDA_FALSA
                self.create_rectangle(izquierda, arriba, izquierda + TAMANO_CELDA,
                                      arriba + TAMANO_CELDA, fill=relleno, outline=colores.BORDE)
                self.create_text(izquierda + TAMANO_CELDA // 2, arriba + TAMANO_CELDA // 2,
                                 text="V" if verdadero else "F",
                                 font=("TkDefaultFont", 16, "bold"), fill=colores.TEXTO)
